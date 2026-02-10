"""Workflow read tests for Library Manager (BEAN-093).

Verifies that workflows are listed in the tree and can be read/viewed.
Mocks PySide6 to run in environments without libGL.so.1.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PySide6 + mistune so we can import the pure-logic functions from
# library_manager without requiring libGL.so.1 (unavailable in CI).
# ---------------------------------------------------------------------------
_QT_MOCKS: dict[str, MagicMock] = {}
for _mod_name in (
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "mistune",
):
    if _mod_name not in sys.modules:
        _QT_MOCKS[_mod_name] = MagicMock()
        sys.modules[_mod_name] = _QT_MOCKS[_mod_name]

from foundry_app.ui.screens.library_manager import (  # noqa: E402
    LIBRARY_CATEGORIES,
    _build_file_tree,
    _scan_dir,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_workflow_library(root: Path) -> Path:
    """Create a library with multiple workflows for testing."""
    lib = root / "test-library"
    wf_dir = lib / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "release-process.md").write_text(
        "# Release Process\n\n## Steps\n\n1. Tag release\n2. Build\n3. Deploy",
        encoding="utf-8",
    )
    (wf_dir / "code-review.md").write_text(
        "# Code Review\n\n## Checklist\n\n- Tests pass\n- Lint clean",
        encoding="utf-8",
    )
    # Nested workflow directory
    sub_dir = wf_dir / "onboarding"
    sub_dir.mkdir()
    (sub_dir / "day-1.md").write_text("# Day 1 Onboarding", encoding="utf-8")

    # Create minimal dirs for other categories so _build_file_tree works
    (lib / "personas").mkdir(parents=True, exist_ok=True)
    (lib / "stacks").mkdir(parents=True, exist_ok=True)
    (lib / "templates").mkdir(parents=True, exist_ok=True)
    (lib / "claude" / "commands").mkdir(parents=True, exist_ok=True)
    (lib / "claude" / "skills").mkdir(parents=True, exist_ok=True)
    (lib / "claude" / "hooks").mkdir(parents=True, exist_ok=True)

    return lib


# ---------------------------------------------------------------------------
# Workflow tree building
# ---------------------------------------------------------------------------


class TestWorkflowTreeBuilding:
    """Verify workflows populate the tree data structure correctly."""

    def test_workflows_category_present(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [cat["name"] for cat in tree]
        assert "Workflows" in names

    def test_all_workflow_files_listed(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        child_names = [c["name"] for c in workflows["children"]]
        assert "code-review.md" in child_names
        assert "release-process.md" in child_names

    def test_workflow_file_has_path(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        release = next(
            c for c in workflows["children"] if c["name"] == "release-process.md"
        )
        assert release["path"] is not None
        assert release["path"].endswith("release-process.md")

    def test_workflow_file_path_is_readable(self, tmp_path: Path):
        """Each file node's path points to a real, non-empty file."""
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        for child in workflows["children"]:
            if child.get("path"):
                p = Path(child["path"])
                assert p.is_file()
                content = p.read_text(encoding="utf-8")
                assert len(content) > 0

    def test_workflow_content_matches_written(self, tmp_path: Path):
        """Verify the content from a tree path matches what was written."""
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        release = next(
            c for c in workflows["children"] if c["name"] == "release-process.md"
        )
        content = Path(release["path"]).read_text(encoding="utf-8")
        assert "# Release Process" in content
        assert "## Steps" in content

    def test_nested_workflow_directory(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        onboarding = next(
            (c for c in workflows["children"] if c["name"] == "onboarding"), None
        )
        assert onboarding is not None
        assert onboarding["path"] is None  # directory node
        assert len(onboarding["children"]) == 1
        assert onboarding["children"][0]["name"] == "day-1.md"

    def test_nested_workflow_file_has_path(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        onboarding = next(c for c in workflows["children"] if c["name"] == "onboarding")
        day1 = onboarding["children"][0]
        assert day1["path"] is not None
        assert day1["path"].endswith("day-1.md")
        assert Path(day1["path"]).is_file()

    def test_empty_workflows_dir(self, tmp_path: Path):
        lib = tmp_path / "empty-lib"
        (lib / "workflows").mkdir(parents=True)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        assert workflows["children"] == []

    def test_hidden_workflow_files_skipped(self, tmp_path: Path):
        lib = tmp_path / "lib"
        wf = lib / "workflows"
        wf.mkdir(parents=True)
        (wf / ".hidden-workflow.md").write_text("hidden", encoding="utf-8")
        (wf / "visible.md").write_text("visible", encoding="utf-8")
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        names = [c["name"] for c in workflows["children"]]
        assert ".hidden-workflow.md" not in names
        assert "visible.md" in names

    def test_workflows_sorted_alphabetically(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        names = [c["name"] for c in workflows["children"]]
        assert names == sorted(names)

    def test_missing_workflows_dir_gives_empty_children(self, tmp_path: Path):
        """A library with no workflows/ dir still has the category (empty)."""
        lib = tmp_path / "no-wf-lib"
        (lib / "personas").mkdir(parents=True)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        assert workflows["children"] == []


# ---------------------------------------------------------------------------
# _scan_dir for workflow directories
# ---------------------------------------------------------------------------


class TestScanDirWorkflows:
    """Test _scan_dir specifically for workflow-shaped directories."""

    def test_scan_flat_workflow_dir(self, tmp_path: Path):
        wf_dir = tmp_path / "workflows"
        wf_dir.mkdir()
        (wf_dir / "alpha.md").write_text("a", encoding="utf-8")
        (wf_dir / "beta.md").write_text("b", encoding="utf-8")
        children = _scan_dir(wf_dir)
        assert len(children) == 2
        assert children[0]["name"] == "alpha.md"
        assert children[1]["name"] == "beta.md"

    def test_scan_nested_workflow_dir(self, tmp_path: Path):
        wf_dir = tmp_path / "workflows"
        (wf_dir / "sub").mkdir(parents=True)
        (wf_dir / "sub" / "nested.md").write_text("nested", encoding="utf-8")
        (wf_dir / "top.md").write_text("top", encoding="utf-8")
        children = _scan_dir(wf_dir)
        sub = next(c for c in children if c["name"] == "sub")
        assert sub["path"] is None
        assert len(sub["children"]) == 1
        assert sub["children"][0]["name"] == "nested.md"
        assert sub["children"][0]["path"] is not None

    def test_scan_dir_file_children_have_empty_children_list(self, tmp_path: Path):
        wf_dir = tmp_path / "wf"
        wf_dir.mkdir()
        (wf_dir / "file.md").write_text("content", encoding="utf-8")
        children = _scan_dir(wf_dir)
        assert children[0]["children"] == []


# ---------------------------------------------------------------------------
# LIBRARY_CATEGORIES constant
# ---------------------------------------------------------------------------


class TestLibraryCategories:
    """Ensure workflows are correctly configured in the categories list."""

    def test_workflows_in_categories(self):
        names = [name for name, _path in LIBRARY_CATEGORIES]
        assert "Workflows" in names

    def test_workflows_maps_to_correct_dir(self):
        mapping = dict(LIBRARY_CATEGORIES)
        assert mapping["Workflows"] == "workflows"
