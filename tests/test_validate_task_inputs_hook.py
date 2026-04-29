"""Tests for .claude/shared/hooks/validate-task-inputs.py PreToolUse hook."""

from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

_HOOK_PATH = (
    Path(__file__).resolve().parent.parent
    / ".claude"
    / "shared"
    / "hooks"
    / "validate-task-inputs.py"
)
_spec = importlib.util.spec_from_file_location("validate_task_inputs", _HOOK_PATH)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

is_task_file = _mod.is_task_file
is_in_progress_transition = _mod.is_in_progress_transition
extract_inputs_section = _mod.extract_inputs_section
parse_inputs_bullets = _mod.parse_inputs_bullets
has_valid_escape_hatch = _mod.has_valid_escape_hatch
all_bullets_are_sentinel = _mod.all_bullets_are_sentinel
validate_task_inputs = _mod.validate_task_inputs
main = _mod.main


# ---------------------------------------------------------------------------
# Pure-function tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path,expected",
    [
        ("ai/beans/BEAN-001-foo/tasks/01-developer-bar.md", True),
        ("ai/beans/BEAN-272-validate/tasks/02-tech-qa-verify.md", True),
        ("ai/beans/BEAN-001-foo/bean.md", False),
        ("ai/beans/_index.md", False),
        ("ai/beans/BEAN-001-foo/tasks/", False),
        ("foundry_app/services/generator.py", False),
        ("", False),
    ],
)
def test_is_task_file(path, expected):
    assert is_task_file(path) is expected


def test_is_in_progress_transition_matches_metadata_row():
    assert is_in_progress_transition("| **Status** | In Progress |")


def test_is_in_progress_transition_case_insensitive():
    assert is_in_progress_transition("| **Status** | IN PROGRESS |")


def test_is_in_progress_transition_rejects_other_statuses():
    assert not is_in_progress_transition("| **Status** | Done |")
    assert not is_in_progress_transition("| **Status** | Pending |")
    assert not is_in_progress_transition("")


def test_extract_inputs_section_returns_body():
    text = (
        "# Task\n\n"
        "## Goal\n\nthings\n\n"
        "## Inputs\n\n- file_a\n- file_b\n\n"
        "## Acceptance Criteria\n\n- [ ] x\n"
    )
    section = extract_inputs_section(text)
    assert section is not None
    assert "- file_a" in section
    assert "- file_b" in section
    assert "Acceptance Criteria" not in section


def test_extract_inputs_section_returns_none_when_missing():
    text = "# Task\n\n## Goal\n\nthings\n\n## Acceptance Criteria\n\n- [ ] x\n"
    assert extract_inputs_section(text) is None


def test_parse_inputs_bullets_picks_up_dashes_and_stars():
    section = "\n- one\n* two\n+ three\n  - indented\nplain line\n"
    assert parse_inputs_bullets(section) == ["one", "two", "three", "indented"]


def test_parse_inputs_bullets_skips_empty():
    section = "\n- \n- real\n"
    assert parse_inputs_bullets(section) == ["real"]


def test_all_bullets_are_sentinel_true_for_empty():
    assert all_bullets_are_sentinel([]) is True


def test_all_bullets_are_sentinel_true_for_dashes():
    assert all_bullets_are_sentinel(["—", "-", "--"]) is True


def test_all_bullets_are_sentinel_false_when_any_real():
    assert all_bullets_are_sentinel(["—", "real_path.py"]) is False


def test_has_valid_escape_hatch_accepts_long_reason():
    text = "Inputs: NONE (justified: this task scans the whole repo for X)"
    assert has_valid_escape_hatch(text)


def test_has_valid_escape_hatch_rejects_short_reason():
    text = "Inputs: NONE (justified: short)"
    assert not has_valid_escape_hatch(text)


def test_has_valid_escape_hatch_rejects_whitespace_only_reason():
    text = "Inputs: NONE (justified:                          )"
    assert not has_valid_escape_hatch(text)


def test_has_valid_escape_hatch_rejects_missing_marker():
    text = "Inputs:\n- file_a"
    assert not has_valid_escape_hatch(text)


# ---------------------------------------------------------------------------
# validate_task_inputs() — full-text behavior
# ---------------------------------------------------------------------------


def _task_text(inputs_block: str) -> str:
    return (
        "# Task 01\n\n"
        "| Field | Value |\n"
        "|-------|-------|\n"
        "| **Owner** | Developer |\n"
        "| **Status** | In Progress |\n\n"
        "## Goal\nDo a thing.\n\n"
        f"{inputs_block}\n"
        "## Acceptance Criteria\n- [ ] done\n"
    )


def test_validate_pass_with_populated_inputs():
    text = _task_text("## Inputs\n\n- foo/bar.py\n- ai/beans/BEAN-X/bean.md\n")
    ok, msg = validate_task_inputs(text)
    assert ok
    assert msg == ""


