"""Tests for BEAN-101: Library Manager — Skill Read.

Validates that skills from the library are correctly listed in the tree
and that selecting a skill file loads its content into the editor.

These tests mock PySide6 so they can run without libGL.so.1.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock PySide6 before importing library_manager (needs libGL.so.1 at import)
for _mod in [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "mistune",
    "foundry_app.ui.theme",
    "foundry_app.ui.widgets.markdown_editor",
]:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

from foundry_app.ui.screens.library_manager import (  # noqa: E402
    LIBRARY_CATEGORIES,
    _build_file_tree,
    _scan_dir,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_skill_library(root: Path, skill_names: list[str] | None = None) -> Path:
    """Create a library with skills for testing.

    Each skill is a directory under claude/skills/ containing a SKILL.md file.
    """
    lib = root / "test-library"
    skills_dir = lib / "claude" / "skills"
    skills_dir.mkdir(parents=True)

    if skill_names is None:
        skill_names = ["handoff", "review-pr", "deploy-app"]

    for name in skill_names:
        skill_dir = skills_dir / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"# Skill: {name.replace('-', ' ').title()}\n\nSkill content for {name}.",
            encoding="utf-8",
        )

    return lib


def _create_full_library(root: Path) -> Path:
    """Create a complete library with all category types for testing."""
    lib = root / "full-library"

    # Skills
    for name in ["handoff", "review-pr", "scaffold-project"]:
        skill_dir = lib / "claude" / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"# Skill: {name.replace('-', ' ').title()}\n\nDescription.",
            encoding="utf-8",
        )

    # Other categories (minimal, just to ensure they exist)
    (lib / "personas" / "dev").mkdir(parents=True)
    (lib / "personas" / "dev" / "persona.md").write_text("# Dev", encoding="utf-8")
    (lib / "stacks").mkdir(parents=True)
    (lib / "templates").mkdir(parents=True)
    (lib / "workflows").mkdir(parents=True)
    (lib / "workflows" / "default.md").write_text("# Default", encoding="utf-8")
    (lib / "claude" / "commands").mkdir(parents=True)
    (lib / "claude" / "commands" / "review-pr.md").write_text("# RP", encoding="utf-8")
    (lib / "claude" / "hooks").mkdir(parents=True)

    return lib


def _get_category(tree: list[dict], name: str) -> dict | None:
    """Find a category by name in the tree output."""
    for cat in tree:
        if cat["name"] == name:
            return cat
    return None


def _find_node(children: list[dict], name: str) -> dict | None:
    """Find a child node by name."""
    for child in children:
        if child["name"] == name:
            return child
    return None


def _collect_leaf_paths(children: list[dict]) -> list[str]:
    """Recursively collect all leaf node paths from a tree."""
    paths: list[str] = []
    for child in children:
        if child.get("path"):
            paths.append(child["path"])
        if child.get("children"):
            paths.extend(_collect_leaf_paths(child["children"]))
    return paths


def _collect_all_names(children: list[dict]) -> list[str]:
    """Recursively collect all node names from a tree."""
    names: list[str] = []
    for child in children:
        names.append(child["name"])
        if child.get("children"):
            names.extend(_collect_all_names(child["children"]))
    return names


# ---------------------------------------------------------------------------
# Test: Skills category appears in tree
# ---------------------------------------------------------------------------


class TestSkillCategoryInTree:
    """Verify the Claude Skills category is present in the tree structure."""

    def test_skills_category_exists(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        assert cat is not None, "Claude Skills category missing from tree"

    def test_skills_category_position(self, tmp_path: Path):
        """Skills should appear at the position defined in LIBRARY_CATEGORIES."""
        lib = _create_full_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [cat["name"] for cat in tree]
        expected_names = [name for name, _ in LIBRARY_CATEGORIES]
        assert names == expected_names

    def test_empty_skills_dir_has_no_children(self, tmp_path: Path):
        lib = tmp_path / "lib"
        (lib / "claude" / "skills").mkdir(parents=True)
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        assert cat is not None
        assert cat["children"] == []

    def test_missing_skills_dir_has_empty_children(self, tmp_path: Path):
        lib = tmp_path / "lib"
        lib.mkdir()
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        assert cat is not None
        assert cat["children"] == []


# ---------------------------------------------------------------------------
# Test: All skills listed when category is expanded
# ---------------------------------------------------------------------------


class TestSkillsListedInTree:
    """Verify all skill directories and files appear in the tree."""

    def test_all_skills_appear_as_children(self, tmp_path: Path):
        skill_names = ["handoff", "review-pr", "deploy-app"]
        lib = _create_skill_library(tmp_path, skill_names)
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        child_names = [c["name"] for c in cat["children"]]
        for name in skill_names:
            assert name in child_names, f"Skill '{name}' missing from tree"

    def test_skill_directories_are_not_leaf_nodes(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path, ["handoff"])
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        skill_node = _find_node(cat["children"], "handoff")
        assert skill_node is not None
        assert skill_node["path"] is None, "Skill directory should not have a path"

    def test_skill_md_files_are_leaf_nodes(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path, ["handoff"])
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        skill_node = _find_node(cat["children"], "handoff")
        skill_file = _find_node(skill_node["children"], "SKILL.md")
        assert skill_file is not None
        assert skill_file["path"] is not None
        assert skill_file["path"].endswith("SKILL.md")

    def test_skill_file_path_is_absolute(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path, ["handoff"])
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        skill_node = _find_node(cat["children"], "handoff")
        skill_file = _find_node(skill_node["children"], "SKILL.md")
        assert Path(skill_file["path"]).is_absolute()

    def test_skill_file_path_points_to_real_file(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path, ["handoff"])
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        skill_node = _find_node(cat["children"], "handoff")
        skill_file = _find_node(skill_node["children"], "SKILL.md")
        assert Path(skill_file["path"]).is_file()

    def test_many_skills_all_listed(self, tmp_path: Path):
        """Test with a realistic number of skills (like the actual library)."""
        names = [
            "build-traceability", "close-loop", "compile-team", "handoff",
            "new-adr", "new-dev-decision", "new-work", "notes-to-stories",
            "release-notes", "review-pr", "scaffold-project", "seed-tasks",
            "threat-model", "update-docs", "validate-config", "validate-repo",
        ]
        lib = _create_skill_library(tmp_path, names)
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        child_names = [c["name"] for c in cat["children"]]
        assert len(child_names) == len(names)
        for name in names:
            assert name in child_names

    def test_skills_sorted_alphabetically(self, tmp_path: Path):
        names = ["zebra", "alpha", "middle"]
        lib = _create_skill_library(tmp_path, names)
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        child_names = [c["name"] for c in cat["children"]]
        assert child_names == sorted(names)


# ---------------------------------------------------------------------------
# Test: Skill file content is readable
# ---------------------------------------------------------------------------


class TestSkillFileContentReadable:
    """Verify skill files can be read from the paths stored in the tree."""

    def test_skill_file_content_matches(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path, ["handoff"])
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        skill_node = _find_node(cat["children"], "handoff")
        skill_file = _find_node(skill_node["children"], "SKILL.md")
        content = Path(skill_file["path"]).read_text(encoding="utf-8")
        assert "# Skill: Handoff" in content
        assert "Skill content for handoff" in content

    def test_all_skill_files_readable(self, tmp_path: Path):
        names = ["handoff", "review-pr", "deploy-app"]
        lib = _create_skill_library(tmp_path, names)
        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        paths = _collect_leaf_paths(cat["children"])
        assert len(paths) == len(names)
        for path_str in paths:
            path = Path(path_str)
            assert path.is_file(), f"Skill file not found: {path}"
            content = path.read_text(encoding="utf-8")
            assert content.startswith("# Skill:"), f"Unexpected content in {path}"


# ---------------------------------------------------------------------------
# Test: Nested skill directory structures
# ---------------------------------------------------------------------------


class TestSkillNestedStructure:
    """Verify tree handles skills with extra files or subdirectories."""

    def test_skill_with_multiple_files(self, tmp_path: Path):
        lib = tmp_path / "lib"
        skill_dir = lib / "claude" / "skills" / "deploy"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Deploy", encoding="utf-8")
        (skill_dir / "README.md").write_text("# Readme", encoding="utf-8")

        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        deploy_node = _find_node(cat["children"], "deploy")
        assert deploy_node is not None
        child_names = [c["name"] for c in deploy_node["children"]]
        assert "SKILL.md" in child_names
        assert "README.md" in child_names

    def test_hidden_files_excluded_from_skill_dirs(self, tmp_path: Path):
        lib = tmp_path / "lib"
        skill_dir = lib / "claude" / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Test", encoding="utf-8")
        (skill_dir / ".hidden").write_text("hidden", encoding="utf-8")

        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        skill_node = _find_node(cat["children"], "test-skill")
        names = _collect_all_names(skill_node["children"])
        assert ".hidden" not in names
        assert "SKILL.md" in names

    def test_skill_with_subdirectory(self, tmp_path: Path):
        lib = tmp_path / "lib"
        skill_dir = lib / "claude" / "skills" / "complex-skill"
        (skill_dir / "examples").mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Complex", encoding="utf-8")
        (skill_dir / "examples" / "basic.md").write_text("# Basic", encoding="utf-8")

        tree = _build_file_tree(lib)
        cat = _get_category(tree, "Claude Skills")
        skill_node = _find_node(cat["children"], "complex-skill")
        assert skill_node is not None
        examples_node = _find_node(skill_node["children"], "examples")
        assert examples_node is not None
        assert examples_node["path"] is None  # directory, not a file
        basic = _find_node(examples_node["children"], "basic.md")
        assert basic is not None
        assert basic["path"] is not None


# ---------------------------------------------------------------------------
# Test: _scan_dir for skill directories
# ---------------------------------------------------------------------------


class TestScanDirForSkills:
    """Test the _scan_dir helper specifically for skill directory patterns."""

    def test_scan_skill_directory(self, tmp_path: Path):
        skill_dir = tmp_path / "handoff"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Handoff", encoding="utf-8")

        result = _scan_dir(tmp_path)
        assert len(result) == 1
        assert result[0]["name"] == "handoff"
        assert result[0]["path"] is None  # directory
        assert len(result[0]["children"]) == 1
        assert result[0]["children"][0]["name"] == "SKILL.md"

    def test_scan_multiple_skill_directories(self, tmp_path: Path):
        for name in ["alpha", "beta", "gamma"]:
            d = tmp_path / name
            d.mkdir()
            (d / "SKILL.md").write_text(f"# {name}", encoding="utf-8")

        result = _scan_dir(tmp_path)
        names = [r["name"] for r in result]
        assert names == ["alpha", "beta", "gamma"]  # sorted

    def test_scan_empty_directory(self, tmp_path: Path):
        result = _scan_dir(tmp_path)
        assert result == []


# ---------------------------------------------------------------------------
# Test: Integration with full library
# ---------------------------------------------------------------------------


class TestSkillReadIntegration:
    """Integration tests using a full library structure."""

    def test_skills_coexist_with_other_categories(self, tmp_path: Path):
        lib = _create_full_library(tmp_path)
        tree = _build_file_tree(lib)

        # All categories present
        cat_names = [c["name"] for c in tree]
        assert "Claude Skills" in cat_names
        assert "Personas" in cat_names
        assert "Workflows" in cat_names
        assert "Claude Commands" in cat_names

        # Skills have correct children
        skills = _get_category(tree, "Claude Skills")
        skill_names = [c["name"] for c in skills["children"]]
        assert "handoff" in skill_names
        assert "review-pr" in skill_names
        assert "scaffold-project" in skill_names

    def test_skill_tree_structure_matches_filesystem(self, tmp_path: Path):
        lib = _create_full_library(tmp_path)
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")

        # Each skill dir should have children
        for skill_node in skills["children"]:
            assert skill_node["path"] is None, f"{skill_node['name']} should be dir"
            assert len(skill_node["children"]) > 0
            # Each should have SKILL.md
            file_names = [c["name"] for c in skill_node["children"]]
            assert "SKILL.md" in file_names

    def test_file_path_label_data_available(self, tmp_path: Path):
        """Verify each skill file node has a string path suitable for display."""
        lib = _create_full_library(tmp_path)
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")

        for skill_node in skills["children"]:
            for child in skill_node["children"]:
                if child["path"] is not None:
                    # Path should be a non-empty string
                    assert isinstance(child["path"], str)
                    assert len(child["path"]) > 0
                    # Path should contain the skill name
                    assert skill_node["name"] in child["path"]
