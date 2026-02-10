"""Tests for .claude/hooks/telemetry-stamp.py PostToolUse hook."""

from __future__ import annotations

import importlib
import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the hook module (filename has a hyphen)
_hook_path = str(Path(__file__).resolve().parent.parent / ".claude" / "hooks")
if _hook_path not in sys.path:
    sys.path.insert(0, _hook_path)
_mod = importlib.import_module("telemetry-stamp")

parse_metadata_field = _mod.parse_metadata_field
replace_metadata_field = _mod.replace_metadata_field
format_duration = _mod.format_duration
count_done_tasks = _mod.count_done_tasks
count_total_tasks = _mod.count_total_tasks
handle_bean_file = _mod.handle_bean_file
handle_task_file = _mod.handle_task_file
main = _mod.main
SENTINEL = _mod.SENTINEL


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BEAN_TEMPLATE = """\
# BEAN-099: Test Bean

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-099 |
| **Status** | {status} |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | {started} |
| **Completed** | {completed} |
| **Duration** | {duration} |
| **Owner** | team-lead |
| **Category** | App |

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | First task | dev | — | {task1_status} |
| 2 | Second task | dev | 1 | {task2_status} |

> Tasks are populated by the Team Lead.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | First task | dev | — | — | — |
| 2 | Second task | dev | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | {total_tasks} |
| **Total Duration** | {total_duration} |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
"""

TASK_TEMPLATE = """\
# Task 01: Test Task

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | {status} |
| **Started** | {started} |
| **Completed** | {completed} |
| **Duration** | {duration} |
| **Tokens** | — |

## Goal

Test task goal.
"""


def make_bean(
    status="Unapproved",
    started=SENTINEL,
    completed=SENTINEL,
    duration=SENTINEL,
    task1_status="Pending",
    task2_status="Pending",
    total_tasks=SENTINEL,
    total_duration=SENTINEL,
):
    return BEAN_TEMPLATE.format(
        status=status,
        started=started,
        completed=completed,
        duration=duration,
        task1_status=task1_status,
        task2_status=task2_status,
        total_tasks=total_tasks,
        total_duration=total_duration,
    )


def make_task(
    status="Pending",
    started=SENTINEL,
    completed=SENTINEL,
    duration=SENTINEL,
):
    return TASK_TEMPLATE.format(
        status=status,
        started=started,
        completed=completed,
        duration=duration,
    )


# ---------------------------------------------------------------------------
# TestParseMetadataField
# ---------------------------------------------------------------------------


class TestParseMetadataField:
    def test_extracts_status(self):
        content = make_bean(status="In Progress")
        assert parse_metadata_field(content, "Status") == "In Progress"

    def test_extracts_started_sentinel(self):
        content = make_bean()
        assert parse_metadata_field(content, "Started") == SENTINEL

    def test_extracts_started_timestamp(self):
        content = make_bean(started="2026-02-09 10:30")
        assert parse_metadata_field(content, "Started") == "2026-02-09 10:30"

    def test_returns_none_for_missing_field(self):
        content = make_bean()
        assert parse_metadata_field(content, "NonExistent") is None

    def test_extracts_total_tasks(self):
        content = make_bean(total_tasks="5")
        assert parse_metadata_field(content, "Total Tasks") == "5"

    def test_handles_extra_whitespace(self):
        content = "|  **Status**  |  Done  |"
        assert parse_metadata_field(content, "Status") == "Done"


# ---------------------------------------------------------------------------
# TestReplaceMetadataField
# ---------------------------------------------------------------------------


class TestReplaceMetadataField:
    def test_replaces_sentinel(self):
        content = make_bean(started=SENTINEL)
        result = replace_metadata_field(content, "Started", "2026-02-09 14:00")
        assert parse_metadata_field(result, "Started") == "2026-02-09 14:00"

    def test_preserves_other_fields(self):
        content = make_bean(status="Done", started=SENTINEL)
        result = replace_metadata_field(content, "Started", "2026-02-09 14:00")
        assert parse_metadata_field(result, "Status") == "Done"
        assert parse_metadata_field(result, "Bean ID") == "BEAN-099"
        assert parse_metadata_field(result, "Priority") == "Medium"

    def test_replaces_only_first_occurrence(self):
        # Total Tasks and Total Duration both have "Total" but are distinct fields
        content = make_bean(total_tasks=SENTINEL, total_duration=SENTINEL)
        result = replace_metadata_field(content, "Total Tasks", "3")
        assert parse_metadata_field(result, "Total Tasks") == "3"
        assert parse_metadata_field(result, "Total Duration") == SENTINEL


# ---------------------------------------------------------------------------
# TestFormatDuration
# ---------------------------------------------------------------------------


