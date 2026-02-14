#!/usr/bin/env python3
"""PostToolUse hook: auto-stamp telemetry timestamps in bean/task files.

Fires after Edit/Write on files matching:
  ai/beans/BEAN-*/bean.md
  ai/beans/BEAN-*/tasks/*.md

Stamps Started/Completed timestamps and computes Duration when status
transitions are detected. Only overwrites fields whose value is the
sentinel em-dash (—).

When a bean is marked Done, duration is computed from git timestamps
(first commit on the feature branch → now) for second-level precision.
Falls back to Started/Completed metadata if git is unavailable.

Reads hook input JSON from stdin, writes JSON message to stdout when
a file is modified.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SENTINEL = "—"
TIMESTAMP_FMT = "%Y-%m-%d %H:%M"

# Patterns to match bean and task files (relative paths from repo root)
BEAN_RE = re.compile(r"ai/beans/BEAN-\d+-[^/]+/bean\.md$")
TASK_RE = re.compile(r"ai/beans/BEAN-\d+-[^/]+/tasks/.*\.md$")


def now_stamp() -> str:
    """Return current timestamp in YYYY-MM-DD HH:MM format."""
    return datetime.now().strftime(TIMESTAMP_FMT)


def parse_metadata_field(content: str, field: str) -> str | None:
    """Extract value of a bold field from a markdown metadata table.

    Looks for rows like: | **Field** | Value |
    Returns the stripped value, or None if not found.
    """
    pattern = re.compile(
        r"^\|\s*\*\*" + re.escape(field) + r"\*\*\s*\|\s*(.*?)\s*\|",
        re.MULTILINE,
    )
    m = pattern.search(content)
    if m:
        return m.group(1).strip()
    return None


def replace_metadata_field(content: str, field: str, value: str) -> str:
    """Replace value of a bold field in a markdown metadata table.

    Replaces: | **Field** | old_value |
    With:     | **Field** | new_value |
    """
    pattern = re.compile(
        r"(^\|\s*\*\*" + re.escape(field) + r"\*\*\s*\|\s*)(.*?)(\s*\|)",
        re.MULTILINE,
    )
    return pattern.sub(rf"\g<1>{value}\3", content, count=1)


def format_seconds(seconds: float) -> str:
    """Format a duration in seconds to human-readable string.

    Returns '< 1m' for <60s, 'Xm' for <1h, 'Xh Ym' for >=1h.
    """
    total_minutes = max(0, int(seconds // 60))
    if total_minutes == 0:
        return "< 1m"
    if total_minutes < 60:
        return f"{total_minutes}m"
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if minutes == 0:
        return f"{hours}h"
    return f"{hours}h {minutes}m"


def format_duration(started: str, completed: str) -> str:
    """Compute human-readable duration between two timestamps.

    Returns 'Xm' for <1h, 'Xh Ym' for >=1h. Returns '< 1m' on parse error.
    """
    try:
        dt_start = datetime.strptime(started.strip(), TIMESTAMP_FMT)
        dt_end = datetime.strptime(completed.strip(), TIMESTAMP_FMT)
        delta = dt_end - dt_start
        return format_seconds(max(0, delta.total_seconds()))
    except (ValueError, TypeError):
        return "< 1m"


def git_branch_duration() -> str | None:
    """Compute duration from the first commit on the current feature branch.

    Uses git to find the first commit on the current branch that isn't on
    'test' or 'main', and computes elapsed time from that commit to now.
    Returns a formatted duration string, or None if git data is unavailable.
    """
    try:
        # Get current branch name
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()

        if not branch or branch in ("main", "test"):
            return None

        # Find the merge base with test (or main as fallback)
        for base in ("test", "main"):
            result = subprocess.run(
                ["git", "merge-base", base, "HEAD"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                merge_base = result.stdout.strip()
                break
        else:
            return None

        # Get timestamp of first commit after merge base
        result = subprocess.run(
            ["git", "log", "--format=%aI", "--reverse", f"{merge_base}..HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None

        first_commit_ts = result.stdout.strip().split("\n")[0]
        dt_start = datetime.fromisoformat(first_commit_ts)
        dt_now = datetime.now(timezone.utc)
        # Ensure both are offset-aware for comparison
        if dt_start.tzinfo is None:
            dt_start = dt_start.replace(tzinfo=timezone.utc)
        delta = (dt_now - dt_start).total_seconds()
        return format_seconds(max(0, delta))

    except Exception:
        return None


def parse_duration_to_seconds(dur: str) -> int | None:
    """Parse a duration string like '< 1m', '5m', '1h 30m' to seconds."""
    dur = dur.strip()
    if dur == "< 1m":
        return 30  # approximate
    m = re.match(r"^(?:(\d+)h)?\s*(?:(\d+)m)?$", dur)
    if m and (m.group(1) or m.group(2)):
        hours = int(m.group(1) or 0)
        minutes = int(m.group(2) or 0)
        return hours * 3600 + minutes * 60
    return None


def parse_tasks_table(content: str) -> list[tuple[str, str, str]]:
    """Parse the Tasks table in a bean.md.

    Returns list of (num, task_name, owner) for rows with non-empty task names.
    """
    rows: list[tuple[str, str, str]] = []
    in_tasks = False
    separator_seen = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Tasks"):
            in_tasks = True
            continue
        if in_tasks and stripped.startswith("##"):
            break
        if not in_tasks:
            continue
        if not stripped.startswith("|"):
            if separator_seen and stripped and not stripped.startswith(">"):
                break
            continue
        if re.match(r"^\|[\s\-|]+\|$", stripped):
            separator_seen = True
            continue
        if not separator_seen:
            continue
        cells = [c.strip() for c in stripped.split("|")]
        cells = [c for c in cells if c]
        if len(cells) >= 3 and cells[1]:
            rows.append((cells[0], cells[1], cells[2]))
    return rows


def find_telemetry_table(content: str) -> tuple[int, int, list[str]]:
    """Find the per-task Telemetry table in a bean.md.

    Returns (first_data_line_idx, last_data_line_idx+1, data_row_lines).
    Returns (-1, -1, []) if not found.
    """
    lines = content.splitlines()
    in_telemetry = False
    separator_idx = -1
    data_rows: list[tuple[int, str]] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## Telemetry"):
            in_telemetry = True
            continue
        if in_telemetry and stripped.startswith("##"):
            break
        if not in_telemetry:
            continue
        # Identify the per-task header (has "Duration" — the summary table has "Metric")
        if stripped.startswith("|") and "Duration" in stripped and "Task" in stripped:
            continue
        if separator_idx < 0 and re.match(r"^\|[\s\-|]+\|$", stripped):
            separator_idx = i
            continue
        if separator_idx >= 0 and stripped.startswith("|"):
            # Stop at the summary table (has "Metric" or bold fields)
            if "**" in stripped or "Metric" in stripped:
                break
            data_rows.append((i, stripped))
        elif separator_idx >= 0 and not stripped.startswith("|"):
            if stripped:
                break

    if separator_idx < 0:
        return -1, -1, []

    if not data_rows:
        return separator_idx + 1, separator_idx + 1, []

    return data_rows[0][0], data_rows[-1][0] + 1, [row for _, row in data_rows]


def telemetry_row_nums(rows: list[str]) -> set[str]:
    """Extract task numbers from telemetry table rows."""
    nums: set[str] = set()
    for row in rows:
        cells = [c.strip() for c in row.split("|")]
        cells = [c for c in cells if c]
        if cells and cells[0] and cells[0] not in ("", SENTINEL):
            nums.add(cells[0])
    return nums


def is_empty_template_row(row: str) -> bool:
    """Check if a telemetry row is the empty template row."""
    cells = [c.strip() for c in row.split("|")]
    cells = [c for c in cells if c]
    return all(not c or c == SENTINEL for c in cells[1:])


def sync_telemetry_table(content: str) -> tuple[str, list[str]]:
    """Sync the Telemetry per-task table with the Tasks table.

    Adds rows for tasks not yet in the Telemetry table.
    Returns (new_content, actions_taken).
    """
    tasks = parse_tasks_table(content)
    if not tasks:
        return content, []

    lines = content.splitlines()
    first_data, end_data, existing_rows = find_telemetry_table(content)
    if first_data < 0:
        return content, []

    # If only an empty template row exists, treat it as no existing data
    has_only_template = (
        len(existing_rows) == 1 and is_empty_template_row(existing_rows[0])
    )
    existing_nums = set() if has_only_template else telemetry_row_nums(existing_rows)

    new_rows: list[str] = []
    actions: list[str] = []
    for num, name, owner in tasks:
        if num not in existing_nums:
            new_rows.append(f"| {num} | {name} | {owner} | {SENTINEL} | {SENTINEL} | {SENTINEL} |")
            actions.append(f"Telem row {num}")

    if not new_rows:
        return content, []

    if has_only_template:
        # Replace the empty template row with real data
        lines[first_data:end_data] = new_rows
    else:
        # Append after existing rows
        for idx, row in enumerate(new_rows):
            lines.insert(end_data + idx, row)

    return "\n".join(lines), actions


def update_telemetry_row_duration(
    content: str, task_num: str, duration: str,
) -> tuple[str, bool]:
    """Update the Duration column of a specific telemetry row.

    Returns (new_content, changed).
    """
    lines = content.splitlines()
    in_telemetry = False
    separator_seen = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## Telemetry"):
            in_telemetry = True
            continue
        if in_telemetry and stripped.startswith("##"):
            break
        if not in_telemetry:
            continue
        if re.match(r"^\|[\s\-|]+\|$", stripped):
            separator_seen = True
            continue
        if not separator_seen or not stripped.startswith("|"):
            continue
        if "**" in stripped or "Metric" in stripped:
            break

        cells = [c.strip() for c in stripped.split("|")]
        cells = [c for c in cells if c]
        if cells and cells[0] == task_num and len(cells) >= 4:
            if cells[3] == SENTINEL:
                cells[3] = duration
                lines[i] = "| " + " | ".join(cells) + " |"
                return "\n".join(lines), True

    return content, False


def sum_telemetry_durations(content: str) -> str | None:
    """Sum per-task durations from the Telemetry table."""
    _, _, rows = find_telemetry_table(content)
    total_seconds = 0
    found_any = False

    for row in rows:
        cells = [c.strip() for c in row.split("|")]
        cells = [c for c in cells if c]
        if len(cells) >= 4:
            dur = cells[3]
            if dur and dur != SENTINEL:
                secs = parse_duration_to_seconds(dur)
                if secs is not None:
                    total_seconds += secs
                    found_any = True

    if not found_any:
        return None
    return format_seconds(total_seconds)


def extract_task_number(filename: str) -> str | None:
    """Extract task number from a task filename like '01-developer-slug.md'."""
    m = re.match(r"^(\d+)-", filename)
    if m:
        return str(int(m.group(1)))
    return None


def count_done_tasks(content: str) -> int:
    """Count rows with 'Done' status in the Tasks table of a bean.md.

    Looks for the table under ## Tasks with columns: # | Task | Owner | Depends On | Status
    Counts rows where the Status column is 'Done'.
    """
    count = 0
    in_tasks = False
    header_seen = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Tasks"):
            in_tasks = True
            continue
        if in_tasks and stripped.startswith("##"):
            break
        if not in_tasks:
            continue
        if not stripped.startswith("|"):
            if header_seen and stripped and not stripped.startswith(">"):
                break
            continue
        # Skip separator rows
        if re.match(r"^\|[\s\-|]+\|$", stripped):
            header_seen = True
            continue
        # Skip header row (contains "Task" or "#")
        if not header_seen:
            header_seen = False
            continue

        cells = [c.strip() for c in stripped.split("|")]
        # cells[0] is empty (before first |), last is empty (after last |)
        cells = [c for c in cells if c]
        if len(cells) >= 5 and cells[-1].lower() == "done":
            count += 1

    return count


def count_total_tasks(content: str) -> int:
    """Count total task rows in the Tasks table of a bean.md."""
    count = 0
    in_tasks = False
    separator_seen = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Tasks"):
            in_tasks = True
            continue
        if in_tasks and stripped.startswith("##"):
            break
        if not in_tasks:
            continue
        if not stripped.startswith("|"):
            if separator_seen and stripped and not stripped.startswith(">"):
                break
            continue
        if re.match(r"^\|[\s\-|]+\|$", stripped):
            separator_seen = True
            continue
        if not separator_seen:
            continue
        cells = [c.strip() for c in stripped.split("|")]
        cells = [c for c in cells if c]
        if len(cells) >= 2:
            count += 1

    return count


def handle_bean_file(path: Path, now: str) -> list[str]:
    """Process a bean.md file for telemetry stamping.

    Returns list of actions taken (empty if no changes).
    """
    content = path.read_text(encoding="utf-8")
    original = content
    actions = []

    status = parse_metadata_field(content, "Status")
    started = parse_metadata_field(content, "Started")
    completed = parse_metadata_field(content, "Completed")

    # Status = "In Progress" + Started = sentinel → stamp Started
    if status and status.lower() == "in progress" and started == SENTINEL:
        content = replace_metadata_field(content, "Started", now)
        actions.append("Started")

    # Status = "Done" + Completed = sentinel → stamp Completed + Duration
    if status and status.lower() == "done" and completed == SENTINEL:
        # If Started is also sentinel, stamp it too
        cur_started = parse_metadata_field(content, "Started")
        if cur_started == SENTINEL:
            content = replace_metadata_field(content, "Started", now)
            cur_started = now
            actions.append("Started")

        content = replace_metadata_field(content, "Completed", now)
        actions.append("Completed")

        cur_duration = parse_metadata_field(content, "Duration")
        if cur_duration == SENTINEL:
            # Prefer git-based duration (second-level precision) over
            # Started→Completed metadata (minute-level, often 0m for fast beans)
            duration = git_branch_duration() or format_duration(cur_started, now)
            content = replace_metadata_field(content, "Duration", duration)
            actions.append(f"Duration={duration}")

    # Status = "Done" → fill Total Tasks in Telemetry summary
    if status and status.lower() == "done":
        total_tasks_val = parse_metadata_field(content, "Total Tasks")
        if total_tasks_val == SENTINEL:
            total = count_total_tasks(content)
            content = replace_metadata_field(
                content, "Total Tasks", str(total)
            )
            actions.append(f"Total Tasks={total}")

        total_dur_val = parse_metadata_field(content, "Total Duration")
        if total_dur_val == SENTINEL:
            # Prefer sum of per-task durations; fall back to git; then
            # Started/Completed
            total_dur = sum_telemetry_durations(content)
            if not total_dur:
                total_dur = git_branch_duration()
            if not total_dur:
                final_started = parse_metadata_field(content, "Started")
                final_completed = parse_metadata_field(content, "Completed")
                if (
                    final_started and final_started != SENTINEL
                    and final_completed and final_completed != SENTINEL
                ):
                    total_dur = format_duration(final_started, final_completed)
            if total_dur:
                content = replace_metadata_field(
                    content, "Total Duration", total_dur
                )
                actions.append(f"Total Duration={total_dur}")

    # Sync telemetry table with tasks table (add missing rows)
    content, sync_actions = sync_telemetry_table(content)
    actions.extend(sync_actions)

    if content != original:
        path.write_text(content, encoding="utf-8")

    return actions


def handle_task_file(path: Path, now: str) -> list[str]:
    """Process a task .md file for telemetry stamping.

    Returns list of actions taken (empty if no changes).
    """
    content = path.read_text(encoding="utf-8")
    original = content
    actions = []

    status = parse_metadata_field(content, "Status")
    started = parse_metadata_field(content, "Started")
    completed = parse_metadata_field(content, "Completed")

    # Status = "In Progress" + Started = sentinel → stamp Started
    if status and status.lower() == "in progress" and started == SENTINEL:
        content = replace_metadata_field(content, "Started", now)
        actions.append("Started")

    # Status = "Done" + Completed = sentinel → stamp Completed + Duration
    if status and status.lower() == "done" and completed == SENTINEL:
        cur_started = parse_metadata_field(content, "Started")
        if cur_started == SENTINEL:
            content = replace_metadata_field(content, "Started", now)
            cur_started = now
            actions.append("Started")

        content = replace_metadata_field(content, "Completed", now)
        actions.append("Completed")

        cur_duration = parse_metadata_field(content, "Duration")
        if cur_duration == SENTINEL:
            duration = format_duration(cur_started, now)
            content = replace_metadata_field(content, "Duration", duration)
            actions.append(f"Duration={duration}")

        # Propagate per-task duration to bean.md telemetry table
        task_num = extract_task_number(path.name)
        if task_num:
            final_dur = parse_metadata_field(content, "Duration")
            if final_dur and final_dur != SENTINEL:
                bean_path = path.parent.parent / "bean.md"
                if bean_path.exists():
                    try:
                        bean_content = bean_path.read_text(encoding="utf-8")
                        bean_content, changed = update_telemetry_row_duration(
                            bean_content, task_num, final_dur,
                        )
                        if changed:
                            bean_path.write_text(bean_content, encoding="utf-8")
                            actions.append(f"Bean telem row {task_num}")
                    except Exception:
                        pass  # Best-effort; don't fail the task stamp

    if content != original:
        path.write_text(content, encoding="utf-8")

    return actions


def main() -> None:
    """Entry point: read hook JSON from stdin, process file, output result."""
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)

        tool_input = data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        if not file_path:
            return

        # Normalize to relative path for pattern matching
        path = Path(file_path)
        try:
            rel = str(path.relative_to(Path.cwd()))
        except ValueError:
            rel = str(path)

        now = now_stamp()
        actions: list[str] = []

        if BEAN_RE.search(rel):
            actions = handle_bean_file(path, now)
        elif TASK_RE.search(rel):
            actions = handle_task_file(path, now)

        if actions:
            stamped = ", ".join(actions)
            msg = (
                f"Telemetry: stamped {stamped} in {path.name} "
                f"(file auto-modified, re-read before next edit)"
            )
            print(json.dumps({"message": msg}))

    except Exception as e:
        print(f"telemetry-stamp: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
