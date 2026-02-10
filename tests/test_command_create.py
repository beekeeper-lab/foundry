"""Tests for BEAN-098 — command create feature (pure logic, no PySide6/libGL).

We mock out PySide6 so the library_manager module can be imported without
requiring libGL.so.1.
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PySide6 before importing library_manager.
# We use MagicMock as module stand-ins so any attribute access succeeds and
# does not pollute other test modules that may also reference PySide6.
# ---------------------------------------------------------------------------

_qt_mods = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "foundry_app.ui.widgets.markdown_editor",
]
_saved: dict[str, types.ModuleType | None] = {}
for _mod_name in _qt_mods:
    _saved[_mod_name] = sys.modules.get(_mod_name)
    sys.modules[_mod_name] = MagicMock()

# QWidget must be a real type so that LibraryManagerScreen class definition
# (which inherits from QWidget) succeeds.
sys.modules["PySide6.QtWidgets"].QWidget = type(
    "QWidget", (), {"__init__": lambda *a, **kw: None},
)

# NOW it's safe to import the pure logic functions
from foundry_app.ui.screens.library_manager import (  # noqa: E402
    _build_file_tree,
    starter_content,
    validate_asset_name,
)

# Restore sys.modules so PySide6 mocks don't leak into other test modules.
for _mod_name, _orig in _saved.items():
    if _orig is None:
        sys.modules.pop(_mod_name, None)
    else:
        sys.modules[_mod_name] = _orig


def _create_library(root: Path) -> Path:
    """Create a minimal library with a commands directory."""
    lib = root / "test-library"
    (lib / "personas" / "dev").mkdir(parents=True)
    (lib / "personas" / "dev" / "persona.md").write_text("# Dev", encoding="utf-8")
    (lib / "stacks").mkdir(parents=True)
    (lib / "templates").mkdir(parents=True)
    (lib / "workflows").mkdir(parents=True)
    cmd_dir = lib / "claude" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "review-pr.md").write_text("# Review PR", encoding="utf-8")
    (lib / "claude" / "skills" / "handoff").mkdir(parents=True)
    (lib / "claude" / "skills" / "handoff" / "SKILL.md").write_text(
        "# Handoff", encoding="utf-8"
    )
    (lib / "claude" / "hooks").mkdir(parents=True)
    (lib / "claude" / "hooks" / "lint.md").write_text("# Lint", encoding="utf-8")
    return lib


# ---------------------------------------------------------------------------
# Starter content
# ---------------------------------------------------------------------------


class TestCommandStarterContent:

    def test_starter_content_uses_command_template(self):
        content = starter_content("Claude Commands", "deploy-app")
        assert "# /deploy-app Command" in content
        assert "/deploy-app [arguments]" in content

    def test_starter_content_contains_all_sections(self):
        content = starter_content("Claude Commands", "my-cmd")
        assert "## Purpose" in content
        assert "## Usage" in content
        assert "## Inputs" in content
        assert "## Process" in content
        assert "## Output" in content

    def test_starter_content_uses_name_not_title(self):
        """Command names should stay lowercase-hyphen, not title-cased."""
        content = starter_content("Claude Commands", "my-deploy-cmd")
        assert "/my-deploy-cmd" in content
        assert "My Deploy Cmd" not in content


# ---------------------------------------------------------------------------
# Name validation
# ---------------------------------------------------------------------------


class TestCommandNameValidation:

    def test_valid_command_name(self):
        assert validate_asset_name("deploy-app") is None

    def test_valid_single_word(self):
        assert validate_asset_name("deploy") is None

    def test_valid_with_digits(self):
        assert validate_asset_name("v2-deploy") is None

    def test_rejects_uppercase(self):
        assert validate_asset_name("DeployApp") is not None

    def test_rejects_spaces(self):
        assert validate_asset_name("deploy app") is not None

    def test_rejects_underscores(self):
        assert validate_asset_name("deploy_app") is not None

    def test_rejects_empty(self):
        assert validate_asset_name("") is not None

    def test_rejects_too_long(self):
        assert validate_asset_name("a" * 61) is not None

    def test_accepts_max_length(self):
        assert validate_asset_name("a" * 60) is None


# ---------------------------------------------------------------------------
# File creation on disk (simulating the _on_new_asset flow)
# ---------------------------------------------------------------------------


class TestCommandFileCreation:

    def test_create_command_file_on_disk(self, tmp_path: Path):
        """Simulate the create-command flow: write starter content to disk."""
        lib = _create_library(tmp_path)
        name = "my-new-cmd"
        target_dir = lib / "claude" / "commands"
        dest = target_dir / f"{name}.md"

        assert not dest.exists()
        content = starter_content("Claude Commands", name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

        assert dest.is_file()
        written = dest.read_text(encoding="utf-8")
        assert "/my-new-cmd" in written
        assert "## Purpose" in written

    def test_duplicate_detection(self, tmp_path: Path):
        """Duplicate name check: file already exists on disk."""
        lib = _create_library(tmp_path)
        existing = lib / "claude" / "commands" / "review-pr.md"
        assert existing.exists(), "review-pr.md should already exist"

    def test_new_command_appears_in_tree(self, tmp_path: Path):
        """After creating a file, _build_file_tree should include it."""
        lib = _create_library(tmp_path)
        name = "brand-new"
        dest = lib / "claude" / "commands" / f"{name}.md"
        dest.write_text(starter_content("Claude Commands", name), encoding="utf-8")

        tree = _build_file_tree(lib)
        commands_cat = next(c for c in tree if c["name"] == "Claude Commands")
        child_names = [ch["name"] for ch in commands_cat["children"]]
        assert "brand-new.md" in child_names

    def test_new_command_has_file_path_in_tree(self, tmp_path: Path):
        """The tree node for the new command should carry the file path."""
        lib = _create_library(tmp_path)
        name = "path-check"
        dest = lib / "claude" / "commands" / f"{name}.md"
        dest.write_text(starter_content("Claude Commands", name), encoding="utf-8")

        tree = _build_file_tree(lib)
        commands_cat = next(c for c in tree if c["name"] == "Claude Commands")
        node = next(
            ch for ch in commands_cat["children"] if ch["name"] == "path-check.md"
        )
        assert node["path"] == str(dest)

    def test_tree_sorted_after_creation(self, tmp_path: Path):
        """Commands should appear sorted alphabetically in the tree."""
        lib = _create_library(tmp_path)
        for name in ["alpha-cmd", "zebra-cmd"]:
            dest = lib / "claude" / "commands" / f"{name}.md"
            dest.write_text(starter_content("Claude Commands", name), encoding="utf-8")

        tree = _build_file_tree(lib)
        commands_cat = next(c for c in tree if c["name"] == "Claude Commands")
        names = [ch["name"] for ch in commands_cat["children"]]
        assert names == sorted(names)
        assert "alpha-cmd.md" in names
        assert "review-pr.md" in names
        assert "zebra-cmd.md" in names
