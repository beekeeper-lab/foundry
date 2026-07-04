"""Tests for the vdd-gate PreToolUse hook (SPEC-008).

The gate blocks a bean's Status -> Done transition unless a passing VDD
report exists (or the bean carries a justified skip marker). Run as a
subprocess with JSON on stdin, exactly as Claude Code invokes it.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_HOOK = (
    Path(__file__).resolve().parent.parent
    / ".claude" / "shared" / "hooks" / "vdd-gate.py"
)

pytestmark = pytest.mark.skipif(
    not _HOOK.is_file(), reason="claude-kit submodule not initialized"
)

_DONE_ROW = "| **Status** | Done |"
_PENDING_ROW = "| **Status** | In Progress |"


def _run(tool_name: str, tool_input: dict) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    return subprocess.run(
        [sys.executable, str(_HOOK)],
        input=payload, capture_output=True, text=True, timeout=15,
    )


def _project(tmp_path: Path, *, report: str | None = None,
             bean_body: str = "") -> Path:
    bean_dir = tmp_path / "ai" / "beans" / "BEAN-042-example"
    bean_dir.mkdir(parents=True)
    bean = bean_dir / "bean.md"
    bean.write_text(
        f"# BEAN-042\n\n| Field | Value |\n|---|---|\n{_PENDING_ROW}\n"
        f"{bean_body}",
        encoding="utf-8",
    )
    if report is not None:
        qa = tmp_path / "ai" / "outputs" / "tech-qa"
        qa.mkdir(parents=True)
        (qa / "BEAN-042-vdd.md").write_text(report, encoding="utf-8")
    return bean


def _edit_to_done(bean: Path) -> subprocess.CompletedProcess:
    return _run("Edit", {
        "file_path": str(bean),
        "old_string": _PENDING_ROW,
        "new_string": _DONE_ROW,
    })


class TestGateBlocks:
    def test_done_without_report_blocked(self, tmp_path):
        bean = _project(tmp_path)
        proc = _edit_to_done(bean)
        assert proc.returncode == 2
        assert "VDD report" in proc.stderr

    def test_done_with_failing_report_blocked(self, tmp_path):
        bean = _project(tmp_path, report="**Aggregate verdict:** FAIL\n")
        proc = _edit_to_done(bean)
        assert proc.returncode == 2
        assert "not PASS" in proc.stderr


class TestGateAllows:
    def test_done_with_passing_report(self, tmp_path):
        bean = _project(tmp_path, report="**Aggregate verdict:** PASS\n")
        assert _edit_to_done(bean).returncode == 0

    def test_historical_verdict_format(self, tmp_path):
        bean = _project(tmp_path, report="**Verdict:** PASS (with notes)\n")
        assert _edit_to_done(bean).returncode == 0

    def test_justified_skip_marker(self, tmp_path):
        bean = _project(
            tmp_path,
            bean_body="\n<!-- vdd-gate: skip (justified: docs-only bean, "
                      "no runtime surface) -->\n",
        )
        assert _edit_to_done(bean).returncode == 0

    def test_non_transition_edit_allowed(self, tmp_path):
        """Re-saving an already-Done bean (telemetry stamps) is not gated."""
        bean = _project(tmp_path)
        bean.write_text(
            bean.read_text(encoding="utf-8").replace(_PENDING_ROW, _DONE_ROW),
            encoding="utf-8",
        )
        proc = _run("Edit", {
            "file_path": str(bean),
            "old_string": _DONE_ROW + "\n",
            "new_string": _DONE_ROW + "\n| **Duration** | 14m |\n",
        })
        assert proc.returncode == 0

    def test_non_bean_files_ignored(self, tmp_path):
        f = tmp_path / "notes.md"
        proc = _run("Write", {"file_path": str(f), "content": _DONE_ROW})
        assert proc.returncode == 0

    def test_status_change_to_in_progress_ignored(self, tmp_path):
        bean = _project(tmp_path)
        proc = _run("Edit", {
            "file_path": str(bean),
            "old_string": "| **Status** | Approved |",
            "new_string": _PENDING_ROW,
        })
        assert proc.returncode == 0


class TestHandoffReminder:
    """SPEC-008 follow-through: non-blocking reminder when a bean closes
    with no typed handoff packet."""

    _REMINDER_HOOK = _HOOK.parent / "handoff-reminder.py"

    def _run_reminder(self, tool_input: dict) -> subprocess.CompletedProcess:
        payload = json.dumps({"tool_name": "Edit", "tool_input": tool_input})
        return subprocess.run(
            [sys.executable, str(self._REMINDER_HOOK)],
            input=payload, capture_output=True, text=True, timeout=15,
        )

    def test_reminds_without_packet_but_never_blocks(self, tmp_path):
        bean = _project(tmp_path)
        proc = self._run_reminder({
            "file_path": str(bean),
            "old_string": _PENDING_ROW,
            "new_string": _DONE_ROW,
        })
        assert proc.returncode == 0
        assert "handoff" in proc.stderr.lower()

    def test_silent_when_packet_exists(self, tmp_path):
        bean = _project(tmp_path)
        handoffs = tmp_path / "ai" / "handoffs"
        handoffs.mkdir(parents=True)
        (handoffs / "developer-to-tech-qa-BEAN-042-task-01.md").write_text("x")
        proc = self._run_reminder({
            "file_path": str(bean),
            "old_string": _PENDING_ROW,
            "new_string": _DONE_ROW,
        })
        assert proc.returncode == 0
        assert proc.stderr.strip() == ""
