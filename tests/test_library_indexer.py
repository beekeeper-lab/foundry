"""Tests for foundry_app.services.library_indexer — library scanning and indexing."""

from pathlib import Path

from foundry_app.core.models import LibraryIndex
from foundry_app.services.library_indexer import build_library_index

# Path to the real library bundled with the repo
LIBRARY_ROOT = Path(__file__).resolve().parent.parent / "ai-team-library"

EXPECTED_PERSONAS = [
    "architect",
    "ba",
    "code-quality-reviewer",
    "compliance-risk",
    "developer",
    "devops-release",
    "integrator-merge-captain",
    "researcher-librarian",
    "security-engineer",
    "team-lead",
    "tech-qa",
    "technical-writer",
    "ux-ui-designer",
]

EXPECTED_STACKS = [
    "clean-code",
    "devops",
    "dotnet",
    "java",
    "node",
    "python",
    "python-qt-pyside6",
    "react",
    "security",
    "sql-dba",
    "typescript",
]

EXPECTED_HOOK_PACKS = [
    "compliance-gate",
    "hook-policy",
    "post-task-qa",
    "pre-commit-lint",
    "security-scan",
]


# ---------------------------------------------------------------------------
# Integration tests against real ai-team-library
# ---------------------------------------------------------------------------


class TestBuildLibraryIndexReal:
    """Integration tests using the actual ai-team-library directory."""

    def test_returns_library_index(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert isinstance(idx, LibraryIndex)
        assert idx.library_root == str(LIBRARY_ROOT.resolve())

    def test_discovers_all_personas(self):
        idx = build_library_index(LIBRARY_ROOT)
        persona_ids = [p.id for p in idx.personas]
        assert persona_ids == EXPECTED_PERSONAS

    def test_discovers_all_stacks(self):
        idx = build_library_index(LIBRARY_ROOT)
        stack_ids = [s.id for s in idx.stacks]
        assert stack_ids == EXPECTED_STACKS

    def test_discovers_all_hook_packs(self):
        idx = build_library_index(LIBRARY_ROOT)
        pack_ids = [h.id for h in idx.hook_packs]
        assert pack_ids == EXPECTED_HOOK_PACKS

    def test_persona_has_expected_files(self):
        idx = build_library_index(LIBRARY_ROOT)
        dev = idx.persona_by_id("developer")
        assert dev is not None
        assert dev.has_persona_md is True
        assert dev.has_outputs_md is True
        assert dev.has_prompts_md is True
        assert len(dev.templates) > 0

    def test_all_personas_have_persona_md(self):
        idx = build_library_index(LIBRARY_ROOT)
        for persona in idx.personas:
            assert persona.has_persona_md, f"{persona.id} missing persona.md"

    def test_stack_has_files(self):
        idx = build_library_index(LIBRARY_ROOT)
        python_stack = idx.stack_by_id("python")
        assert python_stack is not None
        assert "conventions.md" in python_stack.files
        assert len(python_stack.files) >= 3

    def test_hook_pack_has_file(self):
        idx = build_library_index(LIBRARY_ROOT)
        lint = idx.hook_pack_by_id("pre-commit-lint")
        assert lint is not None
        assert "pre-commit-lint.md" in lint.files

    def test_persona_templates_are_filenames(self):
        """Templates list should contain filenames, not full paths."""
        idx = build_library_index(LIBRARY_ROOT)
        dev = idx.persona_by_id("developer")
        assert dev is not None
        for t in dev.templates:
            assert "/" not in t
            assert t.endswith(".md")


# ---------------------------------------------------------------------------
# Graceful degradation tests (using tmp_path)
# ---------------------------------------------------------------------------


class TestBuildLibraryIndexGraceful:
    """Test graceful handling of missing or empty directories."""

    def test_nonexistent_root(self, tmp_path: Path):
        idx = build_library_index(tmp_path / "does-not-exist")
        assert isinstance(idx, LibraryIndex)
        assert idx.personas == []
        assert idx.stacks == []
        assert idx.hook_packs == []

    def test_empty_root(self, tmp_path: Path):
        idx = build_library_index(tmp_path)
        assert isinstance(idx, LibraryIndex)
        assert idx.personas == []
        assert idx.stacks == []
        assert idx.hook_packs == []

    def test_missing_personas_dir(self, tmp_path: Path):
        (tmp_path / "stacks" / "python").mkdir(parents=True)
        (tmp_path / "stacks" / "python" / "conventions.md").touch()
        idx = build_library_index(tmp_path)
        assert idx.personas == []
        assert len(idx.stacks) == 1

    def test_missing_stacks_dir(self, tmp_path: Path):
        (tmp_path / "personas" / "dev").mkdir(parents=True)
        (tmp_path / "personas" / "dev" / "persona.md").touch()
        idx = build_library_index(tmp_path)
        assert idx.stacks == []
        assert len(idx.personas) == 1

    def test_missing_hooks_dir(self, tmp_path: Path):
        (tmp_path / "personas" / "dev").mkdir(parents=True)
        idx = build_library_index(tmp_path)
        assert idx.hook_packs == []

    def test_persona_without_optional_files(self, tmp_path: Path):
        persona_dir = tmp_path / "personas" / "minimal"
        persona_dir.mkdir(parents=True)
        idx = build_library_index(tmp_path)
        p = idx.persona_by_id("minimal")
        assert p is not None
        assert p.has_persona_md is False
        assert p.has_outputs_md is False
        assert p.has_prompts_md is False
        assert p.templates == []

    def test_persona_with_templates(self, tmp_path: Path):
        persona_dir = tmp_path / "personas" / "writer"
        (persona_dir / "templates").mkdir(parents=True)
        (persona_dir / "templates" / "report.md").touch()
        (persona_dir / "templates" / "summary.md").touch()
        idx = build_library_index(tmp_path)
        p = idx.persona_by_id("writer")
        assert p is not None
        assert sorted(p.templates) == ["report.md", "summary.md"]


# ---------------------------------------------------------------------------
# Lookup helper tests
# ---------------------------------------------------------------------------


class TestLibraryIndexLookups:
    """Test the lookup-by-id convenience methods on LibraryIndex."""

    def test_persona_by_id_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.persona_by_id("developer") is not None

    def test_persona_by_id_not_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.persona_by_id("nonexistent") is None

    def test_stack_by_id_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.stack_by_id("python") is not None

    def test_stack_by_id_not_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.stack_by_id("cobol") is None

    def test_hook_pack_by_id_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.hook_pack_by_id("security-scan") is not None

    def test_hook_pack_by_id_not_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.hook_pack_by_id("nonexistent") is None
