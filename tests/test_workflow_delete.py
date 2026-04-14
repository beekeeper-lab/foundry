"""Tests for BEAN-096: Library Manager — Workflow Delete.

These tests mock PySide6 at the sys.modules level so they can run in
environments where libGL.so.1 is unavailable (CI headless workers, etc.).
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# PySide6 mock scaffolding — must be installed before importing the SUT
# ---------------------------------------------------------------------------

_PYSIDE6_INSTALLED = "PySide6.QtCore" in sys.modules

if not _PYSIDE6_INSTALLED:
    _pyside6 = ModuleType("PySide6")
    _qt_core = ModuleType("PySide6.QtCore")
    _qt_gui = ModuleType("PySide6.QtGui")
    _qt_widgets = ModuleType("PySide6.QtWidgets")

    # QtCore stubs
    _qt_mock = MagicMock()
    _qt_mock.Orientation.Horizontal = 1
    _qt_mock.AlignmentFlag.AlignCenter = 0x0084
    _qt_mock.ItemDataRole.UserRole = 0x0100
    _qt_core.Qt = _qt_mock
    _qt_core.QTimer = MagicMock()
    _qt_core.Signal = MagicMock(return_value=MagicMock())

    # QtGui stubs
    _qt_gui.QColor = MagicMock()
    _qt_gui.QFont = MagicMock()

    # QWidget must be a real class (not MagicMock) so that classes inheriting
    # from it can be instantiated via __new__.
    class _StubQWidget:
        def __init__(self, *a, **kw):
            pass

        def setStyleSheet(self, *a):
            pass

        def setToolTip(self, *a):
            pass

        def setAlignment(self, *a):
            pass

        def setWordWrap(self, *a):
            pass

        def hide(self, *a):
            pass

        def show(self, *a):
            pass

    # QtWidgets stubs
    _qt_widgets.QApplication = MagicMock()
    _qt_widgets.QHBoxLayout = MagicMock()
    _qt_widgets.QInputDialog = MagicMock()
    _qt_widgets.QLabel = MagicMock()
    _qt_widgets.QMessageBox = MagicMock()
    _qt_widgets.QMessageBox.StandardButton = MagicMock()
    _qt_widgets.QMessageBox.StandardButton.Yes = 16384
    _qt_widgets.QMessageBox.StandardButton.No = 65536
    _qt_widgets.QPushButton = MagicMock()
    _qt_widgets.QPlainTextEdit = MagicMock()
    _qt_widgets.QSplitter = MagicMock()
    _qt_widgets.QTextBrowser = MagicMock()
    _qt_widgets.QTreeWidget = MagicMock()
    _qt_widgets.QTreeWidgetItem = MagicMock()
    _qt_widgets.QVBoxLayout = MagicMock()
    _qt_widgets.QWidget = _StubQWidget

    sys.modules.setdefault("PySide6", _pyside6)
    sys.modules.setdefault("PySide6.QtCore", _qt_core)
    sys.modules.setdefault("PySide6.QtGui", _qt_gui)
    sys.modules.setdefault("PySide6.QtWidgets", _qt_widgets)

    # markdown_editor also imports mistune — stub it if missing
    if "mistune" not in sys.modules:
        sys.modules["mistune"] = MagicMock()

# Now safe to import the system under test
from foundry_app.ui.screens.library_manager import (  # noqa: E402
    _EDITABLE_CATEGORIES,
    LIBRARY_CATEGORIES,
    LibraryManagerScreen,
    _build_file_tree,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_library(root: Path) -> Path:
    """Create a minimal library directory structure with workflows."""
    lib = root / "test-library"
    # Workflows
    wf_dir = lib / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "deploy.md").write_text("# Deploy workflow", encoding="utf-8")
    (wf_dir / "release.md").write_text("# Release workflow", encoding="utf-8")
    (wf_dir / "hotfix.md").write_text("# Hotfix workflow", encoding="utf-8")
    # Stubs for other categories so the tree populates normally
    for _, rel in LIBRARY_CATEGORIES:
        (lib / rel).mkdir(parents=True, exist_ok=True)
    return lib


def _make_tree_item(name: str, file_path: str | None = None, parent=None):
    """Create a mock QTreeWidgetItem with realistic behaviour."""
    item = MagicMock()
    item.text.return_value = name
    item.data.return_value = file_path
    item.parent.return_value = parent
    item.childCount.return_value = 0
    item.children = []

    def add_child(child):
        item.children.append(child)
        child.parent.return_value = item
        item.childCount.return_value = len(item.children)

    def child_at(idx):
        return item.children[idx] if idx < len(item.children) else None

    item.addChild = add_child
    item.child = child_at
    return item


def _make_screen(lib: Path, workflow_name: str) -> LibraryManagerScreen:
    """Build a LibraryManagerScreen with mocked Qt internals."""
    screen = LibraryManagerScreen.__new__(LibraryManagerScreen)
    screen._library_root = lib
    screen._tree = MagicMock()
    screen._editor = MagicMock()
    screen._file_label = MagicMock()
    screen._empty_label = MagicMock()
    screen._splitter = MagicMock()
    screen._delete_btn = MagicMock()
    screen._new_btn = MagicMock()

    wf_path = str(lib / "workflows" / workflow_name)
    cat_item = _make_tree_item("Workflows")
    cat_item.parent.return_value = None
    file_item = _make_tree_item(workflow_name, file_path=wf_path, parent=cat_item)
    screen._tree.currentItem.return_value = file_item
    return screen


# ---------------------------------------------------------------------------
# Pure function tests — _build_file_tree with workflows
# ---------------------------------------------------------------------------


class TestBuildFileTreeWorkflows:

    def test_workflows_category_present(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [c["name"] for c in tree]
        assert "Workflows" in names

    def test_workflow_files_listed(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        wf = next(c for c in tree if c["name"] == "Workflows")
        child_names = sorted(c["name"] for c in wf["children"])
        assert child_names == ["deploy.md", "hotfix.md", "release.md"]

    def test_workflow_files_have_paths(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        wf = next(c for c in tree if c["name"] == "Workflows")
        for child in wf["children"]:
            assert child["path"] is not None
            assert child["path"].endswith(".md")

    def test_deleted_workflow_not_listed(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        (lib / "workflows" / "deploy.md").unlink()
        tree = _build_file_tree(lib)
        wf = next(c for c in tree if c["name"] == "Workflows")
        names = [c["name"] for c in wf["children"]]
        assert "deploy.md" not in names
        assert len(names) == 2


# ---------------------------------------------------------------------------
# Workflow delete — button state
# ---------------------------------------------------------------------------


class TestWorkflowDeleteButtonState:

    def test_workflows_in_editable_categories(self):
        assert "Workflows" in _EDITABLE_CATEGORIES

    def test_delete_enabled_for_workflow_file(self):
        """Delete button must be enabled when a workflow file leaf is selected."""
        screen = LibraryManagerScreen.__new__(LibraryManagerScreen)
        screen._library_root = Path("/fake")
        screen._delete_btn = MagicMock()
        screen._new_btn = MagicMock()

        cat_item = _make_tree_item("Workflows")
        cat_item.parent.return_value = None
        file_item = _make_tree_item(
            "deploy.md",
            file_path="/fake/workflows/deploy.md",
            parent=cat_item,
        )

        screen._update_button_state(file_item)
        screen._delete_btn.setEnabled.assert_called_with(True)

    def test_delete_disabled_for_workflow_category_node(self):
        """Delete button must be disabled when the Workflows category is selected."""
        screen = LibraryManagerScreen.__new__(LibraryManagerScreen)
        screen._library_root = Path("/fake")
        screen._delete_btn = MagicMock()
        screen._new_btn = MagicMock()

        cat_item = _make_tree_item("Workflows")
        cat_item.parent.return_value = None

        screen._update_button_state(cat_item)
        screen._delete_btn.setEnabled.assert_called_with(False)

    def test_delete_disabled_when_no_selection(self):
        """Delete button disabled when nothing is selected."""
        screen = LibraryManagerScreen.__new__(LibraryManagerScreen)
        screen._library_root = Path("/fake")
        screen._delete_btn = MagicMock()
        screen._new_btn = MagicMock()

        screen._update_button_state(None)
        screen._delete_btn.setEnabled.assert_called_with(False)


# ---------------------------------------------------------------------------
# Workflow delete — end-to-end file removal
# ---------------------------------------------------------------------------

_MSG_QUESTION = "foundry_app.ui.screens.library_manager.QMessageBox.question"
_MSG_CRITICAL = "foundry_app.ui.screens.library_manager.QMessageBox.critical"


class TestWorkflowDeleteFile:

    def test_confirm_deletes_workflow_from_disk(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        target = lib / "workflows" / "deploy.md"
        assert target.is_file()
        screen = _make_screen(lib, "deploy.md")

        from PySide6.QtWidgets import QMessageBox

        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_cancel_preserves_workflow(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        target = lib / "workflows" / "release.md"
        assert target.is_file()
        screen = _make_screen(lib, "release.md")

        from PySide6.QtWidgets import QMessageBox

        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        assert target.is_file()

    def test_confirmation_dialog_shows_workflow_name(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = _make_screen(lib, "hotfix.md")

        from PySide6.QtWidgets import QMessageBox

        with patch(
            _MSG_QUESTION, return_value=QMessageBox.StandardButton.No
        ) as mock_q:
            screen._on_delete_asset()
        msg_arg = mock_q.call_args[0][2]
        assert "hotfix.md" in msg_arg

    def test_tree_refreshes_after_workflow_delete(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = _make_screen(lib, "deploy.md")

        from PySide6.QtWidgets import QMessageBox

        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        screen._tree.clear.assert_called()

    def test_remaining_workflows_survive_delete(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = _make_screen(lib, "deploy.md")

        from PySide6.QtWidgets import QMessageBox

        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert (lib / "workflows" / "release.md").is_file()
        assert (lib / "workflows" / "hotfix.md").is_file()

    def test_delete_nonexistent_workflow_is_safe(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        (lib / "workflows" / "deploy.md").unlink()
        screen = _make_screen(lib, "deploy.md")

        from PySide6.QtWidgets import QMessageBox

        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()  # should not raise

    def test_delete_refuses_path_outside_library_root(self, tmp_path: Path):
        """Safety guard: refuse to delete if resolved path escapes library root."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen.__new__(LibraryManagerScreen)
        screen._library_root = lib
        screen._tree = MagicMock()
        screen._editor = MagicMock()
        screen._file_label = MagicMock()
        screen._empty_label = MagicMock()
        screen._splitter = MagicMock()
        screen._delete_btn = MagicMock()
        screen._new_btn = MagicMock()

        outside = tmp_path / "outside.md"
        outside.write_text("should not be deleted", encoding="utf-8")
        cat_item = _make_tree_item("Workflows")
        cat_item.parent.return_value = None
        file_item = _make_tree_item(
            "outside.md", file_path=str(outside), parent=cat_item
        )
        screen._tree.currentItem.return_value = file_item

        from PySide6.QtWidgets import QMessageBox

        with (
            patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes),
            patch(_MSG_CRITICAL) as mock_crit,
        ):
            screen._on_delete_asset()
        assert outside.is_file(), "File outside library root must not be deleted"
        mock_crit.assert_called_once()


# ---------------------------------------------------------------------------
# Workflow delete — tree state after deletion
# ---------------------------------------------------------------------------


class TestWorkflowDeleteTreeState:

    def test_build_tree_reflects_deletion(self, tmp_path: Path):
        """After deleting a workflow file, _build_file_tree must not list it."""
        lib = _create_library(tmp_path)
        (lib / "workflows" / "deploy.md").unlink()
        tree = _build_file_tree(lib)
        wf = next(c for c in tree if c["name"] == "Workflows")
        names = [c["name"] for c in wf["children"]]
        assert "deploy.md" not in names
        assert "release.md" in names
        assert "hotfix.md" in names

    def test_empty_workflows_after_all_deleted(self, tmp_path: Path):
        """Deleting all workflow files leaves an empty children list."""
        lib = _create_library(tmp_path)
        shutil.rmtree(lib / "workflows")
        (lib / "workflows").mkdir()
        tree = _build_file_tree(lib)
        wf = next(c for c in tree if c["name"] == "Workflows")
        assert wf["children"] == []
