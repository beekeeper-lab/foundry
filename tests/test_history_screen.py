"""Tests for foundry_app.ui.screens.history_screen — generation history browser."""

import json
from pathlib import Path

from PySide6.QtWidgets import QApplication

from foundry_app.ui.screens.history_screen import HistoryScreen

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_run(root: Path, name: str, run_id: str = "test-run") -> Path:
    """Create a fake generated project with a manifest."""
    proj = root / name
    proj.mkdir(parents=True)
    manifest = {
        "run_id": run_id,
        "generated_at": "2026-02-07T12:00:00",
        "library_version": "abc1234",
        "stages": {
            "scaffold": {"wrote": ["dir1/", "dir2/"], "warnings": []},
            "compile": {"wrote": ["a.md", "b.md", "c.md"], "warnings": []},
        },
    }
    (proj / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return proj


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:

    def test_creates_screen(self):
        screen = HistoryScreen()
        assert screen is not None

    def test_has_run_list(self):
        screen = HistoryScreen()
        assert screen.run_list is not None

    def test_has_details_widget(self):
        screen = HistoryScreen()
        assert screen.details_widget is not None

    def test_has_meta_label(self):
        screen = HistoryScreen()
        assert screen.meta_label is not None

    def test_has_regenerate_button(self):
        screen = HistoryScreen()
        assert screen.regenerate_button is not None
        assert not screen.regenerate_button.isEnabled()


# ---------------------------------------------------------------------------
# Run listing
# ---------------------------------------------------------------------------


class TestRunListing:

    def test_empty_root(self, tmp_path: Path):
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        assert screen.run_list.count() == 0

    def test_lists_runs_with_manifests(self, tmp_path: Path):
        _create_run(tmp_path, "run-a")
        _create_run(tmp_path, "run-b")
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        assert screen.run_list.count() == 2

    def test_ignores_dirs_without_manifest(self, tmp_path: Path):
        (tmp_path / "no-manifest").mkdir()
        _create_run(tmp_path, "has-manifest")
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        assert screen.run_list.count() == 1

    def test_refresh_updates_list(self, tmp_path: Path):
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        assert screen.run_list.count() == 0
        _create_run(tmp_path, "new-run")
        screen.refresh_runs()
        assert screen.run_list.count() == 1

    def test_nonexistent_root(self, tmp_path: Path):
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path / "nonexistent")
        assert screen.run_list.count() == 0


# ---------------------------------------------------------------------------
# Manifest viewing
# ---------------------------------------------------------------------------


class TestManifestViewing:

    def test_select_run_shows_manifest(self, tmp_path: Path):
        _create_run(tmp_path, "my-run", run_id="test-123")
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        screen.run_list.setCurrentRow(0)
        content = screen.details_widget.toPlainText()
        assert "test-123" in content

    def test_select_run_shows_metadata(self, tmp_path: Path):
        _create_run(tmp_path, "my-run", run_id="test-123")
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        screen.run_list.setCurrentRow(0)
        meta = screen.meta_label.text()
        assert "test-123" in meta
        assert "Files: 5" in meta  # 2 + 3 files from helper

    def test_select_run_enables_regenerate(self, tmp_path: Path):
        _create_run(tmp_path, "my-run")
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        screen.run_list.setCurrentRow(0)
        assert screen.regenerate_button.isEnabled()

    def test_no_selection_returns_none(self):
        screen = HistoryScreen()
        assert screen.selected_manifest_path() is None

    def test_corrupt_manifest(self, tmp_path: Path):
        proj = tmp_path / "bad-run"
        proj.mkdir()
        (proj / "manifest.json").write_text("not json!", encoding="utf-8")
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        screen.run_list.setCurrentRow(0)
        content = screen.details_widget.toPlainText()
        assert "Error" in content


# ---------------------------------------------------------------------------
# Regenerate signal
# ---------------------------------------------------------------------------


class TestRegenerate:

    def test_regenerate_emits_signal(self, tmp_path: Path):
        proj = _create_run(tmp_path, "my-run")
        screen = HistoryScreen()
        screen.set_projects_root(tmp_path)
        screen.run_list.setCurrentRow(0)

        received = []
        screen.regenerate_requested.connect(lambda p: received.append(p))
        screen._on_regenerate()
        assert len(received) == 1
        assert received[0] == str(proj)
