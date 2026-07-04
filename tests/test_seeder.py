"""Tests for foundry_app.services.seeder — starter bean + seeded tasks."""

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseSelection,
    GenerationOptions,
    PersonaSelection,
    ProjectIdentity,
    SeedMode,
    TeamConfig,
)
from foundry_app.services.seeder import seed_tasks

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a CompositionSpec with sensible defaults."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        expertise=[ExpertiseSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


def _bean_dir(output: Path) -> Path:
    return output / "ai" / "beans" / "BEAN-001-bootstrap"


def _read_bean(output: Path) -> str:
    return (_bean_dir(output) / "bean.md").read_text(encoding="utf-8")


def _task_files(output: Path) -> list[Path]:
    return sorted((_bean_dir(output) / "tasks").glob("*.md"))


def _read_tasks_concat(output: Path) -> str:
    return "\n".join(
        p.read_text(encoding="utf-8") for p in _task_files(output)
    )


def _backlog_index(output: Path) -> Path:
    return output / "ai" / "beans" / "_index.md"


# ---------------------------------------------------------------------------
# Basic generation
# ---------------------------------------------------------------------------


class TestBasicGeneration:

    def test_creates_starter_bean(self, tmp_path: Path):
        result = seed_tasks(_make_spec(), tmp_path)
        assert (_bean_dir(tmp_path) / "bean.md").is_file()
        assert "ai/beans/BEAN-001-bootstrap/bean.md" in result.wrote

    def test_creates_tasks_directory(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        assert (_bean_dir(tmp_path) / "tasks").is_dir()

    def test_does_not_write_ai_tasks_index(self, tmp_path: Path):
        """Regression: the orphan ai/tasks/_index.md must not reappear."""
        seed_tasks(_make_spec(), tmp_path)
        assert not (tmp_path / "ai" / "tasks" / "_index.md").exists()

    def test_returns_stage_result(self, tmp_path: Path):
        result = seed_tasks(_make_spec(), tmp_path)
        assert len(result.wrote) >= 1
        assert result.warnings == []

    def test_bean_status_is_approved(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        assert "| **Status** | Approved |" in _read_bean(tmp_path)

    def test_bean_title_present(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        assert "# BEAN-001: Bootstrap Project Team" in _read_bean(tmp_path)


# ---------------------------------------------------------------------------
# Backlog index upsert
# ---------------------------------------------------------------------------


class TestBacklogIndex:

    def test_index_created_when_missing(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        content = _backlog_index(tmp_path).read_text(encoding="utf-8")
        assert "| BEAN-001 |" in content
        assert "Bootstrap Project Team" in content

    def test_index_preserves_existing_rows(self, tmp_path: Path):
        index_path = _backlog_index(tmp_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(
            "# Bean Backlog\n\n## Backlog\n\n"
            "| Bean ID | Title | Category | Priority | Status | Owner |\n"
            "|---------|-------|----------|----------|--------|-------|\n"
            "| BEAN-042 | Existing | App | Low | Approved | alice |\n",
            encoding="utf-8",
        )
        seed_tasks(_make_spec(), tmp_path)
        content = index_path.read_text(encoding="utf-8")
        assert "BEAN-042" in content
        assert "BEAN-001" in content

    def test_index_not_duplicated_on_rerun(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        seed_tasks(_make_spec(), tmp_path)
        content = _backlog_index(tmp_path).read_text(encoding="utf-8")
        # BEAN-001 appears exactly once in the backlog rows
        assert content.count("| BEAN-001 |") == 1


# ---------------------------------------------------------------------------
# Charter reference vs fallback
# ---------------------------------------------------------------------------


class TestCharterReference:

    def test_references_charter_when_present(self, tmp_path: Path):
        charter = tmp_path / "ai" / "context" / "project-charter.md"
        charter.parent.mkdir(parents=True, exist_ok=True)
        charter.write_text("# Project Charter — Test", encoding="utf-8")
        seed_tasks(_make_spec(), tmp_path)
        bean = _read_bean(tmp_path)
        assert "ai/context/project-charter.md" in bean

    def test_generic_fallback_when_charter_absent(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        bean = _read_bean(tmp_path)
        assert "ai/context/project-charter.md" not in bean
        assert "No project charter was scaffolded" in bean


# ---------------------------------------------------------------------------
# Detailed seed mode
# ---------------------------------------------------------------------------


class TestDetailedMode:

    def test_developer_tasks_generated(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "developer" in content
        assert "Set up local development environment" in content

    def test_multiple_personas(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "developer" in content
        assert "architect" in content

    def test_team_lead_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="team-lead")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "team-lead" in content
        assert "Review project composition" in content

    def test_ba_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="ba")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "Gather and document initial project requirements" in content

    def test_tech_qa_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="tech-qa")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "tech-qa" in content
        assert "Create test plan template" in content

    def test_code_quality_reviewer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id="code-quality-reviewer")]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "code-quality-reviewer" in content
        assert "Define code review standards" in content

    def test_devops_release_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="devops-release")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "devops-release" in content
        assert "CI/CD pipeline" in content

    def test_security_engineer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="security-engineer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "security-engineer" in content
        assert "threat model" in content

    def test_compliance_risk_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="compliance-risk")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "compliance-risk" in content
        assert "regulatory requirements" in content

    def test_researcher_librarian_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="researcher-librarian")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "researcher-librarian" in content
        assert "decision matrix" in content

    def test_technical_writer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="technical-writer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "technical-writer" in content
        assert "README" in content

    def test_ux_ui_designer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="ux-ui-designer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "ux-ui-designer" in content
        assert "wireframes" in content

    def test_integrator_merge_captain_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id="integrator-merge-captain")]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "integrator-merge-captain" in content
        assert "branch strategy" in content

    def test_detailed_has_multiple_tasks_per_persona(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        # Developer should have 3 task files in detailed mode
        assert len(_task_files(tmp_path)) == 3


# ---------------------------------------------------------------------------
# Kickoff seed mode
# ---------------------------------------------------------------------------


class TestKickoffMode:

    def test_kickoff_generates_fewer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            generation=GenerationOptions(seed_mode=SeedMode.KICKOFF),
        )
        seed_tasks(spec, tmp_path)
        assert len(_task_files(tmp_path)) == 1

    def test_kickoff_developer_task(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            generation=GenerationOptions(seed_mode=SeedMode.KICKOFF),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "Set up development environment" in content

    def test_kickoff_team_lead_task(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="team-lead")]),
            generation=GenerationOptions(seed_mode=SeedMode.KICKOFF),
        )
        seed_tasks(spec, tmp_path)
        content = _read_tasks_concat(tmp_path)
        assert "Review composition and create initial backlog" in content


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_no_personas_warns(self, tmp_path: Path):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = seed_tasks(spec, tmp_path)
        assert any("No personas selected" in w for w in result.warnings)

    def test_no_personas_still_creates_bean(self, tmp_path: Path):
        spec = _make_spec(team=TeamConfig(personas=[]))
        seed_tasks(spec, tmp_path)
        assert (_bean_dir(tmp_path) / "bean.md").is_file()
        assert _task_files(tmp_path) == []

    def test_unknown_persona_warns(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="unknown-role")]),
        )
        result = seed_tasks(spec, tmp_path)
        assert any("No seed task templates" in w for w in result.warnings)

    def test_unknown_persona_creates_bean(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="unknown-role")]),
        )
        seed_tasks(spec, tmp_path)
        assert (_bean_dir(tmp_path) / "bean.md").is_file()

    def test_task_numbers_are_sequential(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        files = _task_files(tmp_path)
        # Filenames begin with zero-padded sequential numbers
        for i, path in enumerate(files, start=1):
            assert path.name.startswith(f"{i:02d}-"), (
                f"Expected prefix {i:02d}-, got {path.name}"
            )

    def test_gapless_numbering_with_mixed_personas(self, tmp_path: Path):
        """Task numbers are contiguous even when unknown personas appear."""
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="unknown-role"),
                PersonaSelection(id="architect"),
            ]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        files = _task_files(tmp_path)
        numbers = [int(p.name.split("-", 1)[0]) for p in files]
        assert numbers == list(range(1, len(numbers) + 1))

    def test_existing_directory_not_error(self, tmp_path: Path):
        (_bean_dir(tmp_path) / "tasks").mkdir(parents=True)
        result = seed_tasks(_make_spec(), tmp_path)
        assert result.wrote

    def test_output_dir_accepts_string(self, tmp_path: Path):
        result = seed_tasks(_make_spec(), str(tmp_path))
        assert result.wrote


