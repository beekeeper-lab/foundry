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
    "aws-limited-ops",
    "aws-read-only",
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
    "pre-commit-lint-js",
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
# Hook pack conflicts_with parsing (BEAN-262)
# ---------------------------------------------------------------------------


class TestHookPackConflictsWith:
    """Test that ``## Conflicts With`` is parsed into HookPackInfo.conflicts_with."""

    def test_az_pair_declares_mutual_conflict(self):
        idx = build_library_index(LIBRARY_ROOT)
        read_only = idx.hook_pack_by_id("az-read-only")
        limited = idx.hook_pack_by_id("az-limited-ops")
        assert read_only is not None and limited is not None
        assert "az-limited-ops" in read_only.conflicts_with
        assert "az-read-only" in limited.conflicts_with

    def test_aws_pair_declares_mutual_conflict(self):
        idx = build_library_index(LIBRARY_ROOT)
        read_only = idx.hook_pack_by_id("aws-read-only")
        limited = idx.hook_pack_by_id("aws-limited-ops")
        assert read_only is not None and limited is not None
        assert "aws-limited-ops" in read_only.conflicts_with
        assert "aws-read-only" in limited.conflicts_with

    def test_non_conflicting_pack_has_empty_list(self):
        idx = build_library_index(LIBRARY_ROOT)
        pack = idx.hook_pack_by_id("pre-commit-lint")
        assert pack is not None
        assert pack.conflicts_with == []

    def test_parse_conflicts_from_tmp_file(self, tmp_path: Path):
        hooks_dir = tmp_path / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "my-hook.md").write_text(
            "# Hook Pack: My Hook\n\n## Category\ncustom\n\n"
            "## Conflicts With\n\n- `other-pack` — reason here\n"
            "- `third-pack` — another reason\n"
        )
        idx = build_library_index(tmp_path)
        pack = idx.hook_pack_by_id("my-hook")
        assert pack is not None
        assert pack.conflicts_with == ["other-pack", "third-pack"]

    def test_no_conflicts_section_defaults_empty(self, tmp_path: Path):
        hooks_dir = tmp_path / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "bare.md").write_text("# Hook Pack: Bare\n\n## Purpose\nTest\n")
        idx = build_library_index(tmp_path)
        pack = idx.hook_pack_by_id("bare")
        assert pack is not None
        assert pack.conflicts_with == []

    def test_section_ends_at_next_heading(self, tmp_path: Path):
        hooks_dir = tmp_path / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "scoped.md").write_text(
            "# Hook Pack: Scoped\n\n"
            "## Conflicts With\n\n- `pack-a`\n\n"
            "## Stack Signals\n\n- `fake-pack-not-a-conflict`\n"
        )
        idx = build_library_index(tmp_path)
        pack = idx.hook_pack_by_id("scoped")
        assert pack is not None
        assert pack.conflicts_with == ["pack-a"]


# ---------------------------------------------------------------------------
# Hook pack posture_compatibility parsing (BEAN-263)
# ---------------------------------------------------------------------------


