"""Tests for foundry_app.services.library_indexer — library scanning and indexing."""

from pathlib import Path

from foundry_app.core.models import LibraryIndex
from foundry_app.services.library_indexer import build_library_index

# Path to the real library bundled with the repo
LIBRARY_ROOT = Path(__file__).resolve().parent.parent / "ai-team-library"

EXPECTED_PERSONAS = [
    "architect",
    "ba",
    "change-management",
    "code-quality-reviewer",
    "compliance-risk",
    "customer-success",
    "data-analyst",
    "data-engineer",
    "database-administrator",
    "developer",
    "devops-release",
    "financial-operations",
    "integrator-merge-captain",
    "legal-counsel",
    "mobile-developer",
    "platform-sre-engineer",
    "product-owner",
    "researcher-librarian",
    "sales-engineer",
    "security-engineer",
    "team-lead",
    "tech-qa",
    "technical-writer",
    "ux-ui-designer",
]

EXPECTED_EXPERTISE = [
    "accessibility-compliance",
    "api-design",
    "aws-cloud-platform",
    "azure-cloud-platform",
    "business-intelligence",
    "change-management",
    "clean-code",
    "customer-enablement",
    "data-engineering",
    "devops",
    "dotnet",
    "event-driven-messaging",
    "finops",
    "frontend-build-tooling",
    "gcp-cloud-platform",
    "gdpr-data-privacy",
    "go",
    "hipaa-compliance",
    "iso-9000",
    "java",
    "kotlin",
    "kubernetes",
    "microservices",
    "mlops",
    "node",
    "pci-dss-compliance",
    "product-strategy",
    "python",
    "python-qt-pyside6",
    "react",
    "react-native",
    "rust",
    "sales-engineering",
    "security",
    "sox-compliance",
    "sql-dba",
    "swift",
    "terraform",
    "typescript",
]

EXPECTED_HOOK_PACKS = [
    "az-limited-ops",
    "az-read-only",
    "compliance-gate",
    "git-commit-branch",
    "git-generate-pr",
    "git-merge-to-prod",
    "git-merge-to-test",
    "git-push-feature",
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

    def test_discovers_all_expertise(self):
        idx = build_library_index(LIBRARY_ROOT)
        expertise_ids = [s.id for s in idx.expertise]
        assert expertise_ids == EXPECTED_EXPERTISE

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

    def test_expertise_has_files(self):
        idx = build_library_index(LIBRARY_ROOT)
        python_expertise = idx.expertise_by_id("python")
        assert python_expertise is not None
        assert "conventions.md" in python_expertise.files
        assert len(python_expertise.files) >= 3

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
        assert idx.expertise == []
        assert idx.hook_packs == []

    def test_empty_root(self, tmp_path: Path):
        idx = build_library_index(tmp_path)
        assert isinstance(idx, LibraryIndex)
        assert idx.personas == []
        assert idx.expertise == []
        assert idx.hook_packs == []

    def test_missing_personas_dir(self, tmp_path: Path):
        (tmp_path / "expertise" / "python").mkdir(parents=True)
        (tmp_path / "expertise" / "python" / "conventions.md").touch()
        idx = build_library_index(tmp_path)
        assert idx.personas == []
        assert len(idx.expertise) == 1

    def test_missing_expertise_dir(self, tmp_path: Path):
        (tmp_path / "personas" / "dev").mkdir(parents=True)
        (tmp_path / "personas" / "dev" / "persona.md").touch()
        idx = build_library_index(tmp_path)
        assert idx.expertise == []
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

    def test_expertise_by_id_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.expertise_by_id("python") is not None

    def test_expertise_by_id_not_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.expertise_by_id("cobol") is None

    def test_hook_pack_by_id_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.hook_pack_by_id("security-scan") is not None

    def test_hook_pack_by_id_not_found(self):
        idx = build_library_index(LIBRARY_ROOT)
        assert idx.hook_pack_by_id("nonexistent") is None


# ---------------------------------------------------------------------------
# Hook category tests
# ---------------------------------------------------------------------------


class TestHookPackCategories:
    """Test that hook packs have correct categories assigned."""

    def test_git_hooks_have_git_category(self):
        idx = build_library_index(LIBRARY_ROOT)
        git_ids = [
            "git-commit-branch", "git-push-feature", "git-generate-pr",
            "git-merge-to-test", "git-merge-to-prod",
        ]
        for pack_id in git_ids:
            pack = idx.hook_pack_by_id(pack_id)
            assert pack is not None, f"{pack_id} not found"
            assert pack.category == "git", f"{pack_id} category={pack.category}"

    def test_az_hooks_have_az_category(self):
        idx = build_library_index(LIBRARY_ROOT)
        az_ids = ["az-read-only", "az-limited-ops"]
        for pack_id in az_ids:
            pack = idx.hook_pack_by_id(pack_id)
            assert pack is not None, f"{pack_id} not found"
            assert pack.category == "az", f"{pack_id} category={pack.category}"

    def test_code_quality_hooks_have_category(self):
        idx = build_library_index(LIBRARY_ROOT)
        cq_ids = ["pre-commit-lint", "post-task-qa", "security-scan", "compliance-gate"]
        for pack_id in cq_ids:
            pack = idx.hook_pack_by_id(pack_id)
            assert pack is not None, f"{pack_id} not found"
            assert pack.category == "code-quality", f"{pack_id} category={pack.category}"

    def test_category_from_tmp_file(self, tmp_path: Path):
        """Test category parsing from a hook pack file with Category header."""
        hooks_dir = tmp_path / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "my-hook.md").write_text(
            "# Hook Pack: My Hook\n\n## Category\ncustom\n\n## Purpose\nTest\n"
        )
        idx = build_library_index(tmp_path)
        pack = idx.hook_pack_by_id("my-hook")
        assert pack is not None
        assert pack.category == "custom"

    def test_no_category_defaults_empty(self, tmp_path: Path):
        """Hook packs without a Category header get empty string."""
        hooks_dir = tmp_path / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "bare.md").write_text("# Hook Pack: Bare\n\n## Purpose\nTest\n")
        idx = build_library_index(tmp_path)
        pack = idx.hook_pack_by_id("bare")
        assert pack is not None
        assert pack.category == ""


