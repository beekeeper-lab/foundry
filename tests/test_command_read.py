"""Tests for BEAN-097: Library Manager — Command Read.

Verifies that commands from the library are correctly listed in the
navigation tree and can be loaded into the markdown editor.

Uses sys.modules mocking to bypass PySide6 libGL.so.1 dependency so
the pure tree-building logic can be tested without a display server.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PySide6 modules before importing library_manager
# ---------------------------------------------------------------------------
_MOCKED: dict[str, MagicMock] = {}
for _mod in ("PySide6", "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets"):
    if _mod not in sys.modules:
        _MOCKED[_mod] = MagicMock()
        sys.modules[_mod] = _MOCKED[_mod]

# Now we can safely import the pure-logic helpers
from foundry_app.ui.screens.library_manager import (  # noqa: E402
    _build_file_tree,
    starter_content,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_command_library(root: Path) -> Path:
    """Create a minimal library with several command files."""
    lib = root / "test-library"
    cmd_dir = lib / "claude" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "review-pr.md").write_text("# /review-pr Command\n\nReview a PR.", encoding="utf-8")
    (cmd_dir / "deploy-app.md").write_text("# /deploy-app Command\n\nDeploy.", encoding="utf-8")
    (cmd_dir / "run-tests.md").write_text("# /run-tests Command\n\nRun tests.", encoding="utf-8")
    return lib


def _create_nested_command_library(root: Path) -> Path:
    """Create a library with nested command directories."""
    lib = root / "test-library"
    cmd_dir = lib / "claude" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "review-pr.md").write_text("# /review-pr Command", encoding="utf-8")
    sub_dir = cmd_dir / "ops"
    sub_dir.mkdir()
    (sub_dir / "scale-up.md").write_text("# /scale-up Command", encoding="utf-8")
    (sub_dir / "rollback.md").write_text("# /rollback Command", encoding="utf-8")
    return lib


def _find_category(tree: list[dict], name: str) -> dict | None:
    """Find a category node by display name in the tree."""
    for cat in tree:
        if cat["name"] == name:
            return cat
    return None


def _collect_file_paths(node: dict) -> list[str]:
    """Recursively collect all file paths from a tree node."""
    paths: list[str] = []
    if node.get("path"):
        paths.append(node["path"])
    for child in node.get("children", []):
        paths.extend(_collect_file_paths(child))
    return paths


def _collect_names(children: list[dict]) -> list[str]:
    """Collect names from a list of tree children."""
    return [c["name"] for c in children]


# ---------------------------------------------------------------------------
# Tree building — command category
# ---------------------------------------------------------------------------


class TestCommandTreeBuilding:
    """Verify _build_file_tree correctly populates the Claude Commands category."""

    def test_commands_category_present(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        assert cat is not None

    def test_all_command_files_listed(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        names = _collect_names(cat["children"])
        assert "review-pr.md" in names
        assert "deploy-app.md" in names
        assert "run-tests.md" in names

    def test_command_file_count(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        assert len(cat["children"]) == 3

    def test_command_files_have_paths(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        for child in cat["children"]:
            assert child["path"] is not None
            assert child["path"].endswith(".md")

    def test_command_file_path_is_absolute(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        for child in cat["children"]:
            assert Path(child["path"]).is_absolute()

    def test_command_files_are_sorted(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        names = _collect_names(cat["children"])
        assert names == sorted(names)

    def test_command_file_is_readable(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        for child in cat["children"]:
            path = Path(child["path"])
            assert path.is_file()
            content = path.read_text(encoding="utf-8")
            assert len(content) > 0

    def test_command_file_content_matches(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        review = next(c for c in cat["children"] if c["name"] == "review-pr.md")
        content = Path(review["path"]).read_text(encoding="utf-8")
        assert "# /review-pr Command" in content

    def test_empty_commands_dir(self, tmp_path: Path):
        lib = tmp_path / "empty-lib"
        (lib / "claude" / "commands").mkdir(parents=True)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        assert cat is not None
        assert cat["children"] == []

    def test_missing_commands_dir(self, tmp_path: Path):
        lib = tmp_path / "no-commands-lib"
        lib.mkdir()
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        assert cat is not None
        assert cat["children"] == []

    def test_hidden_command_files_excluded(self, tmp_path: Path):
        lib = tmp_path / "hidden-lib"
        cmd_dir = lib / "claude" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / ".hidden-cmd.md").write_text("# Hidden", encoding="utf-8")
        (cmd_dir / "visible-cmd.md").write_text("# Visible", encoding="utf-8")
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        names = _collect_names(cat["children"])
        assert ".hidden-cmd.md" not in names
        assert "visible-cmd.md" in names


# ---------------------------------------------------------------------------
# Nested command directories
# ---------------------------------------------------------------------------


class TestNestedCommandTree:
    """Verify commands in subdirectories appear correctly."""

    def test_nested_dir_appears(self, tmp_path: Path):
        lib = _create_nested_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        names = _collect_names(cat["children"])
        assert "ops" in names
        assert "review-pr.md" in names

    def test_nested_dir_has_no_path(self, tmp_path: Path):
        lib = _create_nested_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        ops_dir = next(c for c in cat["children"] if c["name"] == "ops")
        assert ops_dir["path"] is None

    def test_nested_files_have_paths(self, tmp_path: Path):
        lib = _create_nested_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        ops_dir = next(c for c in cat["children"] if c["name"] == "ops")
        for child in ops_dir["children"]:
            assert child["path"] is not None
            assert Path(child["path"]).is_file()

    def test_nested_file_count(self, tmp_path: Path):
        lib = _create_nested_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        ops_dir = next(c for c in cat["children"] if c["name"] == "ops")
        assert len(ops_dir["children"]) == 2

    def test_all_file_paths_collected(self, tmp_path: Path):
        lib = _create_nested_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        all_paths = _collect_file_paths(cat)
        assert len(all_paths) == 3  # review-pr.md + ops/scale-up.md + ops/rollback.md


# ---------------------------------------------------------------------------
# Starter content for commands
# ---------------------------------------------------------------------------


class TestCommandStarterContent:
    """Verify starter_content produces correct markdown for commands."""

    def test_command_template_has_name(self):
        content = starter_content("Claude Commands", "deploy-app")
        assert "/deploy-app" in content

    def test_command_template_has_sections(self):
        content = starter_content("Claude Commands", "my-cmd")
        assert "## Purpose" in content
        assert "## Usage" in content
        assert "## Inputs" in content
        assert "## Process" in content
        assert "## Output" in content

    def test_command_template_has_usage_block(self):
        content = starter_content("Claude Commands", "run-tests")
        assert "/run-tests" in content
        assert "```" in content


# ---------------------------------------------------------------------------
# File readability verification
# ---------------------------------------------------------------------------


class TestCommandFileReadability:
    """Verify command files can be read back correctly (simulates editor load)."""

    def test_read_command_content(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        for child in cat["children"]:
            path = Path(child["path"])
            content = path.read_text(encoding="utf-8")
            assert content.startswith("#")

    def test_command_path_resolves_correctly(self, tmp_path: Path):
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        review = next(c for c in cat["children"] if c["name"] == "review-pr.md")
        expected = lib / "claude" / "commands" / "review-pr.md"
        assert Path(review["path"]).resolve() == expected.resolve()

    def test_file_path_label_would_show_path(self, tmp_path: Path):
        """The file label displays str(path) — verify that's meaningful."""
        lib = _create_command_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        review = next(c for c in cat["children"] if c["name"] == "review-pr.md")
        label_text = str(Path(review["path"]))
        assert "review-pr.md" in label_text
        assert "claude" in label_text
        assert "commands" in label_text

    def test_single_command_library(self, tmp_path: Path):
        """Library with just one command file still works."""
        lib = tmp_path / "one-cmd-lib"
        cmd_dir = lib / "claude" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "solo.md").write_text("# Solo command", encoding="utf-8")
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        assert len(cat["children"]) == 1
        assert cat["children"][0]["name"] == "solo.md"
        content = Path(cat["children"][0]["path"]).read_text(encoding="utf-8")
        assert "Solo command" in content

    def test_many_commands(self, tmp_path: Path):
        """Library with many commands lists all of them."""
        lib = tmp_path / "many-cmds-lib"
        cmd_dir = lib / "claude" / "commands"
        cmd_dir.mkdir(parents=True)
        for i in range(20):
            (cmd_dir / f"cmd-{i:03d}.md").write_text(
                f"# Command {i}", encoding="utf-8"
            )
        tree = _build_file_tree(lib)
        cat = _find_category(tree, "Claude Commands")
        assert len(cat["children"]) == 20
