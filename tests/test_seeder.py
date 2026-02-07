"""Tests for foundry_app.services.seeder.seed_tasks."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    HooksConfig,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    StageResult,
    TeamConfig,
)
from foundry_app.services.seeder import seed_tasks


def _make_spec(
    personas: list[str] | None = None,
    stacks: list[str] | None = None,
    project_name: str = "Test Project",
    slug: str = "test-project",
) -> CompositionSpec:
    """Build a minimal CompositionSpec for seeder tests."""
    if personas is None:
        personas = []
    if stacks is None:
        stacks = []
    return CompositionSpec(
        project=ProjectIdentity(name=project_name, slug=slug),
        stacks=[StackSelection(id=sid) for sid in stacks],
        team=TeamConfig(personas=[PersonaSelection(id=pid) for pid in personas]),
        hooks=HooksConfig(),
    )


# ---- Test 1: Creates seeded-tasks.md file ----


def test_creates_seeded_tasks_file(tmp_path: Path):
    """seed_tasks should create a seeded-tasks.md file in the tasks directory."""
    spec = _make_spec(personas=["developer"])
    tasks_dir = tmp_path / "tasks"

    seed_tasks(spec, tasks_dir)

    assert (tasks_dir / "seeded-tasks.md").is_file()


# ---- Test 2: Returns StageResult with seeded-tasks.md in wrote list ----


def test_returns_stage_result_with_wrote(tmp_path: Path):
    """seed_tasks should return a StageResult listing seeded-tasks.md."""
    spec = _make_spec(personas=["developer"])
    tasks_dir = tmp_path / "tasks"

    result = seed_tasks(spec, tasks_dir)

    assert isinstance(result, StageResult)
    assert "seeded-tasks.md" in result.wrote


# ---- Test 3: Includes tasks for selected personas only ----


def test_includes_only_selected_persona_tasks(tmp_path: Path):
    """seed_tasks should include tasks only for personas present in the spec."""
    spec = _make_spec(personas=["developer", "tech-qa"])
    tasks_dir = tmp_path / "tasks"

    seed_tasks(spec, tasks_dir)

    content = (tasks_dir / "seeded-tasks.md").read_text()
    # developer and tech-qa tasks should be present
    assert "**Owner:** developer" in content
    assert "**Owner:** tech-qa" in content
    # ba and architect not selected, so their tasks should be absent
    assert "**Owner:** ba" not in content
    assert "**Owner:** architect" not in content


# ---- Test 4: Primary wave personas get tasks in correct order ----


def test_primary_wave_order(tmp_path: Path):
    """Primary wave tasks (ba, architect, developer, tech-qa) should appear in order."""
    spec = _make_spec(personas=["ba", "architect", "developer", "tech-qa"])
    tasks_dir = tmp_path / "tasks"

    seed_tasks(spec, tasks_dir)

    content = (tasks_dir / "seeded-tasks.md").read_text()
    ba_pos = content.index("**Owner:** ba")
    architect_pos = content.index("**Owner:** architect")
    developer_pos = content.index("**Owner:** developer")
    tech_qa_pos = content.index("**Owner:** tech-qa")
    assert ba_pos < architect_pos < developer_pos < tech_qa_pos


# ---- Test 5: Parallel lane personas get tasks ----


def test_parallel_lane_personas_get_tasks(tmp_path: Path):
    """Parallel lane personas should each get their seeded tasks."""
    parallel = ["security-engineer", "devops-release", "code-quality-reviewer", "technical-writer"]
    spec = _make_spec(personas=parallel)
    tasks_dir = tmp_path / "tasks"

    seed_tasks(spec, tasks_dir)

    content = (tasks_dir / "seeded-tasks.md").read_text()
    assert "**Owner:** security-engineer" in content
    assert "**Owner:** devops-release" in content
    assert "**Owner:** code-quality-reviewer" in content
    assert "**Owner:** technical-writer" in content


# ---- Test 6: Unknown persona produces no tasks but doesn't crash ----


def test_unknown_persona_produces_no_tasks(tmp_path: Path):
    """A persona not in _TASK_WAVES (e.g. ux-ui-designer) should produce no tasks, not crash."""
    spec = _make_spec(personas=["ux-ui-designer", "developer"])
    tasks_dir = tmp_path / "tasks"

    result = seed_tasks(spec, tasks_dir)

    content = (tasks_dir / "seeded-tasks.md").read_text()
    assert isinstance(result, StageResult)
    # developer tasks present
    assert "**Owner:** developer" in content
    # ux-ui-designer has no entry in _TASK_WAVES, so no tasks for it
    assert "**Owner:** ux-ui-designer" not in content


# ---- Test 7: Empty personas list produces file with just header ----


def test_empty_personas_produces_header_only(tmp_path: Path):
    """An empty personas list should still create the file with the header section."""
    spec = _make_spec(personas=[], project_name="Empty Team")
    tasks_dir = tmp_path / "tasks"

    result = seed_tasks(spec, tasks_dir)

    assert isinstance(result, StageResult)
    assert "seeded-tasks.md" in result.wrote
    content = (tasks_dir / "seeded-tasks.md").read_text()
    assert "# Seeded Tasks: Empty Team" in content
    # No owner lines should appear
    assert "**Owner:**" not in content


# ---- Test 8: Task content includes owner, goal, outputs, dependencies, DoD ----


def test_task_content_has_required_sections(tmp_path: Path):
    """Each seeded task should contain Owner, Goal, Outputs, Dependencies, and DoD."""
    spec = _make_spec(personas=["ba"])
    tasks_dir = tmp_path / "tasks"

    seed_tasks(spec, tasks_dir)

    content = (tasks_dir / "seeded-tasks.md").read_text()
    # Check that the first BA task has all required fields
    assert "**Owner:** ba" in content
    assert "**Goal:**" in content
    assert "**Outputs:**" in content
    assert "**Dependencies:**" in content
    assert "**Definition of Done:**" in content
    # DoD should contain checklist items
    assert "- [ ]" in content


# ---- Test 9: Kickoff mode creates single team-lead task ----


def test_kickoff_mode_creates_kickoff_task(tmp_path: Path):
    """seed_tasks with mode='kickoff' should create a single kickoff task."""
    spec = _make_spec(personas=["developer", "architect"], stacks=["python"])
    tasks_dir = tmp_path / "tasks"

    result = seed_tasks(spec, tasks_dir, mode="kickoff")

    assert isinstance(result, StageResult)
    assert "seeded-tasks.md" in result.wrote
    content = (tasks_dir / "seeded-tasks.md").read_text()
    assert "kickoff" in content.lower()
    assert "team-lead" in content
    assert "developer, architect" in content
    assert "python" in content
    assert "- [ ]" in content


# ---- Test 10: Kickoff mode has no per-role tasks ----


def test_kickoff_mode_no_per_role_tasks(tmp_path: Path):
    """seed_tasks with mode='kickoff' should not contain per-role Owner lines."""
    spec = _make_spec(personas=["ba", "developer"])
    tasks_dir = tmp_path / "tasks"

    seed_tasks(spec, tasks_dir, mode="kickoff")

    content = (tasks_dir / "seeded-tasks.md").read_text()
    assert "**Owner:** ba" not in content
    assert "**Owner:** developer" not in content
    assert "**Owner:** team-lead" in content
