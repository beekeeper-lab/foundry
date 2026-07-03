#!/usr/bin/env python3
"""
validate-task-inputs — PreToolUse hook that enforces non-empty Inputs:
on task files when their Status transitions to In Progress.

Why this exists: every persona file carries a "Context Diet" rule that
says "read only what the task's Inputs: lists." The rule is voluntary
when no machinery enforces it, and many task files omit Inputs entirely.
This hook makes the discipline structural: a task cannot be claimed
(`Status: In Progress`) until its Inputs section is populated.

Escape hatch: a task with `Inputs: NONE (justified: <reason>)` (where
the reason has at least 10 non-whitespace characters) is allowed
through. Use sparingly — frequent use signals the validator is too
strict, not that the escape is too lenient.

Exit codes:
- 0  pass / not applicable
- 2  block the dispatch (with a remediation message on stderr)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TASK_PATH_RE = re.compile(r"ai/beans/BEAN-\d+[\w\-]*/tasks/\d+-[\w\-]+\.md$")
STATUS_IN_PROGRESS_RE = re.compile(
    r"\|\s*\*\*Status\*\*\s*\|\s*In Progress\s*\|", re.IGNORECASE
)
INPUTS_HEADING_RE = re.compile(r"^##\s+Inputs\s*$", re.MULTILINE)
NEXT_HEADING_RE = re.compile(r"^##\s+", re.MULTILINE)
ESCAPE_HATCH_RE = re.compile(
    r"^\s*Inputs:\s*NONE\s*\(\s*justified:\s*(.+?)\s*\)\s*$",
    re.MULTILINE,
)
SENTINEL_DASHES = {"—", "-", "--", "—-"}


def is_task_file(file_path: str) -> bool:
    """Return True if the path looks like a task file we care about."""
    return bool(TASK_PATH_RE.search(file_path or ""))


def is_in_progress_transition(new_string: str) -> bool:
    """True when the post-edit string flips Status to In Progress."""
    return bool(STATUS_IN_PROGRESS_RE.search(new_string or ""))


def extract_inputs_section(text: str) -> str | None:
    """Return the body of the `## Inputs` section, or None if absent."""
    heading_match = INPUTS_HEADING_RE.search(text)
    if not heading_match:
        return None
    start = heading_match.end()
    next_match = NEXT_HEADING_RE.search(text, start)
    end = next_match.start() if next_match else len(text)
    return text[start:end]


def parse_inputs_bullets(section: str) -> list[str]:
    """Return non-empty bullet items from the Inputs section."""
    items: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ", "+ ")):
            content = stripped[2:].strip()
            if content:
                items.append(content)
    return items


def has_valid_escape_hatch(text: str) -> bool:
    """True iff `Inputs: NONE (justified: <reason>)` with a real reason."""
    match = ESCAPE_HATCH_RE.search(text)
    if not match:
        return False
    reason = match.group(1)
    return len(re.sub(r"\s+", "", reason)) >= 10


def all_bullets_are_sentinel(bullets: list[str]) -> bool:
    """True if every bullet is just an em-dash or hyphen sentinel."""
    if not bullets:
        return True
    return all(b.strip() in SENTINEL_DASHES for b in bullets)


def validate_task_inputs(text: str) -> tuple[bool, str]:
    """Return (ok, message). When ok is False, message is the remediation."""
    if has_valid_escape_hatch(text):
        return True, ""

    section = extract_inputs_section(text)
    if section is None:
        return (
            False,
            "missing `## Inputs` section. Add an Inputs section listing the "
            "specific files, anchors, or paths the task should read.",
        )

    bullets = parse_inputs_bullets(section)
    if not bullets:
        return (
            False,
            "`## Inputs` section is empty. List the specific files, "
            "anchors, or paths the task should read as bullet items.",
        )

    if all_bullets_are_sentinel(bullets):
        return (
            False,
            "`## Inputs` contains only sentinel placeholders (`—`). Replace "
            "them with the actual files / anchors the task should read.",
        )

    return True, ""


def remediation_block(file_path: str, detail: str) -> str:
    """Compose the user-facing failure message."""
    return (
        f"BLOCKED: cannot move {file_path} to `In Progress` — {detail}\n"
        "\n"
        "Expected format:\n"
        "  ## Inputs\n"
        "  - path/to/file.md — specific anchor or section\n"
        "  - other/file.py — function or class name\n"
        "\n"
        "Escape hatch (rare, for genuinely input-less tasks):\n"
        "  Inputs: NONE (justified: <reason of at least 10 characters>)\n"
    )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""

    if not is_task_file(file_path):
        sys.exit(0)

    if tool_name == "Edit":
        new_string = tool_input.get("new_string") or ""
        if not is_in_progress_transition(new_string):
            sys.exit(0)
    else:
        content = tool_input.get("content") or ""
        if not is_in_progress_transition(content):
            sys.exit(0)

    path = Path(file_path)
    if not path.exists():
        sys.exit(0)

    text = path.read_text(encoding="utf-8")
    ok, detail = validate_task_inputs(text)
    if ok:
        sys.exit(0)

    print(remediation_block(file_path, detail), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
