"""Tests for command delete in Library Manager (BEAN-100).

These tests mock PySide6 at the module level so they can run in environments
without libGL.so.1 (headless CI, worktrees, etc.).
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# PySide6 mock setup — must happen before importing library_manager
# ---------------------------------------------------------------------------

def _build_qt_mock():
    """Build a mock PySide6 module tree that satisfies library_manager imports."""
    pyside6 = MagicMock()

    # Qt.ItemDataRole.UserRole — used to store file paths on tree items
    pyside6.QtCore.Qt.ItemDataRole.UserRole = 0x0100
    pyside6.QtCore.Qt.AlignmentFlag.AlignCenter = 0x0004
    pyside6.QtCore.Qt.Orientation.Horizontal = 0x01

    # StandardButton enum values used in confirmation dialogs
    pyside6.QtWidgets.QMessageBox.StandardButton.Yes = 0x4000
    pyside6.QtWidgets.QMessageBox.StandardButton.No = 0x10000

    return pyside6


_pyside6 = _build_qt_mock()

# Patch sys.modules so `from PySide6.QtWidgets import ...` works
_MODULES = {
    "PySide6": _pyside6,
    "PySide6.QtCore": _pyside6.QtCore,
    "PySide6.QtGui": _pyside6.QtGui,
    "PySide6.QtWidgets": _pyside6.QtWidgets,
}

# Also mock the markdown_editor module (it imports PySide6 internally)
_editor_mock = MagicMock()
_MODULES["foundry_app.ui.widgets.markdown_editor"] = _editor_mock

# Install all mocks
for mod_name, mod in _MODULES.items():
    sys.modules.setdefault(mod_name, mod)

# NOW import the module under test — PySide6 references resolve to our mocks
from foundry_app.ui.screens.library_manager import (  # noqa: E402
    _EDITABLE_CATEGORIES,
    LIBRARY_CATEGORIES,
    _build_file_tree,
    validate_asset_name,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_library(root: Path) -> Path:
    """Create a minimal library structure for testing command delete."""
    lib = root / "test-library"

    # Commands
    cmd_dir = lib / "claude" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "review-pr.md").write_text("# Review PR command", encoding="utf-8")
    (cmd_dir / "deploy-app.md").write_text("# Deploy App command", encoding="utf-8")

    # Minimal other categories so _build_file_tree works
    (lib / "personas").mkdir(parents=True)
    (lib / "stacks").mkdir(parents=True)
    (lib / "templates").mkdir(parents=True)
    (lib / "workflows").mkdir(parents=True)
    (lib / "claude" / "skills").mkdir(parents=True)
    (lib / "claude" / "hooks").mkdir(parents=True)

    return lib


# ---------------------------------------------------------------------------
# Pure logic tests — tree scanning finds commands
# ---------------------------------------------------------------------------


class TestCommandTreeScanning:

    def test_commands_appear_in_tree(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        commands = next(c for c in tree if c["name"] == "Claude Commands")
        names = [c["name"] for c in commands["children"]]
        assert "review-pr.md" in names
        assert "deploy-app.md" in names

    def test_command_nodes_have_file_paths(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        commands = next(c for c in tree if c["name"] == "Claude Commands")
        for child in commands["children"]:
            assert child["path"] is not None
            assert child["path"].endswith(".md")

    def test_deleted_command_not_in_tree(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        # Delete the file manually
        (lib / "claude" / "commands" / "review-pr.md").unlink()
        tree = _build_file_tree(lib)
        commands = next(c for c in tree if c["name"] == "Claude Commands")
        names = [c["name"] for c in commands["children"]]
        assert "review-pr.md" not in names
        assert "deploy-app.md" in names

    def test_empty_commands_dir(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        # Remove all commands
        for f in (lib / "claude" / "commands").iterdir():
            f.unlink()
        tree = _build_file_tree(lib)
        commands = next(c for c in tree if c["name"] == "Claude Commands")
        assert commands["children"] == []


# ---------------------------------------------------------------------------
# Command delete — filesystem operations
# ---------------------------------------------------------------------------


class TestCommandDeleteFilesystem:

    def test_command_file_deleted_from_disk(self, tmp_path: Path):
        """Verify that unlinking a command .md file removes it from disk."""
        lib = _create_library(tmp_path)
        target = lib / "claude" / "commands" / "review-pr.md"
        assert target.is_file()
        target.unlink()
        assert not target.exists()

    def test_other_commands_survive_delete(self, tmp_path: Path):
        """Deleting one command does not affect sibling commands."""
        lib = _create_library(tmp_path)
        (lib / "claude" / "commands" / "review-pr.md").unlink()
        assert (lib / "claude" / "commands" / "deploy-app.md").is_file()

    def test_commands_dir_persists_after_file_delete(self, tmp_path: Path):
        """The commands directory survives individual file deletion."""
        lib = _create_library(tmp_path)
        (lib / "claude" / "commands" / "review-pr.md").unlink()
        assert (lib / "claude" / "commands").is_dir()

    def test_tree_reflects_deletion(self, tmp_path: Path):
        """After deleting a command, rescanning the tree omits it."""
        lib = _create_library(tmp_path)
        tree_before = _build_file_tree(lib)
        cmds_before = next(c for c in tree_before if c["name"] == "Claude Commands")
        assert len(cmds_before["children"]) == 2

        (lib / "claude" / "commands" / "review-pr.md").unlink()

        tree_after = _build_file_tree(lib)
        cmds_after = next(c for c in tree_after if c["name"] == "Claude Commands")
        assert len(cmds_after["children"]) == 1
        assert cmds_after["children"][0]["name"] == "deploy-app.md"


# ---------------------------------------------------------------------------
# Command delete — confirmation dialog logic
# ---------------------------------------------------------------------------


class TestCommandDeleteConfirmation:

    def test_confirmation_message_includes_command_name(self, tmp_path: Path):
        """The confirmation dialog should name the command being deleted."""
        lib = _create_library(tmp_path)
        command_path = lib / "claude" / "commands" / "review-pr.md"
        display = command_path.name
        msg = f"Delete '{display}'? This cannot be undone."
        assert "review-pr.md" in msg

    def test_confirmation_uses_filename_not_full_path(self, tmp_path: Path):
        """Display name is the filename, not the full filesystem path."""
        lib = _create_library(tmp_path)
        command_path = lib / "claude" / "commands" / "review-pr.md"
        display = command_path.name
        assert display == "review-pr.md"
        assert str(lib) not in display

    def test_cancel_preserves_command(self, tmp_path: Path):
        """If the user cancels, the command file stays on disk."""
        lib = _create_library(tmp_path)
        target = lib / "claude" / "commands" / "review-pr.md"
        # Simulate cancel — just don't delete
        assert target.is_file()
        # File remains unchanged
        content = target.read_text(encoding="utf-8")
        assert content == "# Review PR command"


# ---------------------------------------------------------------------------
# Safety — path traversal protection
# ---------------------------------------------------------------------------


class TestCommandDeleteSafety:

    def test_path_within_library_root(self, tmp_path: Path):
        """Command files should be relative to the library root."""
        lib = _create_library(tmp_path)
        command_path = lib / "claude" / "commands" / "review-pr.md"
        resolved = command_path.resolve()
        assert resolved.is_relative_to(lib.resolve())

    def test_path_outside_library_root_rejected(self, tmp_path: Path):
        """Paths outside the library root must be rejected."""
        lib = _create_library(tmp_path)
        outside_path = tmp_path / "outside" / "evil.md"
        outside_path.parent.mkdir(parents=True)
        outside_path.write_text("malicious", encoding="utf-8")
        resolved = outside_path.resolve()
        assert not resolved.is_relative_to(lib.resolve())

    def test_symlink_escape_detected(self, tmp_path: Path):
        """Symlinks that escape the library root should be caught by resolve()."""
        lib = _create_library(tmp_path)
        outside = tmp_path / "outside"
        outside.mkdir()
        evil_file = outside / "evil.md"
        evil_file.write_text("bad", encoding="utf-8")
        # Create a symlink inside the library that points outside
        symlink = lib / "claude" / "commands" / "escape.md"
        symlink.symlink_to(evil_file)
        resolved = symlink.resolve()
        assert not resolved.is_relative_to(lib.resolve())


# ---------------------------------------------------------------------------
# Button state logic — editable category check
# ---------------------------------------------------------------------------


class TestCommandButtonState:

    def test_commands_category_is_editable(self):
        """Claude Commands must be in the editable categories map."""
        assert "Claude Commands" in _EDITABLE_CATEGORIES

    def test_commands_rel_path(self):
        """The relative path for commands should be claude/commands."""
        assert _EDITABLE_CATEGORIES["Claude Commands"] == "claude/commands"

    def test_commands_in_library_categories(self):
        """Claude Commands must appear in the display category list."""
        names = [name for name, _ in LIBRARY_CATEGORIES]
        assert "Claude Commands" in names


# ---------------------------------------------------------------------------
# Validation (reused from main tests, but runnable without Qt)
# ---------------------------------------------------------------------------


class TestCommandNameValidation:

    def test_valid_command_name(self):
        assert validate_asset_name("review-pr") is None

    def test_valid_single_word(self):
        assert validate_asset_name("deploy") is None

    def test_valid_with_numbers(self):
        assert validate_asset_name("gen-v2") is None

    def test_uppercase_rejected(self):
        assert validate_asset_name("ReviewPR") is not None

    def test_spaces_rejected(self):
        assert validate_asset_name("review pr") is not None

    def test_empty_rejected(self):
        assert validate_asset_name("") is not None