class TestHookPackPostureCompatibility:
    """Test that ``## Posture Compatibility`` is parsed into HookPackInfo."""

    def test_compliance_gate_excludes_baseline_and_hardened(self):
        idx = build_library_index(LIBRARY_ROOT)
        pack = idx.hook_pack_by_id("compliance-gate")
        assert pack is not None
        compat = pack.posture_compatibility
        assert compat["baseline"]["included"].lower() == "no"
        assert compat["hardened"]["included"].lower() == "no"
        assert compat["regulated"]["included"].lower() == "yes"
        assert compat["regulated"]["default_mode"] == "enforcing"

    def test_git_commit_branch_supports_every_posture(self):
        idx = build_library_index(LIBRARY_ROOT)
        pack = idx.hook_pack_by_id("git-commit-branch")
        assert pack is not None
        for posture in ("baseline", "hardened", "regulated"):
            assert pack.posture_compatibility[posture]["included"].lower() == "yes"

    def test_every_real_pack_except_policy_has_three_postures(self):
        idx = build_library_index(LIBRARY_ROOT)
        for pack in idx.hook_packs:
            if pack.id == "hook-policy":
                continue
            assert set(pack.posture_compatibility.keys()) == {
                "baseline", "hardened", "regulated",
            }, f"{pack.id} missing postures"

    def test_parse_yes_no_optional_and_conditional(self, tmp_path: Path):
        hooks_dir = tmp_path / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "mixed.md").write_text(
            "# Hook Pack: Mixed\n\n"
            "## Posture Compatibility\n\n"
            "| Posture | Included | Default Mode |\n"
            "|---------|----------|--------------|\n"
            "| `baseline` | No | — |\n"
            "| `hardened` | Optional | advisory |\n"
            "| `regulated` | Yes (when strict) | enforcing |\n"
        )
        idx = build_library_index(tmp_path)
        pack = idx.hook_pack_by_id("mixed")
        assert pack is not None
        assert pack.posture_compatibility == {
            "baseline": {"included": "No", "default_mode": "—"},
            "hardened": {"included": "Optional", "default_mode": "advisory"},
            "regulated": {
                "included": "Yes (when strict)",
                "default_mode": "enforcing",
            },
        }

    def test_no_section_defaults_empty(self, tmp_path: Path):
        hooks_dir = tmp_path / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "bare.md").write_text("# Hook Pack: Bare\n\n## Purpose\nT\n")
        idx = build_library_index(tmp_path)
        pack = idx.hook_pack_by_id("bare")
        assert pack is not None
        assert pack.posture_compatibility == {}

    def test_section_terminates_at_next_heading(self, tmp_path: Path):
        hooks_dir = tmp_path / "claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "scoped.md").write_text(
            "# Hook Pack: Scoped\n\n"
            "## Posture Compatibility\n\n"
            "| Posture | Included | Default Mode |\n"
            "|---------|----------|--------------|\n"
            "| `baseline` | Yes | enforcing |\n\n"
            "## Stack Signals\n\n"
            "| Posture | Included | Default Mode |\n"
            "|---------|----------|--------------|\n"
            "| `bogus` | Yes | enforcing |\n"
        )
        idx = build_library_index(tmp_path)
        pack = idx.hook_pack_by_id("scoped")
        assert pack is not None
        assert set(pack.posture_compatibility.keys()) == {"baseline"}


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


class TestExpertiseCategories:
    """Test that expertise category parsing works correctly."""

    def test_category_from_conventions_md(self, tmp_path: Path):
        """Test category parsing from conventions.md with Category header."""
        expertise_dir = tmp_path / "expertise" / "python"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Python\n\n## Category\nLanguages\n\n## Defaults\nSome content\n"
        )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("python")
        assert e is not None
        assert e.category == "Languages"

    def test_no_category_defaults_empty(self, tmp_path: Path):
        """Expertise without a Category header gets empty string."""
        expertise_dir = tmp_path / "expertise" / "bare"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Bare\n\n## Defaults\nSome content\n"
        )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("bare")
        assert e is not None
        assert e.category == ""

    def test_no_conventions_md_defaults_empty(self, tmp_path: Path):
        """Expertise without conventions.md gets empty category."""
        expertise_dir = tmp_path / "expertise" / "minimal"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "other.md").write_text("# Other\n")
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("minimal")
        assert e is not None
        assert e.category == ""

    def test_category_case_insensitive_heading(self, tmp_path: Path):
        """## category (lowercase) should also be parsed."""
        expertise_dir = tmp_path / "expertise" / "lower"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Lower\n\n## category\nInfrastructure\n"
        )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("lower")
        assert e is not None
        assert e.category == "Infrastructure"

    def test_category_fallback_to_first_md(self, tmp_path: Path):
        """When no conventions.md exists, parse category from first .md file."""
        expertise_dir = tmp_path / "expertise" / "fallback"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "alpha.md").write_text(
            "# Alpha\n\n## Category\nBusiness Practices\n\n## Content\nStuff\n"
        )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("fallback")
        assert e is not None
        assert e.category == "Business Practices"

    def test_all_expertise_have_expected_category(self):
        """Every real expertise item has the correct ## Category value."""
        expected = {
            "accessibility-compliance": "Compliance & Governance",
            "api-design": "Architecture & Patterns",
            "aws-cloud-platform": "Infrastructure & Platforms",
            "azure-cloud-platform": "Infrastructure & Platforms",
            "business-intelligence": "Data & ML",
            "change-management": "Business Practices",
            "clean-code": "Architecture & Patterns",
            "customer-enablement": "Business Practices",
            "data-engineering": "Data & ML",
            "devops": "Infrastructure & Platforms",
            "dotnet": "Languages",
            "event-driven-messaging": "Architecture & Patterns",
            "finops": "Business Practices",
            "frontend-build-tooling": "Architecture & Patterns",
            "gcp-cloud-platform": "Infrastructure & Platforms",
            "gdpr-data-privacy": "Compliance & Governance",
            "go": "Languages",
            "hipaa-compliance": "Compliance & Governance",
            "iso-9000": "Compliance & Governance",
            "java": "Languages",
            "kotlin": "Languages",
            "kubernetes": "Infrastructure & Platforms",
            "microservices": "Architecture & Patterns",
            "mlops": "Data & ML",
            "node": "Languages",
            "pci-dss-compliance": "Compliance & Governance",
            "product-strategy": "Business Practices",
            "python": "Languages",
            "python-qt-pyside6": "Languages",
            "react": "Languages",
            "react-native": "Languages",
            "rust": "Languages",
            "sales-engineering": "Business Practices",
            "security": "Compliance & Governance",
            "sox-compliance": "Compliance & Governance",
            "sql-dba": "Data & ML",
            "swift": "Languages",
            "terraform": "Infrastructure & Platforms",
            "typescript": "Languages",
        }
        idx = build_library_index(LIBRARY_ROOT)
        for expertise in idx.expertise:
            assert expertise.id in expected, f"{expertise.id} not in expected map"
            assert expertise.category == expected[expertise.id], (
                f"{expertise.id}: expected {expected[expertise.id]!r}, "
                f"got {expertise.category!r}"
            )

    def test_category_with_whitespace(self, tmp_path: Path):
        """Category value should be stripped of leading/trailing whitespace."""
        expertise_dir = tmp_path / "expertise" / "spaced"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Spaced\n\n## Category\n  Data & ML  \n"
        )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("spaced")
        assert e is not None
        assert e.category == "Data & ML"


