"""Tests for foundry_app.ui.screens.settings_screen — core path configuration."""

from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from foundry_app.core.settings import FoundrySettings
from foundry_app.ui.screens.settings_screen import SettingsScreen

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_settings(tmp_path: Path) -> FoundrySettings:
    """Create a FoundrySettings that writes to an isolated location."""
    settings = FoundrySettings()
    # Clear any previous state
    settings._qs.clear()
    return settings


# ---------------------------------------------------------------------------
# Library root
# ---------------------------------------------------------------------------


class TestLibraryRoot:

    def test_set_library_root_updates_field(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)
        screen.set_library_root("/some/path")
        assert screen.library_root_edit.text() == "/some/path"

    def test_set_library_root_persists(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)
        screen.set_library_root("/some/path")
        assert settings.library_root == "/some/path"

    def test_set_library_root_adds_to_recent(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)
        screen.set_library_root("/path/one")
        assert "/path/one" in settings.recent_libraries

    def test_set_library_root_emits_signal(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)
        received = []
        screen.settings_changed.connect(lambda p: received.append(p))
        screen.set_library_root("/new/path")
        assert len(received) == 1
        assert received[0] == "/new/path"

    def test_loads_existing_library_root(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        settings.library_root = "/existing/library"
        screen = SettingsScreen(settings=settings)
        assert screen.library_root_edit.text() == "/existing/library"


# ---------------------------------------------------------------------------
# Workspace root
# ---------------------------------------------------------------------------


class TestWorkspaceRoot:

    def test_loads_existing_workspace_root(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        settings.workspace_root = "/existing/workspace"
        screen = SettingsScreen(settings=settings)
        assert screen.workspace_root_edit.text() == "/existing/workspace"


# ---------------------------------------------------------------------------
# Recent libraries
# ---------------------------------------------------------------------------


class TestRecentLibraries:

    def test_recent_combo_populated(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        settings.add_recent_library("/lib/one")
        settings.add_recent_library("/lib/two")
        screen = SettingsScreen(settings=settings)
        assert screen.recent_combo.count() == 2

    def test_select_recent_updates_library_root(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        settings.add_recent_library("/lib/first")
        settings.add_recent_library("/lib/second")
        screen = SettingsScreen(settings=settings)

        received = []
        screen.settings_changed.connect(lambda p: received.append(p))

        # Select the second item (index 1 = /lib/first since recent is LIFO)
        screen._on_recent_selected(1)
        assert screen.library_root_edit.text() == "/lib/first"
        assert len(received) == 1

    def test_multiple_set_library_root_updates_recent(self, tmp_path: Path):
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)
        screen.set_library_root("/path/a")
        screen.set_library_root("/path/b")
        assert screen.recent_combo.count() == 2


# ---------------------------------------------------------------------------
# Browse dialog (mocked)
# ---------------------------------------------------------------------------


class TestBrowse:

    @patch("foundry_app.ui.screens.settings_screen.QFileDialog.getExistingDirectory")
    def test_browse_library_sets_path(self, mock_dialog, tmp_path: Path):
        mock_dialog.return_value = "/browsed/library"
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)

        received = []
        screen.settings_changed.connect(lambda p: received.append(p))
        screen._browse_library()

        assert screen.library_root_edit.text() == "/browsed/library"
        assert settings.library_root == "/browsed/library"
        assert len(received) == 1

    @patch("foundry_app.ui.screens.settings_screen.QFileDialog.getExistingDirectory")
    def test_browse_library_cancelled(self, mock_dialog, tmp_path: Path):
        mock_dialog.return_value = ""
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)
        screen._browse_library()
        assert screen.library_root_edit.text() == ""

    @patch("foundry_app.ui.screens.settings_screen.QFileDialog.getExistingDirectory")
    def test_browse_workspace_sets_path(self, mock_dialog, tmp_path: Path):
        mock_dialog.return_value = "/browsed/workspace"
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)
        screen._browse_workspace()
        assert screen.workspace_root_edit.text() == "/browsed/workspace"
        assert settings.workspace_root == "/browsed/workspace"

    @patch("foundry_app.ui.screens.settings_screen.QFileDialog.getExistingDirectory")
    def test_browse_workspace_cancelled(self, mock_dialog, tmp_path: Path):
        mock_dialog.return_value = ""
        settings = _make_settings(tmp_path)
        screen = SettingsScreen(settings=settings)
        screen._browse_workspace()
        assert screen.workspace_root_edit.text() == ""
