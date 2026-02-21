"""Tests for Library Manager template read functionality (BEAN-089).

These tests verify the template listing and reading logic without
requiring a running PySide6/libGL display server.  Pure-logic tests
call ``_build_file_tree`` / ``_scan_dir`` directly; integration tests
mock the Qt layer.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# PySide6 stub — allows importing library_manager without libGL
# ---------------------------------------------------------------------------

def _install_pyside6_stubs() -> None:
    """Install MagicMock-based PySide6 stubs so imports succeed without libGL."""
    try:
        from PySide6.QtWidgets import QWidget  # noqa: F401

        return  # real PySide6 is functional — nothing to do
    except (ImportError, RuntimeError):
        pass  # libGL missing or other init failure — install stubs

    stub = MagicMock()
    for name in list(sys.modules):
        if name == "PySide6" or name.startswith("PySide6."):
            del sys.modules[name]
    for name in [
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ]:
        sys.modules[name] = stub


_install_pyside6_stubs()

# Now safe to import the library_manager module
from foundry_app.ui.screens.library_manager import (  # noqa: E402
    STARTER_TEMPLATE,
    _build_file_tree,
    _scan_dir,
    starter_content,
    validate_asset_name,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_template_library(root: Path) -> Path:
    """Create a library with a rich template directory for testing."""
    lib = root / "test-library"

    # Shared templates
    tpl_dir = lib / "templates"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "CLAUDE.md.j2").write_text("# Claude template\n\nMain template.", encoding="utf-8")
    (tpl_dir / "README.md.j2").write_text("# README template\n\nFor projects.", encoding="utf-8")

    # Nested shared templates
    shared_sub = tpl_dir / "shared"
    shared_sub.mkdir(parents=True)
    (shared_sub / "adr.md").write_text("# ADR template\n\nDecision record.", encoding="utf-8")
    (shared_sub / "runbook.md").write_text("# Runbook\n\nOperations guide.", encoding="utf-8")

    # Persona with templates sub-directory
    persona_dir = lib / "personas" / "developer"
    persona_dir.mkdir(parents=True)
    (persona_dir / "persona.md").write_text("# Developer persona", encoding="utf-8")
    ptpl = persona_dir / "templates"
    ptpl.mkdir()
    (ptpl / "impl.md.j2").write_text("# Implementation template", encoding="utf-8")
    (ptpl / "review.md.j2").write_text("# Review template", encoding="utf-8")

    # Other categories (minimal)
    (lib / "stacks" / "python").mkdir(parents=True)
    (lib / "stacks" / "python" / "conventions.md").write_text("# Python", encoding="utf-8")
    (lib / "workflows").mkdir(parents=True)
    (lib / "workflows" / "default.md").write_text("# Default", encoding="utf-8")
    (lib / "claude" / "commands").mkdir(parents=True)
    (lib / "claude" / "skills").mkdir(parents=True)
    (lib / "claude" / "hooks").mkdir(parents=True)

    return lib


# ---------------------------------------------------------------------------
# _scan_dir — template directories
# ---------------------------------------------------------------------------


class TestScanDirTemplates:
    """Verify _scan_dir correctly enumerates template files and dirs."""

    def test_scans_flat_template_files(self, tmp_path: Path):
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / "a.md").write_text("aaa", encoding="utf-8")
        (tpl / "b.md.j2").write_text("bbb", encoding="utf-8")
        result = _scan_dir(tpl)
        names = [c["name"] for c in result]
        assert "a.md" in names
        assert "b.md.j2" in names

    def test_scans_nested_template_dirs(self, tmp_path: Path):
        tpl = tmp_path / "templates"
        sub = tpl / "shared"
        sub.mkdir(parents=True)
        (sub / "adr.md").write_text("adr", encoding="utf-8")
        result = _scan_dir(tpl)
        assert len(result) == 1
        assert result[0]["name"] == "shared"
        assert result[0]["path"] is None
        assert len(result[0]["children"]) == 1
        assert result[0]["children"][0]["name"] == "adr.md"

    def test_file_nodes_have_path(self, tmp_path: Path):
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / "file.md").write_text("content", encoding="utf-8")
        result = _scan_dir(tpl)
        assert result[0]["path"] is not None
        assert result[0]["path"].endswith("file.md")

    def test_dir_nodes_have_no_path(self, tmp_path: Path):
        tpl = tmp_path / "templates"
        sub = tpl / "sub"
        sub.mkdir(parents=True)
        (sub / "x.md").write_text("x", encoding="utf-8")
        result = _scan_dir(tpl)
        assert result[0]["path"] is None

    def test_hidden_files_excluded(self, tmp_path: Path):
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / ".hidden").write_text("nope", encoding="utf-8")
        (tpl / "visible.md").write_text("yes", encoding="utf-8")
        result = _scan_dir(tpl)
        names = [c["name"] for c in result]
        assert ".hidden" not in names
        assert "visible.md" in names

    def test_results_sorted_alphabetically(self, tmp_path: Path):
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / "zebra.md").write_text("z", encoding="utf-8")
        (tpl / "alpha.md").write_text("a", encoding="utf-8")
        (tpl / "middle.md").write_text("m", encoding="utf-8")
        result = _scan_dir(tpl)
        names = [c["name"] for c in result]
        assert names == ["alpha.md", "middle.md", "zebra.md"]

    def test_empty_dir_returns_empty_list(self, tmp_path: Path):
        tpl = tmp_path / "templates"
        tpl.mkdir()
        result = _scan_dir(tpl)
        assert result == []

    def test_deeply_nested_templates(self, tmp_path: Path):
        deep = tmp_path / "templates" / "level1" / "level2" / "level3"
        deep.mkdir(parents=True)
        (deep / "deep.md").write_text("deep content", encoding="utf-8")
        result = _scan_dir(tmp_path / "templates")
        # Drill down: level1 > level2 > level3 > deep.md
        node = result[0]
        assert node["name"] == "level1"
        node = node["children"][0]
        assert node["name"] == "level2"
        node = node["children"][0]
        assert node["name"] == "level3"
        assert node["children"][0]["name"] == "deep.md"
        assert node["children"][0]["path"].endswith("deep.md")


# ---------------------------------------------------------------------------
# _build_file_tree — template category
# ---------------------------------------------------------------------------


class TestBuildFileTreeTemplates:
    """Verify _build_file_tree populates the Shared Templates category."""

    def test_shared_templates_category_present(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [c["name"] for c in tree]
        assert "Shared Templates" in names

    def test_shared_templates_lists_all_files(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        tpl = next(c for c in tree if c["name"] == "Shared Templates")
        top_names = [c["name"] for c in tpl["children"]]
        assert "CLAUDE.md.j2" in top_names
        assert "README.md.j2" in top_names
        assert "shared" in top_names  # nested dir

    def test_shared_templates_nested_dir_contents(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        tpl = next(c for c in tree if c["name"] == "Shared Templates")
        shared_dir = next(c for c in tpl["children"] if c["name"] == "shared")
        child_names = [c["name"] for c in shared_dir["children"]]
        assert "adr.md" in child_names
        assert "runbook.md" in child_names

    def test_shared_template_file_paths_are_absolute(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        tpl = next(c for c in tree if c["name"] == "Shared Templates")
        claude_tpl = next(c for c in tpl["children"] if c["name"] == "CLAUDE.md.j2")
        assert claude_tpl["path"] is not None
        assert Path(claude_tpl["path"]).is_absolute()
        assert Path(claude_tpl["path"]).is_file()

    def test_persona_templates_listed_under_persona(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        tpl_dir = next(c for c in dev["children"] if c["name"] == "templates")
        tpl_names = [c["name"] for c in tpl_dir["children"]]
        assert "impl.md.j2" in tpl_names
        assert "review.md.j2" in tpl_names

    def test_persona_template_files_have_paths(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        tpl_dir = next(c for c in dev["children"] if c["name"] == "templates")
        for tpl in tpl_dir["children"]:
            assert tpl["path"] is not None
            assert Path(tpl["path"]).is_file()

    def test_missing_templates_dir_gives_empty(self, tmp_path: Path):
        lib = tmp_path / "sparse-lib"
        (lib / "personas" / "test").mkdir(parents=True)
        (lib / "personas" / "test" / "persona.md").write_text("hi", encoding="utf-8")
        tree = _build_file_tree(lib)
        tpl = next(c for c in tree if c["name"] == "Shared Templates")
        assert tpl["children"] == []

    def test_nonexistent_library_returns_empty(self, tmp_path: Path):
        tree = _build_file_tree(tmp_path / "nonexistent")
        assert tree == []

    def test_all_seven_categories_present(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [c["name"] for c in tree]
        assert len(names) == 7
        assert "Personas" in names
        assert "Expertise" in names
        assert "Shared Templates" in names
        assert "Workflows" in names
        assert "Claude Commands" in names
        assert "Claude Skills" in names
        assert "Claude Hooks" in names


# ---------------------------------------------------------------------------
# Template file content reading
# ---------------------------------------------------------------------------


class TestTemplateFileReading:
    """Verify that template files can be read from paths in the tree."""

    def test_shared_template_content_readable(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        tpl = next(c for c in tree if c["name"] == "Shared Templates")
        claude_tpl = next(c for c in tpl["children"] if c["name"] == "CLAUDE.md.j2")
        content = Path(claude_tpl["path"]).read_text(encoding="utf-8")
        assert "# Claude template" in content
        assert "Main template." in content

    def test_nested_template_content_readable(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        tpl = next(c for c in tree if c["name"] == "Shared Templates")
        shared_dir = next(c for c in tpl["children"] if c["name"] == "shared")
        adr = next(c for c in shared_dir["children"] if c["name"] == "adr.md")
        content = Path(adr["path"]).read_text(encoding="utf-8")
        assert "# ADR template" in content
        assert "Decision record." in content

    def test_persona_template_content_readable(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = next(c for c in personas["children"] if c["name"] == "developer")
        tpl_dir = next(c for c in dev["children"] if c["name"] == "templates")
        impl = next(c for c in tpl_dir["children"] if c["name"] == "impl.md.j2")
        content = Path(impl["path"]).read_text(encoding="utf-8")
        assert "# Implementation template" in content

    def test_all_shared_templates_have_readable_content(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        tpl = next(c for c in tree if c["name"] == "Shared Templates")

        def collect_files(nodes):
            files = []
            for node in nodes:
                if node["path"] is not None:
                    files.append(node)
                files.extend(collect_files(node.get("children", [])))
            return files

        files = collect_files(tpl["children"])
        assert len(files) == 4  # CLAUDE.md.j2, README.md.j2, shared/adr.md, shared/runbook.md
        for f in files:
            content = Path(f["path"]).read_text(encoding="utf-8")
            assert len(content) > 0

    def test_template_path_matches_filesystem(self, tmp_path: Path):
        lib = _create_template_library(tmp_path)
        tree = _build_file_tree(lib)
        tpl = next(c for c in tree if c["name"] == "Shared Templates")
        claude_tpl = next(c for c in tpl["children"] if c["name"] == "CLAUDE.md.j2")
        expected = lib / "templates" / "CLAUDE.md.j2"
        assert Path(claude_tpl["path"]) == expected


# ---------------------------------------------------------------------------
# Starter content for templates
# ---------------------------------------------------------------------------


class TestTemplateStarterContentPure:
    """Verify starter_content() returns correct template scaffolding."""

    def test_shared_template_has_purpose_section(self):
        content = starter_content("Shared Templates", "risk-log")
        assert "## Purpose" in content

    def test_shared_template_has_checklist_section(self):
        content = starter_content("Shared Templates", "risk-log")
        assert "## Checklist" in content

    def test_shared_template_has_definition_of_done(self):
        content = starter_content("Shared Templates", "risk-log")
        assert "## Definition of Done" in content

    def test_shared_template_title_from_name(self):
        content = starter_content("Shared Templates", "risk-log")
        assert "# Risk Log" in content

    def test_shared_template_has_metadata_table(self):
        content = starter_content("Shared Templates", "test-plan")
        assert "| **Category** |" in content
        assert "| **Version** |" in content

    def test_persona_template_has_purpose(self):
        content = starter_content("_persona_template", "code-review")
        assert "## Purpose" in content
        assert "# Code Review" in content

    def test_starter_template_constant(self):
        assert "## Purpose" in STARTER_TEMPLATE
        assert "## Checklist" in STARTER_TEMPLATE
        assert "## Definition of Done" in STARTER_TEMPLATE
        assert "{name}" in STARTER_TEMPLATE


# ---------------------------------------------------------------------------
# Validate asset name (pure logic)
# ---------------------------------------------------------------------------


class TestValidateAssetNamePure:

    def test_valid_template_names(self):
        assert validate_asset_name("risk-log") is None
        assert validate_asset_name("adr-template") is None
        assert validate_asset_name("readme") is None
        assert validate_asset_name("v2-template") is None

    def test_empty_name(self):
        assert validate_asset_name("") is not None

    def test_uppercase_rejected(self):
        assert validate_asset_name("MyTemplate") is not None

    def test_spaces_rejected(self):
        assert validate_asset_name("my template") is not None

    def test_underscore_rejected(self):
        assert validate_asset_name("my_template") is not None

    def test_special_chars_rejected(self):
        assert validate_asset_name("tmpl@1") is not None

    def test_too_long(self):
        assert validate_asset_name("a" * 61) is not None
        assert validate_asset_name("a" * 60) is None