class TestFormatDuration:
    def test_zero_duration(self):
        assert format_duration("2026-02-09 10:00", "2026-02-09 10:00") == "0m"

    def test_minutes_only(self):
        assert format_duration("2026-02-09 10:00", "2026-02-09 10:23") == "23m"

    def test_exactly_one_hour(self):
        assert format_duration("2026-02-09 10:00", "2026-02-09 11:00") == "1h 0m"

    def test_hours_and_minutes(self):
        assert format_duration("2026-02-09 10:00", "2026-02-09 11:15") == "1h 15m"

    def test_multi_hour(self):
        assert format_duration("2026-02-09 10:00", "2026-02-09 13:45") == "3h 45m"

    def test_unparseable_returns_zero(self):
        assert format_duration("garbage", "2026-02-09 10:00") == "0m"

    def test_reversed_returns_zero(self):
        # Negative duration clamps to 0
        assert format_duration("2026-02-09 11:00", "2026-02-09 10:00") == "0m"


# ---------------------------------------------------------------------------
# TestCountDoneTasks
# ---------------------------------------------------------------------------


class TestCountDoneTasks:
    def test_no_done_tasks(self):
        content = make_bean(task1_status="Pending", task2_status="Pending")
        assert count_done_tasks(content) == 0

    def test_one_done_task(self):
        content = make_bean(task1_status="Done", task2_status="Pending")
        assert count_done_tasks(content) == 1

    def test_all_done_tasks(self):
        content = make_bean(task1_status="Done", task2_status="Done")
        assert count_done_tasks(content) == 2

    def test_count_total_tasks(self):
        content = make_bean(task1_status="Done", task2_status="Pending")
        assert count_total_tasks(content) == 2


# ---------------------------------------------------------------------------
# TestHandleBeanFile
# ---------------------------------------------------------------------------


class TestHandleBeanFile:
    def test_in_progress_stamps_started(self, tmp_path):
        p = tmp_path / "bean.md"
        p.write_text(make_bean(status="In Progress"))
        now = "2026-02-09 14:00"
        actions = handle_bean_file(p, now)
        assert "Started" in actions
        content = p.read_text()
        assert parse_metadata_field(content, "Started") == now

    def test_in_progress_no_double_stamp(self, tmp_path):
        p = tmp_path / "bean.md"
        p.write_text(make_bean(status="In Progress", started="2026-02-09 13:00"))
        actions = handle_bean_file(p, "2026-02-09 14:00")
        assert actions == []

    def test_done_stamps_completed_and_duration(self, tmp_path):
        p = tmp_path / "bean.md"
        p.write_text(make_bean(
            status="Done",
            started="2026-02-09 13:00",
            task1_status="Done",
            task2_status="Done",
        ))
        now = "2026-02-09 13:23"
        actions = handle_bean_file(p, now)
        assert "Completed" in actions
        content = p.read_text()
        assert parse_metadata_field(content, "Completed") == now
        assert parse_metadata_field(content, "Duration") == "23m"

    def test_done_stamps_started_if_missing(self, tmp_path):
        p = tmp_path / "bean.md"
        p.write_text(make_bean(status="Done", task1_status="Done", task2_status="Done"))
        now = "2026-02-09 14:00"
        actions = handle_bean_file(p, now)
        assert "Started" in actions
        assert "Completed" in actions
        content = p.read_text()
        assert parse_metadata_field(content, "Started") == now
        assert parse_metadata_field(content, "Duration") == "0m"

    def test_done_fills_total_tasks(self, tmp_path):
        p = tmp_path / "bean.md"
        p.write_text(make_bean(
            status="Done",
            started="2026-02-09 13:00",
            completed="2026-02-09 13:30",
            duration="30m",
            task1_status="Done",
            task2_status="Done",
        ))
        now = "2026-02-09 13:30"
        actions = handle_bean_file(p, now)
        content = p.read_text()
        assert parse_metadata_field(content, "Total Tasks") == "2"

    def test_done_fills_total_duration(self, tmp_path):
        p = tmp_path / "bean.md"
        p.write_text(make_bean(
            status="Done",
            started="2026-02-09 13:00",
            completed="2026-02-09 14:15",
            duration="1h 15m",
            task1_status="Done",
            task2_status="Done",
        ))
        now = "2026-02-09 14:15"
        actions = handle_bean_file(p, now)
        content = p.read_text()
        assert parse_metadata_field(content, "Total Duration") == "1h 15m"

    def test_noop_on_unapproved(self, tmp_path):
        p = tmp_path / "bean.md"
        p.write_text(make_bean(status="Unapproved"))
        actions = handle_bean_file(p, "2026-02-09 14:00")
        assert actions == []

    def test_noop_when_already_stamped(self, tmp_path):
        p = tmp_path / "bean.md"
        p.write_text(make_bean(
            status="Done",
            started="2026-02-09 13:00",
            completed="2026-02-09 13:30",
            duration="30m",
            task1_status="Done",
            task2_status="Done",
            total_tasks="2",
            total_duration="30m",
        ))
        original = p.read_text()
        actions = handle_bean_file(p, "2026-02-09 14:00")
        assert actions == []
        assert p.read_text() == original


