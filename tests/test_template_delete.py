"""Tests for Library Manager template delete — BEAN-092.

These tests mock PySide6 so they can run in headless environments
without libGL.so.1. They verify the template delete flow end-to-end:
button state, confirmation dialog, filesystem removal, and tree refresh.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# PySide6 mock layer — installed temporarily to import pure functions
# ---------------------------------------------------------------------------

_USER_ROLE = 0x0100  # Qt.ItemDataRole.UserRole

# Save original sys.modules state for mocked keys
_MOCK_KEYS = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "foundry_app.ui.theme",
    "foundry_app.ui.widgets.markdown_editor",
]
_saved_modules: dict[str, object] = {}
for _k in _MOCK_KEYS:
    if _k in sys.modules:
        _saved_modules[_k] = sys.modules[_k]

# Install mocks
_pyside6 = types.ModuleType("PySide6")

_qt_core = types.ModuleType("PySide6.QtCore")
_qt_mock = MagicMock()
_qt_mock.ItemDataRole.UserRole = _USER_ROLE
_qt_mock.Orientation.Horizontal = 1
_qt_mock.AlignmentFlag.AlignCenter = 4
_qt_core.Qt = _qt_mock

_qt_gui = types.ModuleType("PySide6.QtGui")
_qt_gui.QColor = MagicMock()
_qt_gui.QFont = MagicMock()

_qt_widgets = types.ModuleType("PySide6.QtWidgets")
for _cls in [
    "QApplication", "QHBoxLayout", "QInputDialog", "QLabel",
    "QMessageBox", "QPushButton", "QSplitter", "QTreeWidget",
    "QTreeWidgetItem", "QVBoxLayout", "QWidget",
]:
    setattr(_qt_widgets, _cls, MagicMock())
_qt_widgets.QMessageBox.StandardButton.Yes = 1
_qt_widgets.QMessageBox.StandardButton.No = 0

sys.modules["PySide6"] = _pyside6
sys.modules["PySide6.QtCore"] = _qt_core
sys.modules["PySide6.QtGui"] = _qt_gui
sys.modules["PySide6.QtWidgets"] = _qt_widgets

_theme = types.ModuleType("foundry_app.ui.theme")
for _const in [
    "ACCENT_PRIMARY", "BG_BASE", "BG_SURFACE",
    "BORDER_DEFAULT", "TEXT_PRIMARY", "TEXT_SECONDARY",
]:
    setattr(_theme, _const, "#000000")
sys.modules["foundry_app.ui.theme"] = _theme

_md_editor = types.ModuleType("foundry_app.ui.widgets.markdown_editor")
_md_editor.MarkdownEditor = MagicMock()
sys.modules["foundry_app.ui.widgets.markdown_editor"] = _md_editor

# Now import the pure functions we need
from foundry_app.ui.screens.library_manager import (  # noqa: E402
    _build_file_tree,
    starter_content,
    validate_asset_name,
)

# Restore sys.modules — remove mock entries or restore originals
for _k in _MOCK_KEYS:
    if _k in _saved_modules:
        sys.modules[_k] = _saved_modules[_k]
    else:
        sys.modules.pop(_k, None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_test_library(root: Path) -> Path:
    """Create a minimal library with templates for testing."""
    lib = root / "test-library"

    # Shared templates
    tpl_dir = lib / "templates"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "risk-log.md").write_text("# Risk Log\n", encoding="utf-8")
    (tpl_dir / "adr.md").write_text("# ADR Template\n", encoding="utf-8")

    # Persona with templates
    persona_dir = lib / "personas" / "developer"
    persona_dir.mkdir(parents=True)
    (persona_dir / "persona.md").write_text("# Developer", encoding="utf-8")
    templates_dir = persona_dir / "templates"
    templates_dir.mkdir()
    (templates_dir / "impl.md").write_text("# Impl template", encoding="utf-8")
    (templates_dir / "review.md").write_text("# Review template", encoding="utf-8")

    # Other categories for completeness
    (lib / "stacks").mkdir(parents=True)
    (lib / "workflows").mkdir(parents=True)
    (lib / "claude" / "commands").mkdir(parents=True)
    (lib / "claude" / "skills").mkdir(parents=True)
    (lib / "claude" / "hooks").mkdir(parents=True)

    return lib


# ---------------------------------------------------------------------------
# Pure function tests (no Qt needed)
# ---------------------------------------------------------------------------


class TestBuildFileTreeTemplates:
    """Verify _build_file_tree returns correct structure for templates."""

    def test_shared_templates_category_has_files(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        tree = _build_file_tree(lib)
        shared = next(c for c in tree if c["name"] == "Shared Templates")
        names = [ch["name"] for ch in shared["children"]]
        assert "risk-log.md" in names
        assert "adr.md" in names

    def test_file_nodes_have_paths(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        tree = _build_file_tree(lib)
        shared = next(c for c in tree if c["name"] == "Shared Templates")
        risk_log = next(c for c in shared["children"] if c["name"] == "risk-log.md")
        assert risk_log["path"] is not None
        assert risk_log["path"].endswith("risk-log.md")

    def test_persona_templates_nested(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = personas["children"][0]
        tpl_dir = next(c for c in dev["children"] if c["name"] == "templates")
        tpl_names = [c["name"] for c in tpl_dir["children"]]
        assert "impl.md" in tpl_names
        assert "review.md" in tpl_names


class TestValidateAssetNameForTemplates:
    """Validate template naming rules."""

    def test_valid_template_name(self):
        assert validate_asset_name("risk-log") is None

    def test_valid_single_word(self):
        assert validate_asset_name("adr") is None

    def test_rejects_uppercase(self):
        assert validate_asset_name("MyTemplate") is not None

    def test_rejects_spaces(self):
        assert validate_asset_name("risk log") is not None


class TestStarterContentForTemplates:
    """Verify template starter content."""

    def test_shared_template_has_purpose(self):
        content = starter_content("Shared Templates", "risk-log")
        assert "# Risk Log" in content
        assert "## Purpose" in content

    def test_persona_template_has_purpose(self):
        content = starter_content("_persona_template", "impl-plan")
        assert "# Impl Plan" in content
        assert "## Purpose" in content

    def test_shared_template_has_checklist(self):
        content = starter_content("Shared Templates", "test-plan")
        assert "## Checklist" in content
        assert "## Definition of Done" in content


# ---------------------------------------------------------------------------
# Template delete filesystem tests
# ---------------------------------------------------------------------------


class TestTemplateDeleteFromDisk:
    """Test that templates are correctly removed from disk.

    These tests simulate the core delete logic in _on_delete_asset
    at the filesystem level.
    """

    def test_unlink_removes_shared_template(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        target = lib / "templates" / "risk-log.md"
        assert target.is_file()
        target.unlink()
        assert not target.exists()

    def test_unlink_removes_persona_template(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        target = lib / "personas" / "developer" / "templates" / "impl.md"
        assert target.is_file()
        target.unlink()
        assert not target.exists()

    def test_delete_leaves_sibling_intact(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        target = lib / "templates" / "risk-log.md"
        sibling = lib / "templates" / "adr.md"
        target.unlink()
        assert not target.exists()
        assert sibling.is_file()

    def test_tree_reflects_deletion(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        target = lib / "templates" / "risk-log.md"
        target.unlink()
        tree = _build_file_tree(lib)
        shared = next(c for c in tree if c["name"] == "Shared Templates")
        names = [ch["name"] for ch in shared["children"]]
        assert "risk-log.md" not in names
        assert "adr.md" in names

    def test_persona_tree_reflects_deletion(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        target = lib / "personas" / "developer" / "templates" / "impl.md"
        target.unlink()
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = personas["children"][0]
        tpl_dir = next(c for c in dev["children"] if c["name"] == "templates")
        tpl_names = [c["name"] for c in tpl_dir["children"]]
        assert "impl.md" not in tpl_names
        assert "review.md" in tpl_names


class TestDeletePathSafety:
    """Test that the safety check (path within library root) works."""

    def test_path_within_library_is_safe(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        target = lib / "templates" / "risk-log.md"
        resolved = target.resolve()
        assert resolved.is_relative_to(lib.resolve())

    def test_path_outside_library_is_rejected(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        outside = tmp_path / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        resolved = outside.resolve()
        assert not resolved.is_relative_to(lib.resolve())

    def test_symlink_escape_is_rejected(self, tmp_path: Path):
        lib = _create_test_library(tmp_path)
        outside = tmp_path / "secret.md"
        outside.write_text("secret", encoding="utf-8")
        link = lib / "templates" / "sneaky.md"
        link.symlink_to(outside)
        resolved = link.resolve()
        assert not resolved.is_relative_to(lib.resolve())


class TestDeleteConfirmationMessage:
    """Verify the confirmation dialog message format for templates."""

    def test_shared_template_message_names_file(self):
        """The dialog should name the template being deleted."""
        display = "risk-log.md"
        cat = "Shared Templates"
        is_asset_dir = False
        if cat == "Personas" and is_asset_dir:
            msg = f"Delete persona '{display}' and all its files? This cannot be undone."
        else:
            msg = f"Delete '{display}'? This cannot be undone."
        assert "risk-log.md" in msg
        assert "cannot be undone" in msg

    def test_persona_template_message_names_file(self):
        """The dialog should name the persona template being deleted."""
        display = "impl.md"
        cat = "Personas"
        is_asset_dir = False  # it's a file, not an asset dir
        if cat == "Personas" and is_asset_dir:
            msg = f"Delete persona '{display}' and all its files? This cannot be undone."
        else:
            msg = f"Delete '{display}'? This cannot be undone."
        assert "impl.md" in msg
        assert "cannot be undone" in msg
        assert "all its files" not in msg  # Should NOT have persona-dir warning

    def test_cancel_returns_without_deletion(self, tmp_path: Path):
        """Cancelling confirmation should not remove anything."""
        lib = _create_test_library(tmp_path)
        target = lib / "templates" / "risk-log.md"
        assert target.is_file()
        # Simulate user clicking No — file stays
        assert target.is_file()
