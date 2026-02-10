"""Tests for persona read/list — pure logic, no Qt dependency (BEAN-081).

Validates that the tree-building logic correctly discovers, lists, and
structures persona assets from the library directory.

PySide6 is mocked out so these tests run in headless environments without
libGL.so.1.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock PySide6 modules before importing library_manager
for _mod_name in (
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "mistune",
):
    if _mod_name not in sys.modules:
        sys.modules[_mod_name] = MagicMock()

# ruff: noqa: E402
from foundry_app.ui.screens.library_manager import _build_file_tree

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_persona_library(root: Path) -> Path:
    """Create a realistic persona library structure for testing."""
    lib = root / "test-library"

    # Multiple personas with standard structure
    for name in ("architect", "developer", "tech-qa"):
        persona_dir = lib / "personas" / name
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text(
            f"# Persona: {name.replace('-', ' ').title()}\n\n## Mission\n\nDoes {name} things.",
            encoding="utf-8",
        )
        (persona_dir / "outputs.md").write_text(
            f"# {name.replace('-', ' ').title()} -- Outputs",
            encoding="utf-8",
        )
        (persona_dir / "prompts.md").write_text(
            f"# {name.replace('-', ' ').title()} -- Prompts",
            encoding="utf-8",
        )
        templates_dir = persona_dir / "templates"
        templates_dir.mkdir()
        (templates_dir / "review.md").write_text("# Review template", encoding="utf-8")

    # Other categories (minimal, just to ensure they exist)
    (lib / "stacks" / "python").mkdir(parents=True)
    (lib / "stacks" / "python" / "conventions.md").write_text("# Python", encoding="utf-8")
    (lib / "templates").mkdir(parents=True)
    (lib / "templates" / "shared.md").write_text("# Shared", encoding="utf-8")
    (lib / "workflows").mkdir(parents=True)
    (lib / "workflows" / "default.md").write_text("# Default", encoding="utf-8")
    (lib / "claude" / "commands").mkdir(parents=True)
    (lib / "claude" / "skills").mkdir(parents=True)
    (lib / "claude" / "hooks").mkdir(parents=True)

    return lib


# ---------------------------------------------------------------------------
# _build_file_tree — persona category population
# ---------------------------------------------------------------------------


class TestPersonaTreeListing:
    """AC: Tree shows all existing personas when the Persona category is selected."""

    def test_personas_category_exists(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [cat["name"] for cat in tree]
        assert "Personas" in names

    def test_all_personas_listed(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        child_names = sorted(c["name"] for c in personas["children"])
        assert child_names == ["architect", "developer", "tech-qa"]

    def test_persona_directory_node_has_no_path(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        for persona in personas["children"]:
            assert persona["path"] is None, (
                f"Persona dir '{persona['name']}' should have path=None"
            )

    def test_persona_contains_standard_files(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        child_names = [c["name"] for c in dev["children"]]
        assert "persona.md" in child_names
        assert "outputs.md" in child_names
        assert "prompts.md" in child_names
        assert "templates" in child_names

    def test_persona_files_have_correct_paths(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        persona_md = next(c for c in dev["children"] if c["name"] == "persona.md")
        assert persona_md["path"] is not None
        assert persona_md["path"].endswith("developer/persona.md")
        assert Path(persona_md["path"]).is_file()

    def test_persona_template_subdirectory_listed(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        templates = next(c for c in dev["children"] if c["name"] == "templates")
        assert templates["path"] is None
        assert len(templates["children"]) == 1
        assert templates["children"][0]["name"] == "review.md"

    def test_persona_template_files_have_paths(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        templates = next(c for c in dev["children"] if c["name"] == "templates")
        review = templates["children"][0]
        assert review["path"] is not None
        assert review["path"].endswith("templates/review.md")

    def test_empty_personas_directory(self, tmp_path: Path):
        lib = tmp_path / "empty-lib"
        (lib / "personas").mkdir(parents=True)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        assert personas["children"] == []

    def test_single_persona(self, tmp_path: Path):
        lib = tmp_path / "single-lib"
        p = lib / "personas" / "solo"
        p.mkdir(parents=True)
        (p / "persona.md").write_text("# Solo", encoding="utf-8")
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        assert len(personas["children"]) == 1
        assert personas["children"][0]["name"] == "solo"

    def test_hidden_files_excluded_from_personas(self, tmp_path: Path):
        lib = tmp_path / "hidden-lib"
        p = lib / "personas" / "dev"
        p.mkdir(parents=True)
        (p / "persona.md").write_text("# Dev", encoding="utf-8")
        (p / ".hidden").write_text("hidden", encoding="utf-8")
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = personas["children"][0]
        names = [c["name"] for c in dev["children"]]
        assert ".hidden" not in names
        assert "persona.md" in names


# ---------------------------------------------------------------------------
# _scan_dir — persona file reading
# ---------------------------------------------------------------------------


class TestPersonaFileContent:
    """AC: Clicking a persona file displays its content in the editor pane."""

    def test_persona_md_content_readable(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        persona_md = next(c for c in dev["children"] if c["name"] == "persona.md")
        path = Path(persona_md["path"])
        content = path.read_text(encoding="utf-8")
        assert "# Persona: Developer" in content
        assert "## Mission" in content

    def test_outputs_md_content_readable(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        outputs_md = next(c for c in dev["children"] if c["name"] == "outputs.md")
        content = Path(outputs_md["path"]).read_text(encoding="utf-8")
        assert "Developer -- Outputs" in content

    def test_prompts_md_content_readable(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        prompts_md = next(c for c in dev["children"] if c["name"] == "prompts.md")
        content = Path(prompts_md["path"]).read_text(encoding="utf-8")
        assert "Developer -- Prompts" in content


# ---------------------------------------------------------------------------
# File path correctness
# ---------------------------------------------------------------------------


class TestPersonaFilePaths:
    """AC: File path label updates to show the selected file path."""

    def test_file_paths_are_absolute(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        for child in dev["children"]:
            if child["path"] is not None:
                assert Path(child["path"]).is_absolute()

    def test_file_paths_exist_on_disk(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        for persona in personas["children"]:
            for child in persona["children"]:
                if child["path"] is not None:
                    assert Path(child["path"]).exists(), (
                        f"Path should exist: {child['path']}"
                    )

    def test_all_persona_files_under_library_root(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")

        def _collect_paths(nodes: list[dict]) -> list[str]:
            paths = []
            for node in nodes:
                if node.get("path"):
                    paths.append(node["path"])
                paths.extend(_collect_paths(node.get("children", [])))
            return paths

        all_paths = _collect_paths(personas["children"])
        assert len(all_paths) > 0
        for p in all_paths:
            assert str(lib) in p, f"Path {p} should be under library root {lib}"


# ---------------------------------------------------------------------------
# _scan_dir — directory sorting
# ---------------------------------------------------------------------------


class TestPersonaSorting:
    """Personas and their files should be listed in sorted order."""

    def test_personas_sorted_alphabetically(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        names = [c["name"] for c in personas["children"]]
        assert names == sorted(names)

    def test_persona_files_sorted_alphabetically(self, tmp_path: Path):
        lib = _create_persona_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        names = [c["name"] for c in dev["children"]]
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# Real library scan (integration-style)
# ---------------------------------------------------------------------------


class TestRealLibraryScan:
    """Verify _build_file_tree works against the actual ai-team-library."""

    def test_scan_real_library_personas(self):
        lib = Path("/tmp/foundry-worktree-BEAN-081/ai-team-library")
        if not lib.is_dir():
            return  # skip if not available
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        names = [c["name"] for c in personas["children"]]
        # Real library should have at least these core personas
        assert "developer" in names
        assert "architect" in names
        assert "tech-qa" in names
        assert "team-lead" in names
        assert "ba" in names

    def test_real_persona_has_standard_files(self):
        lib = Path("/tmp/foundry-worktree-BEAN-081/ai-team-library")
        if not lib.is_dir():
            return
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        child_names = [c["name"] for c in dev["children"]]
        assert "persona.md" in child_names
        assert "outputs.md" in child_names
        assert "prompts.md" in child_names

    def test_real_persona_files_are_readable(self):
        lib = Path("/tmp/foundry-worktree-BEAN-081/ai-team-library")
        if not lib.is_dir():
            return
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        for persona in personas["children"]:
            for child in persona["children"]:
                if child["path"] is not None:
                    path = Path(child["path"])
                    assert path.is_file(), f"Expected file: {path}"
                    content = path.read_text(encoding="utf-8")
                    assert len(content) > 0, f"File should not be empty: {path}"