class TestExpertiseAppliesTo:
    """ADR-012 / BEAN-259: ``## Applies To`` parser tests."""

    def test_applies_to_parsed_from_conventions_md(self, tmp_path: Path):
        """A populated ``## Applies To`` section is parsed into a list."""
        expertise_dir = tmp_path / "expertise" / "frontend"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Frontend\n\n## Category\nLanguages\n\n"
            "## Applies To\n\n- developer\n- tech-qa\n- ux-ui-designer\n",
        )
        # Add the personas that the section references so the
        # unknown-persona warning doesn't drop them.
        for pid in ("developer", "tech-qa", "ux-ui-designer"):
            (tmp_path / "personas" / pid).mkdir(parents=True)
            (tmp_path / "personas" / pid / "persona.md").write_text(
                f"# Persona: {pid}\n"
            )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("frontend")
        assert e is not None
        assert e.applies_to == ["developer", "tech-qa", "ux-ui-designer"]

    def test_no_applies_to_section_defaults_empty(self, tmp_path: Path):
        """Expertise without an ``## Applies To`` section has applies_to=[]."""
        expertise_dir = tmp_path / "expertise" / "bare"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Bare\n\n## Category\nLanguages\n\n## Defaults\n- foo\n",
        )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("bare")
        assert e is not None
        assert e.applies_to == []

    def test_empty_applies_to_section_returns_empty_list(self, tmp_path: Path):
        """Heading present, no bullets — treated as 'applies to all'."""
        expertise_dir = tmp_path / "expertise" / "empty"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Empty\n\n## Applies To\n\n## Defaults\n- foo\n",
        )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("empty")
        assert e is not None
        assert e.applies_to == []

    def test_applies_to_falls_back_to_first_md(self, tmp_path: Path):
        """Multi-file packs without conventions.md use the first .md alphabetically."""
        expertise_dir = tmp_path / "expertise" / "multi"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "alpha.md").write_text(
            "# Alpha\n\n## Applies To\n\n- developer\n- architect\n",
        )
        (expertise_dir / "beta.md").write_text(
            "# Beta\n\n## Applies To\n\n- tech-qa\n",
        )
        for pid in ("developer", "architect", "tech-qa"):
            (tmp_path / "personas" / pid).mkdir(parents=True)
            (tmp_path / "personas" / pid / "persona.md").write_text(
                f"# Persona: {pid}\n"
            )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("multi")
        assert e is not None
        # Should pick alpha.md, not beta.md
        assert e.applies_to == ["developer", "architect"]

    def test_unknown_persona_id_dropped_with_warning(
        self, tmp_path: Path, caplog,
    ):
        """An ``applies_to`` entry that is not a real persona is dropped and warned."""
        import logging

        expertise_dir = tmp_path / "expertise" / "scoped"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Scoped\n\n## Applies To\n\n- developer\n- bogus-persona\n",
        )
        # Only register `developer` as a real persona.
        (tmp_path / "personas" / "developer").mkdir(parents=True)
        (tmp_path / "personas" / "developer" / "persona.md").write_text(
            "# Persona: Developer\n"
        )
        with caplog.at_level(logging.WARNING):
            idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("scoped")
        assert e is not None
        assert e.applies_to == ["developer"]
        # Warning matches the existing "Persona '<id>' not found" shape.
        assert any(
            "bogus-persona" in record.message
            and "not found" in record.message
            for record in caplog.records
        )

    def test_horizontal_rule_after_bullets_is_ignored(self, tmp_path: Path):
        """A markdown HR (``---``) following the bullets must not be parsed as
        a persona id. Real-world expertise files put a horizontal rule between
        the ``## Applies To`` section and the next heading."""
        expertise_dir = tmp_path / "expertise" / "withhr"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# WithHR\n\n## Applies To\n\n- developer\n- tech-qa\n\n"
            "Some prose paragraph between the section and the rule.\n\n"
            "---\n\n## Defaults\n- foo\n",
        )
        for pid in ("developer", "tech-qa"):
            (tmp_path / "personas" / pid).mkdir(parents=True)
            (tmp_path / "personas" / pid / "persona.md").write_text(
                f"# Persona: {pid}\n"
            )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("withhr")
        assert e is not None
        assert e.applies_to == ["developer", "tech-qa"]

    def test_applies_to_stops_at_next_heading(self, tmp_path: Path):
        """Bullets after the next ``## ...`` heading are not collected."""
        expertise_dir = tmp_path / "expertise" / "bounded"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Bounded\n\n## Applies To\n\n- developer\n\n"
            "## Defaults\n\n- tech-qa\n",
        )
        (tmp_path / "personas" / "developer").mkdir(parents=True)
        (tmp_path / "personas" / "developer" / "persona.md").write_text(
            "# Persona: Developer\n"
        )
        idx = build_library_index(tmp_path)
        e = idx.expertise_by_id("bounded")
        assert e is not None
        assert e.applies_to == ["developer"]

    def test_real_library_curated_applies_to(self):
        """The curated expertise files in the real library have the
        ``## Applies To`` lists set during BEAN-259 implementation."""
        idx = build_library_index(LIBRARY_ROOT)

        python = idx.expertise_by_id("python")
        assert python is not None
        assert "developer" in python.applies_to
        assert "tech-qa" in python.applies_to
        assert "ux-ui-designer" not in python.applies_to
        assert "devops-release" not in python.applies_to

        typescript = idx.expertise_by_id("typescript")
        assert typescript is not None
        assert "developer" in typescript.applies_to
        assert "tech-qa" in typescript.applies_to
        assert "devops-release" not in typescript.applies_to
        assert "ux-ui-designer" not in typescript.applies_to

        react = idx.expertise_by_id("react")
        assert react is not None
        assert "developer" in react.applies_to
        assert "ux-ui-designer" in react.applies_to

        a11y = idx.expertise_by_id("accessibility-compliance")
        assert a11y is not None
        assert "ux-ui-designer" in a11y.applies_to

    def test_unannotated_expertise_default_empty(self):
        """Expertise files in the library without ``## Applies To`` keep
        applies_to=[] — the empty-default rule preserves pre-BEAN-259
        behavior for any non-curated file."""
        idx = build_library_index(LIBRARY_ROOT)
        # `devops` has no ## Applies To section in this commit; it should
        # default to empty, meaning "applies to every persona".
        devops = idx.expertise_by_id("devops")
        assert devops is not None
        assert devops.applies_to == []
