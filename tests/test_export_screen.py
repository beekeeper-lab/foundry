"""Tests for foundry_app.ui.screens.export_screen — project export."""

import json
from pathlib import Path

from PySide6.QtWidgets import QApplication

from foundry_app.ui.screens.export_screen import ExportScreen

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_project(root: Path, name: str, with_manifest: bool = True) -> Path:
    """Create a fake generated project directory."""
    proj = root / name
    proj.mkdir(parents=True)
    if with_manifest:
        (proj / "manifest.json").write_text(
            json.dumps({"run_id": "test", "stages": {}}),
            encoding="utf-8",
        )
    return proj


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:

    def test_creates_screen(self):
        screen = ExportScreen()
        assert screen is not None

    def test_has_project_list(self):
        screen = ExportScreen()
        assert screen.project_list is not None

    def test_has_format_combo(self):
        screen = ExportScreen()
        assert screen.format_combo.count() >= 2

    def test_has_export_button(self):
        screen = ExportScreen()
        assert screen.export_button is not None
        assert not screen.export_button.isEnabled()

    def test_has_status_label(self):
        screen = ExportScreen()
        assert screen.status_label is not None


# ---------------------------------------------------------------------------
# Project listing
# ---------------------------------------------------------------------------


class TestProjectListing:

    def test_empty_root(self, tmp_path: Path):
        screen = ExportScreen()
        screen.set_projects_root(tmp_path)
        assert screen.project_list.count() == 0

    def test_lists_directories(self, tmp_path: Path):
        _create_project(tmp_path, "project-a")
        _create_project(tmp_path, "project-b")
        screen = ExportScreen()
        screen.set_projects_root(tmp_path)
        assert screen.project_list.count() == 2

    def test_manifest_indicator(self, tmp_path: Path):
        _create_project(tmp_path, "my-proj", with_manifest=True)
        screen = ExportScreen()
        screen.set_projects_root(tmp_path)
        item = screen.project_list.item(0)
        assert "manifest found" in item.text()

    def test_no_manifest_no_indicator(self, tmp_path: Path):
        _create_project(tmp_path, "bare-proj", with_manifest=False)
        screen = ExportScreen()
        screen.set_projects_root(tmp_path)
        item = screen.project_list.item(0)
        assert "manifest" not in item.text()

    def test_refresh_updates_list(self, tmp_path: Path):
        screen = ExportScreen()
        screen.set_projects_root(tmp_path)
        assert screen.project_list.count() == 0

        _create_project(tmp_path, "new-proj")
        screen.refresh_projects()
        assert screen.project_list.count() == 1

    def test_nonexistent_root(self, tmp_path: Path):
        screen = ExportScreen()
        screen.set_projects_root(tmp_path / "nonexistent")
        assert screen.project_list.count() == 0


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


class TestSelection:

    def test_no_selection_returns_none(self):
        screen = ExportScreen()
        assert screen.selected_project_path() is None

    def test_selection_enables_export(self, tmp_path: Path):
        _create_project(tmp_path, "proj")
        screen = ExportScreen()
        screen.set_projects_root(tmp_path)
        screen.project_list.setCurrentRow(0)
        assert screen.export_button.isEnabled()

    def test_selected_path(self, tmp_path: Path):
        proj = _create_project(tmp_path, "my-proj")
        screen = ExportScreen()
        screen.set_projects_root(tmp_path)
        screen.project_list.setCurrentRow(0)
        assert screen.selected_project_path() == proj