# ---------------------------------------------------------------------------
# TestHandleTaskFile
# ---------------------------------------------------------------------------


class TestHandleTaskFile:
    def test_in_progress_stamps_started(self, tmp_path):
        p = tmp_path / "task.md"
        p.write_text(make_task(status="In Progress"))
        now = "2026-02-09 14:00"
        actions = handle_task_file(p, now)
        assert "Started" in actions
        content = p.read_text()
        assert parse_metadata_field(content, "Started") == now

    def test_done_stamps_completed(self, tmp_path):
        p = tmp_path / "task.md"
        p.write_text(make_task(status="Done", started="2026-02-09 13:00"))
        now = "2026-02-09 13:45"
        actions = handle_task_file(p, now)
        assert "Completed" in actions
        content = p.read_text()
        assert parse_metadata_field(content, "Completed") == now
        assert parse_metadata_field(content, "Duration") == "45m"

    def test_done_stamps_started_if_missing(self, tmp_path):
        p = tmp_path / "task.md"
        p.write_text(make_task(status="Done"))
        now = "2026-02-09 14:00"
        actions = handle_task_file(p, now)
        assert "Started" in actions
        assert "Completed" in actions
        content = p.read_text()
        assert parse_metadata_field(content, "Duration") == "0m"

    def test_noop_on_pending(self, tmp_path):
        p = tmp_path / "task.md"
        p.write_text(make_task(status="Pending"))
        actions = handle_task_file(p, "2026-02-09 14:00")
        assert actions == []

    def test_noop_when_already_stamped(self, tmp_path):
        p = tmp_path / "task.md"
        p.write_text(make_task(
            status="Done",
            started="2026-02-09 13:00",
            completed="2026-02-09 13:30",
            duration="30m",
        ))
        original = p.read_text()
        actions = handle_task_file(p, "2026-02-09 14:00")
        assert actions == []
        assert p.read_text() == original


# ---------------------------------------------------------------------------
# TestMainIntegration
# ---------------------------------------------------------------------------


class TestMainIntegration:
    def _make_stdin_json(self, file_path: str) -> str:
        return json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": file_path},
        })

    def test_bean_edit_produces_stdout(self, tmp_path):
        # Set up directory structure matching BEAN_RE
        bean_dir = tmp_path / "ai" / "beans" / "BEAN-099-test"
        bean_dir.mkdir(parents=True)
        bean_file = bean_dir / "bean.md"
        bean_file.write_text(make_bean(status="In Progress"))

        stdin_json = self._make_stdin_json(str(bean_file))
        stdout = StringIO()

        with (
            patch("sys.stdin", StringIO(stdin_json)),
            patch("sys.stdout", stdout),
            patch.object(_mod, "now_stamp", return_value="2026-02-09 14:00"),
            patch.object(Path, "cwd", return_value=tmp_path),
        ):
            main()

        output = stdout.getvalue().strip()
        assert output
        result = json.loads(output)
        assert "message" in result
        assert "Started" in result["message"]

    def test_task_edit_produces_stdout(self, tmp_path):
        task_dir = tmp_path / "ai" / "beans" / "BEAN-099-test" / "tasks"
        task_dir.mkdir(parents=True)
        task_file = task_dir / "01-test.md"
        task_file.write_text(make_task(status="Done", started="2026-02-09 13:00"))

        stdin_json = self._make_stdin_json(str(task_file))
        stdout = StringIO()

        with (
            patch("sys.stdin", StringIO(stdin_json)),
            patch("sys.stdout", stdout),
            patch.object(_mod, "now_stamp", return_value="2026-02-09 13:30"),
            patch.object(Path, "cwd", return_value=tmp_path),
        ):
            main()

        output = stdout.getvalue().strip()
        result = json.loads(output)
        assert "Completed" in result["message"]

    def test_non_bean_file_noop(self, tmp_path):
        other = tmp_path / "README.md"
        other.write_text("# Hello")

        stdin_json = self._make_stdin_json(str(other))
        stdout = StringIO()

        with (
            patch("sys.stdin", StringIO(stdin_json)),
            patch("sys.stdout", stdout),
            patch.object(Path, "cwd", return_value=tmp_path),
        ):
            main()

        assert stdout.getvalue().strip() == ""

    def test_error_does_not_crash(self):
        stdout = StringIO()
        stderr = StringIO()

        with (
            patch("sys.stdin", StringIO("invalid json!!")),
            patch("sys.stdout", stdout),
            patch("sys.stderr", stderr),
        ):
            main()  # Should not raise

        assert stdout.getvalue().strip() == ""
        assert "telemetry-stamp" in stderr.getvalue()

    def test_no_file_path_noop(self):
        stdin_json = json.dumps({"tool_name": "Edit", "tool_input": {}})
        stdout = StringIO()

        with (
            patch("sys.stdin", StringIO(stdin_json)),
            patch("sys.stdout", stdout),
        ):
            main()

        assert stdout.getvalue().strip() == ""
