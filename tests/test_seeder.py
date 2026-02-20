"""Tests for foundry_app.services.seeder — starter task generation."""

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    PersonaSelection,
    ProjectIdentity,
    SeedMode,
    StackSelection,
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
        stacks=[StackSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


def _read_index(output: Path) -> str:
    """Read the generated task index file."""
    return (output / "ai" / "tasks" / "_index.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Basic generation
# ---------------------------------------------------------------------------


class TestBasicGeneration:

    def test_creates_task_index_file(self, tmp_path: Path):
        result = seed_tasks(_make_spec(), tmp_path)
        assert (tmp_path / "ai" / "tasks" / "_index.md").is_file()
        assert "ai/tasks/_index.md" in result.wrote

    def test_creates_tasks_directory(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        assert (tmp_path / "ai" / "tasks").is_dir()

    def test_returns_stage_result(self, tmp_path: Path):
        result = seed_tasks(_make_spec(), tmp_path)
        assert len(result.wrote) == 1
        assert result.warnings == []

    def test_index_has_header(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        content = _read_index(tmp_path)
        assert "# Task Index" in content

    def test_index_has_table_header(self, tmp_path: Path):
        seed_tasks(_make_spec(), tmp_path)
        content = _read_index(tmp_path)
        assert "| # | Task | Owner | Status |" in content


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
        content = _read_index(tmp_path)
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
        content = _read_index(tmp_path)
        assert "developer" in content
        assert "architect" in content

    def test_team_lead_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="team-lead")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "team-lead" in content
        assert "Review project composition" in content

    def test_ba_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="ba")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "ba" in content
        assert "Gather and document initial project requirements" in content

    def test_tech_qa_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="tech-qa")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "tech-qa" in content
        assert "Create test plan template" in content

    def test_code_quality_reviewer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="code-quality-reviewer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "code-quality-reviewer" in content
        assert "Define code review standards" in content

    def test_devops_release_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="devops-release")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "devops-release" in content
        assert "CI/CD pipeline" in content

    def test_security_engineer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="security-engineer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "security-engineer" in content
        assert "threat model" in content

    def test_compliance_risk_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="compliance-risk")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "compliance-risk" in content
        assert "regulatory requirements" in content

    def test_researcher_librarian_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="researcher-librarian")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "researcher-librarian" in content
        assert "decision matrix" in content

    def test_technical_writer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="technical-writer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "technical-writer" in content
        assert "README" in content

    def test_ux_ui_designer_tasks(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="ux-ui-designer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
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
        content = _read_index(tmp_path)
        assert "integrator-merge-captain" in content
        assert "branch strategy" in content

    def test_detailed_has_multiple_tasks_per_persona(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        # Developer should have 3 tasks in detailed mode
        lines = [l for l in content.splitlines() if "developer" in l and l.startswith("|")]
        assert len(lines) == 3


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
        content = _read_index(tmp_path)
        lines = [l for l in content.splitlines() if "developer" in l and l.startswith("|")]
        assert len(lines) == 1

    def test_kickoff_developer_task(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            generation=GenerationOptions(seed_mode=SeedMode.KICKOFF),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "Set up development environment" in content

    def test_kickoff_team_lead_task(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="team-lead")]),
            generation=GenerationOptions(seed_mode=SeedMode.KICKOFF),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        assert "Review composition and create initial backlog" in content


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_no_personas_warns(self, tmp_path: Path):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = seed_tasks(spec, tmp_path)
        assert any("No personas selected" in w for w in result.warnings)

    def test_no_personas_still_creates_file(self, tmp_path: Path):
        spec = _make_spec(team=TeamConfig(personas=[]))
        seed_tasks(spec, tmp_path)
        assert (tmp_path / "ai" / "tasks" / "_index.md").is_file()

    def test_unknown_persona_warns(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="unknown-role")]),
        )
        result = seed_tasks(spec, tmp_path)
        assert any("No seed task templates" in w for w in result.warnings)

    def test_unknown_persona_creates_file(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="unknown-role")]),
        )
        seed_tasks(spec, tmp_path)
        assert (tmp_path / "ai" / "tasks" / "_index.md").is_file()

    def test_task_numbers_are_sequential(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        task_lines = [
            l for l in content.splitlines()
            if l.startswith("| ") and not l.startswith("| #") and not l.startswith("|---")
        ]
        for i, line in enumerate(task_lines, 1):
            assert line.startswith(f"| {i} |")

    def test_gapless_numbering_with_mixed_personas(self, tmp_path: Path):
        """Task numbers are contiguous 1..N even when unknown personas are in the team."""
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="unknown-role"),
                PersonaSelection(id="architect"),
            ]),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        task_lines = [
            l for l in content.splitlines()
            if l.startswith("| ") and not l.startswith("| #") and not l.startswith("|---")
        ]
        numbers = [int(l.split("|")[1].strip()) for l in task_lines]
        assert numbers == list(range(1, len(numbers) + 1))

    def test_existing_directory_not_error(self, tmp_path: Path):
        (tmp_path / "ai" / "tasks").mkdir(parents=True)
        result = seed_tasks(_make_spec(), tmp_path)
        assert len(result.wrote) == 1

    def test_output_dir_accepts_string(self, tmp_path: Path):
        result = seed_tasks(_make_spec(), str(tmp_path))
        assert len(result.wrote) == 1


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
        content = _read_index(tmp_path)
        # 3 tasks per persona × 13 personas = 39 tasks
        task_lines = [
            l for l in content.splitlines()
            if l.startswith("| ") and not l.startswith("| #") and not l.startswith("|---")
        ]
        assert len(task_lines) == 39
        assert result.warnings == []

    def test_full_team_kickoff(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id=pid) for pid in _ALL_PERSONA_IDS]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.KICKOFF),
        )
        result = seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        # 1 task per persona × 13 personas = 13 tasks
        task_lines = [
            l for l in content.splitlines()
            if l.startswith("| ") and not l.startswith("| #") and not l.startswith("|---")
        ]
        assert len(task_lines) == 13
        assert result.warnings == []

    def test_all_personas_present_in_output(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id=pid) for pid in _ALL_PERSONA_IDS]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        seed_tasks(spec, tmp_path)
        content = _read_index(tmp_path)
        for persona_id in _ALL_PERSONA_IDS:
            assert persona_id in content, f"Missing tasks for persona '{persona_id}'"

    def test_no_warnings_for_any_library_persona(self, tmp_path: Path):
        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id=pid) for pid in _ALL_PERSONA_IDS]
            ),
            generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
        )
        result = seed_tasks(spec, tmp_path)
        assert result.warnings == [], f"Unexpected warnings: {result.warnings}"
