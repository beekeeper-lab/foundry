"""Tests for Stack Read functionality — BEAN-085.

Pure-logic tests for _build_file_tree / _scan_dir applied to stacks.
These tests verify that the tree data structure is built correctly
without requiring PySide6/Qt (no libGL dependency).

PySide6 modules are mocked out so the pure-Python helpers can be imported
in environments where libGL.so.1 is unavailable.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PySide6 so we can import the pure-logic helpers from library_manager.
# ---------------------------------------------------------------------------
_PYSIDE6_MODULES = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "mistune",
]
_saved: dict[str, ModuleType | None] = {}

for _mod in _PYSIDE6_MODULES:
    _saved[_mod] = sys.modules.get(_mod)
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

from foundry_app.ui.screens.library_manager import _build_file_tree  # noqa: E402

# Restore any previously-loaded real modules so we don't poison other tests.
for _mod, _prev in _saved.items():
    if _prev is None:
        sys.modules.pop(_mod, None)
    else:
        sys.modules[_mod] = _prev


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_stack_library(root: Path) -> Path:
    """Create a library with multiple stacks for testing."""
    lib = root / "test-library"

    # Stack 1: python-fastapi with 3 files
    s1 = lib / "stacks" / "python-fastapi"
    s1.mkdir(parents=True)
    (s1 / "conventions.md").write_text("# Python FastAPI Conventions", encoding="utf-8")
    (s1 / "testing.md").write_text("# Testing Guide", encoding="utf-8")
    (s1 / "security.md").write_text("# Security Guide", encoding="utf-8")

    # Stack 2: react with 2 files
    s2 = lib / "stacks" / "react"
    s2.mkdir(parents=True)
    (s2 / "conventions.md").write_text("# React Conventions", encoding="utf-8")
    (s2 / "performance.md").write_text("# Performance Tips", encoding="utf-8")

    # Stack 3: empty stack directory (no files)
    s3 = lib / "stacks" / "empty-stack"
    s3.mkdir(parents=True)

    return lib


# ---------------------------------------------------------------------------
# Tests: Tree structure for stacks
# ---------------------------------------------------------------------------


class TestStackTreeStructure:
    """Verify _build_file_tree returns correct structure for stacks."""

    def test_stacks_category_present(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        cat_names = [c["name"] for c in tree]
        assert "Stacks" in cat_names

    def test_all_stacks_listed(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        stack_names = sorted(c["name"] for c in stacks["children"])
        assert stack_names == ["empty-stack", "python-fastapi", "react"]

    def test_stack_directories_have_no_path(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        for stack_dir in stacks["children"]:
            assert stack_dir["path"] is None, (
                f"Stack dir '{stack_dir['name']}' should have path=None"
            )

    def test_stack_files_have_paths(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        pf = next(c for c in stacks["children"] if c["name"] == "python-fastapi")
        for f in pf["children"]:
            assert f["path"] is not None
            assert f["path"].endswith(".md")

    def test_stack_file_paths_are_absolute(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        pf = next(c for c in stacks["children"] if c["name"] == "python-fastapi")
        for f in pf["children"]:
            assert Path(f["path"]).is_absolute()

    def test_stack_file_count(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        pf = next(c for c in stacks["children"] if c["name"] == "python-fastapi")
        assert len(pf["children"]) == 3

    def test_react_stack_files(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        react = next(c for c in stacks["children"] if c["name"] == "react")
        file_names = sorted(c["name"] for c in react["children"])
        assert file_names == ["conventions.md", "performance.md"]

    def test_empty_stack_has_no_children(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        empty = next(c for c in stacks["children"] if c["name"] == "empty-stack")
        assert empty["children"] == []

    def test_no_stacks_dir_gives_empty_children(self, tmp_path: Path):
        lib = tmp_path / "bare-lib"
        lib.mkdir()
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        assert stacks["children"] == []

    def test_hidden_files_excluded_from_stacks(self, tmp_path: Path):
        lib = tmp_path / "lib"
        sd = lib / "stacks" / "mystack"
        sd.mkdir(parents=True)
        (sd / ".hidden").write_text("hidden", encoding="utf-8")
        (sd / "visible.md").write_text("visible", encoding="utf-8")
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        mystack = stacks["children"][0]
        file_names = [c["name"] for c in mystack["children"]]
        assert ".hidden" not in file_names
        assert "visible.md" in file_names

    def test_stacks_sorted_alphabetically(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        names = [c["name"] for c in stacks["children"]]
        assert names == sorted(names)

    def test_files_within_stack_sorted_alphabetically(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        pf = next(c for c in stacks["children"] if c["name"] == "python-fastapi")
        file_names = [c["name"] for c in pf["children"]]
        assert file_names == sorted(file_names)

    def test_stack_file_points_to_correct_content(self, tmp_path: Path):
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        pf = next(c for c in stacks["children"] if c["name"] == "python-fastapi")
        conv = next(c for c in pf["children"] if c["name"] == "conventions.md")
        path = Path(conv["path"])
        assert path.is_file()
        content = path.read_text(encoding="utf-8")
        assert "Python FastAPI Conventions" in content

    def test_file_content_readable_from_tree_path(self, tmp_path: Path):
        """Simulate what the UI does: read file content via the path in the tree."""
        lib = _create_stack_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        react = next(c for c in stacks["children"] if c["name"] == "react")
        perf = next(c for c in react["children"] if c["name"] == "performance.md")
        path = Path(perf["path"])
        assert path.is_file()
        content = path.read_text(encoding="utf-8")
        assert "Performance Tips" in content

    def test_nonexistent_library_returns_empty(self, tmp_path: Path):
        tree = _build_file_tree(tmp_path / "nonexistent")
        assert tree == []
