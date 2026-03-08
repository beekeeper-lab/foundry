"""Tests for BEAN-108: Library Manager — Hook Delete.

Verifies that selecting a hook enables the Delete button, the confirmation
dialog names the hook, confirming deletes the file from disk, the tree
refreshes, and cancelling preserves the hook.

These tests use mocks for QMessageBox to avoid needing a live display server.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QMessageBox

from foundry_app.ui.screens.library_manager import (
    LibraryManagerScreen,
    _build_file_tree,
)

pytestmark = pytest.mark.usefixtures("qapp")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MSG_QUESTION = "foundry_app.ui.screens.library_manager.QMessageBox.question"


def _create_hook_library(root: Path) -> Path:
    """Create a minimal library with multiple hooks for testing."""
    lib = root / "test-library"
    hooks_dir = lib / "claude" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit-lint.md").write_text(
        "# Hook Pack: Pre Commit Lint\n\nLint hook.", encoding="utf-8"
    )
    (hooks_dir / "security-scan.md").write_text(
        "# Hook Pack: Security Scan\n\nSecurity hook.", encoding="utf-8"
    )
    (hooks_dir / "post-deploy-notify.md").write_text(
        "# Hook Pack: Post Deploy Notify\n\nNotify hook.", encoding="utf-8"
    )
    # Need at least one other category for the tree structure
    (lib / "personas").mkdir(parents=True)
    (lib / "stacks").mkdir(parents=True)
    (lib / "templates").mkdir(parents=True)
    (lib / "workflows").mkdir(parents=True)
    (lib / "claude" / "commands").mkdir(parents=True)
    (lib / "claude" / "skills").mkdir(parents=True)
    return lib


def _find_hooks_category(screen: LibraryManagerScreen):
    """Find the 'Claude Hooks' top-level tree item."""
    for i in range(screen.tree.topLevelItemCount()):
        item = screen.tree.topLevelItem(i)
        if item.text(0) == "Claude Hooks":
            return item
    return None


def _find_hook_child(hooks_item, name: str):
    """Find a child item by name under the hooks category."""
    for i in range(hooks_item.childCount()):
        child = hooks_item.child(i)
        if child.text(0) == name:
            return child
    return None


# ---------------------------------------------------------------------------
# Pure logic: hooks appear in file tree
# ---------------------------------------------------------------------------


class TestHooksInFileTree:

    def test_hooks_category_exists(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks = next((c for c in tree if c["name"] == "Claude Hooks"), None)
        assert hooks is not None

    def test_hook_files_appear_as_children(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks = next(c for c in tree if c["name"] == "Claude Hooks")
        names = [child["name"] for child in hooks["children"]]
        assert "pre-commit-lint.md" in names
        assert "security-scan.md" in names
        assert "post-deploy-notify.md" in names

    def test_hook_files_have_paths(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks = next(c for c in tree if c["name"] == "Claude Hooks")
        for child in hooks["children"]:
            assert child["path"] is not None
            assert child["path"].endswith(".md")


# ---------------------------------------------------------------------------
# Button state: Delete enabled when hook selected
# ---------------------------------------------------------------------------


class TestHookDeleteButtonState:

    def test_delete_enabled_when_hook_file_selected(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        assert hooks_item is not None
        assert hooks_item.childCount() == 3
        screen.tree.setCurrentItem(hooks_item.child(0))
        assert screen.delete_button.isEnabled()

    def test_delete_disabled_for_hooks_category_node(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        screen.tree.setCurrentItem(hooks_item)
        assert not screen.delete_button.isEnabled()

    def test_delete_enabled_for_each_hook(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        for i in range(hooks_item.childCount()):
            screen.tree.setCurrentItem(hooks_item.child(i))
            assert screen.delete_button.isEnabled(), (
                f"Delete should be enabled for hook '{hooks_item.child(i).text(0)}'"
            )

    def test_new_enabled_when_hook_selected(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        screen.tree.setCurrentItem(hooks_item.child(0))
        assert screen.new_button.isEnabled()


# ---------------------------------------------------------------------------
# Delete confirm: file removed from disk
# ---------------------------------------------------------------------------


class TestHookDeleteConfirm:

    def test_confirm_deletes_hook_file(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "claude" / "hooks" / "pre-commit-lint.md"
        assert target.is_file()
        hooks_item = _find_hooks_category(screen)
        child = _find_hook_child(hooks_item, "pre-commit-lint.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_confirm_deletes_second_hook(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "claude" / "hooks" / "security-scan.md"
        assert target.is_file()
        hooks_item = _find_hooks_category(screen)
        child = _find_hook_child(hooks_item, "security-scan.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_other_hooks_preserved_after_delete(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        child = _find_hook_child(hooks_item, "pre-commit-lint.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        # Other hooks should still exist
        assert (lib / "claude" / "hooks" / "security-scan.md").is_file()
        assert (lib / "claude" / "hooks" / "post-deploy-notify.md").is_file()


# ---------------------------------------------------------------------------
# Delete cancel: hook preserved
# ---------------------------------------------------------------------------


class TestHookDeleteCancel:

    def test_cancel_preserves_hook(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "claude" / "hooks" / "pre-commit-lint.md"
        hooks_item = _find_hooks_category(screen)
        child = _find_hook_child(hooks_item, "pre-commit-lint.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        assert target.is_file()

    def test_cancel_preserves_all_hooks(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        child = _find_hook_child(hooks_item, "security-scan.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        assert (lib / "claude" / "hooks" / "pre-commit-lint.md").is_file()
        assert (lib / "claude" / "hooks" / "security-scan.md").is_file()
        assert (lib / "claude" / "hooks" / "post-deploy-notify.md").is_file()


# ---------------------------------------------------------------------------
# Confirmation dialog names the hook
# ---------------------------------------------------------------------------


class TestHookDeleteConfirmationDialog:

    def test_dialog_names_the_hook(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        child = _find_hook_child(hooks_item, "pre-commit-lint.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No) as mock_q:
            screen._on_delete_asset()
        mock_q.assert_called_once()
        msg = mock_q.call_args[0][2]
        assert "pre-commit-lint.md" in msg

    def test_dialog_names_different_hook(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        child = _find_hook_child(hooks_item, "security-scan.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No) as mock_q:
            screen._on_delete_asset()
        msg = mock_q.call_args[0][2]
        assert "security-scan.md" in msg

    def test_dialog_title_is_confirm_delete(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        screen.tree.setCurrentItem(hooks_item.child(0))
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No) as mock_q:
            screen._on_delete_asset()
        title = mock_q.call_args[0][1]
        assert title == "Confirm Delete"


# ---------------------------------------------------------------------------
# Tree refresh after delete
# ---------------------------------------------------------------------------


class TestHookDeleteTreeRefresh:

    def test_tree_refreshes_after_hook_delete(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        assert hooks_item.childCount() == 3
        child = _find_hook_child(hooks_item, "pre-commit-lint.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        # Re-find after refresh
        hooks_item = _find_hooks_category(screen)
        assert hooks_item.childCount() == 2

    def test_deleted_hook_absent_from_tree(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        child = _find_hook_child(hooks_item, "security-scan.md")
        screen.tree.setCurrentItem(child)
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        hooks_item = _find_hooks_category(screen)
        child_names = [
            hooks_item.child(i).text(0) for i in range(hooks_item.childCount())
        ]
        assert "security-scan.md" not in child_names
        assert "pre-commit-lint.md" in child_names
        assert "post-deploy-notify.md" in child_names

    def test_delete_all_hooks_leaves_empty_category(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hook_names = ["pre-commit-lint.md", "security-scan.md", "post-deploy-notify.md"]
        for name in hook_names:
            hooks_item = _find_hooks_category(screen)
            child = _find_hook_child(hooks_item, name)
            screen.tree.setCurrentItem(child)
            with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
                screen._on_delete_asset()
        hooks_item = _find_hooks_category(screen)
        assert hooks_item.childCount() == 0

    def test_cancel_does_not_change_tree_count(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        hooks_item = _find_hooks_category(screen)
        before = hooks_item.childCount()
        screen.tree.setCurrentItem(hooks_item.child(0))
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        hooks_item = _find_hooks_category(screen)
        assert hooks_item.childCount() == before