def test_validate_fail_when_inputs_section_missing():
    text = (
        "# Task 01\n\n"
        "| Field | Value |\n"
        "|-------|-------|\n"
        "| **Status** | In Progress |\n\n"
        "## Goal\nDo a thing.\n\n"
        "## Acceptance Criteria\n- [ ] done\n"
    )
    ok, msg = validate_task_inputs(text)
    assert not ok
    assert "missing" in msg.lower()


def test_validate_fail_when_inputs_empty():
    text = _task_text("## Inputs\n\n")
    ok, msg = validate_task_inputs(text)
    assert not ok
    assert "empty" in msg.lower()


def test_validate_fail_when_only_sentinel_dashes():
    text = _task_text("## Inputs\n\n- —\n- —\n")
    ok, msg = validate_task_inputs(text)
    assert not ok
    assert "sentinel" in msg.lower()


def test_validate_pass_with_escape_hatch():
    text = (
        "# Task 01\n\n"
        "| **Status** | In Progress |\n\n"
        "## Goal\nScan everything.\n\n"
        "Inputs: NONE (justified: this task scans the whole repo for stale TODOs)\n\n"
        "## Acceptance Criteria\n- [ ] done\n"
    )
    ok, msg = validate_task_inputs(text)
    assert ok
    assert msg == ""


def test_validate_fail_with_escape_hatch_too_short():
    text = (
        "# Task 01\n\n"
        "| **Status** | In Progress |\n\n"
        "## Goal\nScan.\n\n"
        "Inputs: NONE (justified: short)\n\n"
        "## Acceptance Criteria\n- [ ] done\n"
    )
    ok, msg = validate_task_inputs(text)
    assert not ok


# ---------------------------------------------------------------------------
# main() — JSON envelope behavior
# ---------------------------------------------------------------------------


def _run_main(payload: dict) -> int:
    """Invoke main() with a stdin JSON payload; return exit code."""
    with patch("sys.stdin", StringIO(json.dumps(payload))):
        with pytest.raises(SystemExit) as exc:
            main()
        return exc.value.code or 0


def test_main_passes_for_non_task_files(tmp_path):
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": str(tmp_path / "foundry_app/services/foo.py"),
            "new_string": "| **Status** | In Progress |",
        },
    }
    assert _run_main(payload) == 0


def test_main_passes_for_non_in_progress_edits(tmp_path):
    task = tmp_path / "ai/beans/BEAN-1-x/tasks/01-dev-foo.md"
    task.parent.mkdir(parents=True)
    task.write_text(_task_text("## Inputs\n\n- a.py\n"))
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": str(task),
            "new_string": "| **Status** | Done |",
        },
    }
    assert _run_main(payload) == 0


def test_main_blocks_when_inputs_missing(tmp_path, capsys):
    task = tmp_path / "ai/beans/BEAN-1-x/tasks/01-dev-foo.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "# Task\n\n| **Status** | In Progress |\n\n"
        "## Goal\nx\n\n## Acceptance Criteria\n- [ ] y\n"
    )
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": str(task),
            "new_string": "| **Status** | In Progress |",
        },
    }
    assert _run_main(payload) == 2
    captured = capsys.readouterr()
    assert "BLOCKED" in captured.err
    assert str(task) in captured.err


def test_main_passes_when_inputs_populated(tmp_path):
    task = tmp_path / "ai/beans/BEAN-1-x/tasks/01-dev-foo.md"
    task.parent.mkdir(parents=True)
    task.write_text(_task_text("## Inputs\n\n- ai/beans/BEAN-1-x/bean.md\n"))
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": str(task),
            "new_string": "| **Status** | In Progress |",
        },
    }
    assert _run_main(payload) == 0


def test_main_passes_with_escape_hatch(tmp_path):
    task = tmp_path / "ai/beans/BEAN-1-x/tasks/01-dev-foo.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "# Task\n\n| **Status** | In Progress |\n\n"
        "## Goal\nScan everything.\n\n"
        "Inputs: NONE (justified: this is a repo-wide scan with no specific input)\n\n"
        "## Acceptance Criteria\n- [ ] x\n"
    )
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": str(task),
            "new_string": "| **Status** | In Progress |",
        },
    }
    assert _run_main(payload) == 0


def test_main_handles_invalid_json(capsys):
    with patch("sys.stdin", StringIO("not json")):
        with pytest.raises(SystemExit) as exc:
            main()
        assert (exc.value.code or 0) == 0


def test_main_passes_for_non_edit_tools():
    payload = {"tool_name": "Bash", "tool_input": {"command": "ls"}}
    assert _run_main(payload) == 0


def test_main_handles_write_tool(tmp_path):
    """Write tool uses `content` field instead of `new_string`."""
    task = tmp_path / "ai/beans/BEAN-1-x/tasks/01-dev-foo.md"
    task.parent.mkdir(parents=True)
    task.write_text(_task_text("## Inputs\n\n- foo.py\n"))
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": str(task),
            "content": _task_text("## Inputs\n\n- foo.py\n").replace(
                "Pending", "In Progress"
            ),
        },
    }
    # Even though content has Pending->In Progress somewhere, the file's
    # current Inputs is populated, so it passes.
    # Adjust: ensure file content is what the validator reads (current state).
    assert _run_main(payload) == 0
