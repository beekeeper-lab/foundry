"""Tests for foundry_app.services.diff_reporter — overlay diff report generation."""

from pathlib import Path

from foundry_app.core.models import (
    FileAction,
    FileActionType,
    OverlayPlan,
)
from foundry_app.services.diff_reporter import write_diff_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_plan(**kwargs) -> OverlayPlan:
    """Build an OverlayPlan with sensible defaults."""
    return OverlayPlan(**kwargs)


def _read_report(output: Path) -> str:
    """Read the generated diff report."""
    return (output / "diff-report.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Basic generation
# ---------------------------------------------------------------------------


class TestBasicGeneration:

    def test_creates_report_file(self, tmp_path: Path):
        plan = _make_plan()
        result = write_diff_report(plan, tmp_path)
        assert (tmp_path / "diff-report.md").is_file()
        assert "diff-report.md" in result.wrote

    def test_returns_stage_result(self, tmp_path: Path):
        result = write_diff_report(_make_plan(), tmp_path)
        assert len(result.wrote) == 1
        assert result.warnings == []

    def test_report_has_header(self, tmp_path: Path):
        write_diff_report(_make_plan(), tmp_path)
        content = _read_report(tmp_path)
        assert "# Diff Report" in content

    def test_report_has_summary_table(self, tmp_path: Path):
        write_diff_report(_make_plan(), tmp_path)
        content = _read_report(tmp_path)
        assert "## Summary" in content
        assert "| Action | Count |" in content

    def test_output_dir_accepts_string(self, tmp_path: Path):
        result = write_diff_report(_make_plan(), str(tmp_path))
        assert len(result.wrote) == 1

    def test_report_has_timestamp(self, tmp_path: Path):
        write_diff_report(_make_plan(), tmp_path)
        content = _read_report(tmp_path)
        assert "Generated:" in content


# ---------------------------------------------------------------------------
# Action sections
# ---------------------------------------------------------------------------


class TestCreatedFiles:

    def test_creates_section_present(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="new-file.txt", action=FileActionType.CREATE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "## Created Files" in content
        assert "`new-file.txt`" in content

    def test_multiple_creates(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="a.txt", action=FileActionType.CREATE),
            FileAction(path="b.txt", action=FileActionType.CREATE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "`a.txt`" in content
        assert "`b.txt`" in content

    def test_create_count_in_summary(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="a.txt", action=FileActionType.CREATE),
            FileAction(path="b.txt", action=FileActionType.CREATE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "| Created | 2 |" in content


class TestUpdatedFiles:

    def test_updates_section_present(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="existing.txt", action=FileActionType.UPDATE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "## Updated Files" in content
        assert "`existing.txt`" in content

    def test_update_count_in_summary(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="a.txt", action=FileActionType.UPDATE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "| Updated | 1 |" in content


class TestDeletedFiles:

    def test_deletes_section_present(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="old.txt", action=FileActionType.DELETE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "## Deleted Files" in content
        assert "`old.txt`" in content

    def test_delete_count_in_summary(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="a.txt", action=FileActionType.DELETE),
            FileAction(path="b.txt", action=FileActionType.DELETE),
            FileAction(path="c.txt", action=FileActionType.DELETE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "| Deleted | 3 |" in content


class TestSkippedFiles:

    def test_skips_section_present(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="same.txt", action=FileActionType.SKIP),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "## Skipped Files" in content
        assert "`same.txt`" in content


# ---------------------------------------------------------------------------
# Mixed actions
# ---------------------------------------------------------------------------


class TestMixedActions:

    def test_all_action_types(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="new.py", action=FileActionType.CREATE),
            FileAction(path="changed.py", action=FileActionType.UPDATE),
            FileAction(path="removed.py", action=FileActionType.DELETE),
            FileAction(path="same.py", action=FileActionType.SKIP),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "| Created | 1 |" in content
        assert "| Updated | 1 |" in content
        assert "| Deleted | 1 |" in content
        assert "| Skipped (unchanged) | 1 |" in content
        assert "| **Total** | **4** |" in content

    def test_total_count(self, tmp_path: Path):
        plan = _make_plan(actions=[
            FileAction(path="a.txt", action=FileActionType.CREATE),
            FileAction(path="b.txt", action=FileActionType.CREATE),
            FileAction(path="c.txt", action=FileActionType.UPDATE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "| **Total** | **3** |" in content


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_empty_plan(self, tmp_path: Path):
        plan = _make_plan()
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "No changes detected." in content
        assert "| Created | 0 |" in content
        assert "| **Total** | **0** |" in content

    def test_empty_plan_no_action_sections(self, tmp_path: Path):
        plan = _make_plan()
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "## Created Files" not in content
        assert "## Updated Files" not in content
        assert "## Deleted Files" not in content

    def test_overwrites_existing_report(self, tmp_path: Path):
        (tmp_path / "diff-report.md").write_text("old content")
        plan = _make_plan(actions=[
            FileAction(path="new.txt", action=FileActionType.CREATE),
        ])
        write_diff_report(plan, tmp_path)
        content = _read_report(tmp_path)
        assert "old content" not in content
        assert "# Diff Report" in content