# ---------------------------------------------------------------------------
# Persona category tests
# ---------------------------------------------------------------------------


class TestPersonaCategories:
    """Test that persona category parsing works correctly."""

    def test_all_personas_have_expected_category(self):
        """Every real persona has the correct ## Category value."""
        expected = {
            "architect": "Software Development",
            "ba": "Software Development",
            "change-management": "Business Operations",
            "code-quality-reviewer": "Software Development",
            "compliance-risk": "Compliance & Legal",
            "customer-success": "Business Operations",
            "data-analyst": "Data & Analytics",
            "data-engineer": "Software Development",
            "database-administrator": "Software Development",
            "developer": "Software Development",
            "devops-release": "Software Development",
            "financial-operations": "Business Operations",
            "integrator-merge-captain": "Software Development",
            "legal-counsel": "Business Operations",
            "mobile-developer": "Software Development",
            "platform-sre-engineer": "Software Development",
            "product-owner": "Business Operations",
            "researcher-librarian": "Data & Analytics",
            "sales-engineer": "Business Operations",
            "security-engineer": "Compliance & Legal",
            "team-lead": "Software Development",
            "tech-qa": "Software Development",
            "technical-writer": "Data & Analytics",
            "ux-ui-designer": "Software Development",
        }
        idx = build_library_index(LIBRARY_ROOT)
        for persona in idx.personas:
            assert persona.id in expected, f"{persona.id} not in expected map"
            assert persona.category == expected[persona.id], (
                f"{persona.id}: expected {expected[persona.id]!r}, "
                f"got {persona.category!r}"
            )

    def test_category_from_persona_md(self, tmp_path: Path):
        """Test category parsing from a persona.md with Category header."""
        persona_dir = tmp_path / "personas" / "my-persona"
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text(
            "# Persona: My Persona\n\n## Category\nEngineering\n\n## Role\nTest\n"
        )
        idx = build_library_index(tmp_path)
        p = idx.persona_by_id("my-persona")
        assert p is not None
        assert p.category == "Engineering"

    def test_no_category_defaults_empty(self, tmp_path: Path):
        """Personas without a Category header get empty string."""
        persona_dir = tmp_path / "personas" / "bare"
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text("# Persona: Bare\n\n## Role\nTest\n")
        idx = build_library_index(tmp_path)
        p = idx.persona_by_id("bare")
        assert p is not None
        assert p.category == ""

    def test_no_persona_md_defaults_empty(self, tmp_path: Path):
        """Personas without a persona.md file get empty category."""
        persona_dir = tmp_path / "personas" / "minimal"
        persona_dir.mkdir(parents=True)
        idx = build_library_index(tmp_path)
        p = idx.persona_by_id("minimal")
        assert p is not None
        assert p.category == ""

    def test_category_case_insensitive_heading(self, tmp_path: Path):
        """## category (lowercase) should also be parsed."""
        persona_dir = tmp_path / "personas" / "lower"
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text(
            "# Persona\n\n## category\nOperations\n"
        )
        idx = build_library_index(tmp_path)
        p = idx.persona_by_id("lower")
        assert p is not None
        assert p.category == "Operations"

    def test_category_with_whitespace(self, tmp_path: Path):
        """Category value should be stripped of leading/trailing whitespace."""
        persona_dir = tmp_path / "personas" / "spaced"
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text(
            "# Persona\n\n## Category\n  Leadership  \n"
        )
        idx = build_library_index(tmp_path)
        p = idx.persona_by_id("spaced")
        assert p is not None
        assert p.category == "Leadership"