# ---------------------------------------------------------------------------
# All personas combined
# ---------------------------------------------------------------------------


_ALL_PERSONA_IDS = [
    "team-lead",
    "ba",
    "architect",
    "developer",
    "tech-qa",
    "code-quality-reviewer",
    "devops-release",
    "security-engineer",
    "compliance-risk",
    "researcher-librarian",
    "technical-writer",
    "ux-ui-designer",
    "integrator-merge-captain",
]


class TestAllPersonas:

    def test_full_team_detailed(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id=pid) for pid in _ALL_PERSONA_IDS]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        result = seed_tasks(spec, tmp_path)
        # 3 tasks per persona × 13 personas = 39 task files
        assert len(_task_files(tmp_path)) == 39
        assert result.warnings == []

    def test_full_team_kickoff(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id=pid) for pid in _ALL_PERSONA_IDS]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.KICKOFF),
        )
        result = seed_tasks(spec, tmp_path)
        # 1 task per persona × 13 personas = 13 task files
        assert len(_task_files(tmp_path)) == 13
        assert result.warnings == []

    def test_all_personas_present_in_task_filenames(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id=pid) for pid in _ALL_PERSONA_IDS]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        filenames = " ".join(p.name for p in _task_files(tmp_path))
        for persona_id in _ALL_PERSONA_IDS:
            assert persona_id in filenames, (
                f"Missing task files for persona '{persona_id}'"
            )

    def test_no_warnings_for_any_library_persona(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id=pid) for pid in _ALL_PERSONA_IDS]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        result = seed_tasks(spec, tmp_path)
        assert result.warnings == [], f"Unexpected warnings: {result.warnings}"


class TestVddReadyAcceptanceCriteria:
    """SPEC-013: seeded ACs carry VDD evidence prefixes so /vdd can reach a
    programmatic verdict on a freshly generated project."""

    def test_all_seed_acs_are_programmatic(self, tmp_path: Path):
        from foundry_app.services.vdd import parse_acceptance_criteria

        seed_tasks(_make_spec(), tmp_path)
        criteria = parse_acceptance_criteria(_read_bean(tmp_path))
        assert criteria, "seed bean must declare acceptance criteria"
        kinds = {c.kind for c in criteria}
        assert "manual" not in kinds, (
            f"seed ACs must all be machine-checkable, got kinds: {kinds}"
        )

    def test_seed_acs_reference_expected_evidence(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        bean = _read_bean(tmp_path)
        assert "(file-contains:ai/beans/BEAN-001-bootstrap/tasks/*.md::" in bean
        assert "(file:ai/outputs/*/*.md)" in bean
        assert "(file:ai/beans/BEAN-002-*/bean.md)" in bean
