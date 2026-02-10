"""Tests for Library Manager hook read functionality — BEAN-105.

These tests verify that hooks are correctly discovered, listed in the tree,
and their content can be read. Uses sys.modules mocking to avoid the
libGL.so.1 dependency in headless environments.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PySide6 before importing the module under test
# ---------------------------------------------------------------------------

_QT_MODULES = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "mistune",
]

_mocks: dict[str, ModuleType | MagicMock] = {}
for mod_name in _QT_MODULES:
    if mod_name not in sys.modules:
        _mocks[mod_name] = MagicMock()
        sys.modules[mod_name] = _mocks[mod_name]

# Now safe to import the pure-logic parts
from foundry_app.ui.screens.library_manager import (  # noqa: E402
    LIBRARY_CATEGORIES,
    _build_file_tree,
    _scan_dir,
    starter_content,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_hook_library(root: Path) -> Path:
    """Create a library with multiple hooks for testing."""
    lib = root / "test-library"
    hooks_dir = lib / "claude" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit-lint.md").write_text(
        "# Hook Pack: Pre Commit Lint\n\n## Purpose\n\nLint before commit.",
        encoding="utf-8",
    )
    (hooks_dir / "security-scan.md").write_text(
        "# Hook Pack: Security Scan\n\n## Purpose\n\nRun security checks.",
        encoding="utf-8",
    )
    (hooks_dir / "compliance-gate.md").write_text(
        "# Hook Pack: Compliance Gate\n\n## Hooks\n\n| Hook | Trigger |\n|------|---------|",
        encoding="utf-8",
    )
    # Create minimal dirs for other categories so _build_file_tree works
    (lib / "personas").mkdir(parents=True, exist_ok=True)
    (lib / "stacks").mkdir(parents=True, exist_ok=True)
    (lib / "templates").mkdir(parents=True, exist_ok=True)
    (lib / "workflows").mkdir(parents=True, exist_ok=True)
    (lib / "claude" / "commands").mkdir(parents=True, exist_ok=True)
    (lib / "claude" / "skills").mkdir(parents=True, exist_ok=True)
    return lib


# ---------------------------------------------------------------------------
# Hook category in LIBRARY_CATEGORIES
# ---------------------------------------------------------------------------


class TestHookCategoryConfig:

    def test_hooks_category_exists_in_library_categories(self):
        names = [name for name, _ in LIBRARY_CATEGORIES]
        assert "Claude Hooks" in names

    def test_hooks_category_maps_to_correct_path(self):
        for name, rel_path in LIBRARY_CATEGORIES:
            if name == "Claude Hooks":
                assert rel_path == "claude/hooks"
                return
        raise AssertionError("Claude Hooks not found in LIBRARY_CATEGORIES")


# ---------------------------------------------------------------------------
# Tree building — hooks appear correctly
# ---------------------------------------------------------------------------


class TestHookTreeBuilding:

    def test_hooks_category_present_in_tree(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        cat_names = [c["name"] for c in tree]
        assert "Claude Hooks" in cat_names

    def test_all_hooks_listed_as_children(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        names = {c["name"] for c in hooks_cat["children"]}
        assert names == {"pre-commit-lint.md", "security-scan.md", "compliance-gate.md"}

    def test_hook_children_count(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        assert len(hooks_cat["children"]) == 3

    def test_hook_file_nodes_have_paths(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        for child in hooks_cat["children"]:
            assert child["path"] is not None
            assert child["path"].endswith(".md")

    def test_hook_file_nodes_have_no_children(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        for child in hooks_cat["children"]:
            assert child["children"] == []

    def test_hook_file_paths_are_absolute(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        for child in hooks_cat["children"]:
            assert Path(child["path"]).is_absolute()

    def test_hook_file_paths_point_to_existing_files(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        for child in hooks_cat["children"]:
            assert Path(child["path"]).is_file()

    def test_hook_files_sorted_alphabetically(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        names = [c["name"] for c in hooks_cat["children"]]
        assert names == sorted(names)

    def test_empty_hooks_dir_gives_empty_children(self, tmp_path: Path):
        lib = tmp_path / "empty-lib"
        hooks_dir = lib / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        assert hooks_cat["children"] == []

    def test_missing_hooks_dir_gives_empty_children(self, tmp_path: Path):
        lib = tmp_path / "no-hooks-lib"
        lib.mkdir()
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        assert hooks_cat["children"] == []

    def test_hidden_hook_files_excluded(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        hooks_dir = lib / "claude" / "hooks"
        (hooks_dir / ".hidden-hook.md").write_text("hidden", encoding="utf-8")
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        names = {c["name"] for c in hooks_cat["children"]}
        assert ".hidden-hook.md" not in names
        assert len(hooks_cat["children"]) == 3  # only the 3 visible hooks

    def test_single_hook_in_tree(self, tmp_path: Path):
        lib = tmp_path / "single-lib"
        hooks_dir = lib / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "only-hook.md").write_text("# Only Hook", encoding="utf-8")
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        assert len(hooks_cat["children"]) == 1
        assert hooks_cat["children"][0]["name"] == "only-hook.md"


# ---------------------------------------------------------------------------
# Hook file content can be read from paths in tree
# ---------------------------------------------------------------------------


class TestHookFileRead:

    def test_hook_file_content_readable(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        for child in hooks_cat["children"]:
            path = Path(child["path"])
            content = path.read_text(encoding="utf-8")
            assert len(content) > 0

    def test_lint_hook_content(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        hook = next(c for c in hooks_cat["children"] if c["name"] == "pre-commit-lint.md")
        content = Path(hook["path"]).read_text(encoding="utf-8")
        assert "Hook Pack: Pre Commit Lint" in content
        assert "## Purpose" in content

    def test_security_scan_hook_content(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        hook = next(c for c in hooks_cat["children"] if c["name"] == "security-scan.md")
        content = Path(hook["path"]).read_text(encoding="utf-8")
        assert "Security Scan" in content

    def test_compliance_gate_hook_content(self, tmp_path: Path):
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        hook = next(c for c in hooks_cat["children"] if c["name"] == "compliance-gate.md")
        content = Path(hook["path"]).read_text(encoding="utf-8")
        assert "Compliance Gate" in content
        assert "| Hook | Trigger |" in content

    def test_hook_file_path_contains_hooks_dir(self, tmp_path: Path):
        """Verify file path label would show the correct hooks directory."""
        lib = _create_hook_library(tmp_path)
        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        for child in hooks_cat["children"]:
            path_str = child["path"]
            assert "claude" in path_str
            assert "hooks" in path_str


# ---------------------------------------------------------------------------
# _scan_dir handles hooks directory correctly
# ---------------------------------------------------------------------------


class TestScanDirHooks:

    def test_scan_hooks_directory(self, tmp_path: Path):
        hooks_dir = tmp_path / "hooks"
        hooks_dir.mkdir()
        (hooks_dir / "hook-a.md").write_text("a", encoding="utf-8")
        (hooks_dir / "hook-b.md").write_text("b", encoding="utf-8")
        children = _scan_dir(hooks_dir)
        assert len(children) == 2
        names = {c["name"] for c in children}
        assert names == {"hook-a.md", "hook-b.md"}

    def test_scan_hooks_with_nested_dir(self, tmp_path: Path):
        hooks_dir = tmp_path / "hooks"
        hooks_dir.mkdir()
        (hooks_dir / "simple.md").write_text("simple", encoding="utf-8")
        sub = hooks_dir / "pack"
        sub.mkdir()
        (sub / "part1.md").write_text("part1", encoding="utf-8")
        children = _scan_dir(hooks_dir)
        assert len(children) == 2
        dir_node = next(c for c in children if c["name"] == "pack")
        assert dir_node["path"] is None
        assert len(dir_node["children"]) == 1
        assert dir_node["children"][0]["name"] == "part1.md"


# ---------------------------------------------------------------------------
# Hook starter content (for new hook creation — verifies template)
# ---------------------------------------------------------------------------


class TestHookStarterContent:

    def test_hook_starter_has_pack_name(self):
        content = starter_content("Claude Hooks", "pre-commit-lint")
        assert "Hook Pack: Pre Commit Lint" in content

    def test_hook_starter_has_hooks_table(self):
        content = starter_content("Claude Hooks", "my-hook")
        assert "## Hooks" in content
        assert "| Hook Name |" in content

    def test_hook_starter_has_posture_section(self):
        content = starter_content("Claude Hooks", "my-hook")
        assert "## Posture Compatibility" in content

    def test_hook_starter_has_configuration(self):
        content = starter_content("Claude Hooks", "my-hook")
        assert "## Configuration" in content
