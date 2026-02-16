"""Tests for foundry_app.services.scaffold — directory skeleton creation."""

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    TeamConfig,
)
from foundry_app.services.scaffold import scaffold_project

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


# ---------------------------------------------------------------------------
# Standard directory structure
# ---------------------------------------------------------------------------


class TestStandardStructure:

    def test_creates_project_root(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec()
        scaffold_project(spec, output)
        assert output.is_dir()

    def test_creates_claude_agents_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        assert (output / ".claude" / "agents").is_dir()

    def test_creates_claude_commands_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        assert (output / ".claude" / "commands").is_dir()

    def test_creates_claude_hooks_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        assert (output / ".claude" / "hooks").is_dir()

    def test_creates_claude_skills_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        assert (output / ".claude" / "skills").is_dir()

    def test_creates_ai_context_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        assert (output / "ai" / "context").is_dir()

    def test_creates_ai_outputs_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        assert (output / "ai" / "outputs").is_dir()

    def test_creates_ai_beans_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        assert (output / "ai" / "beans").is_dir()

    def test_creates_ai_tasks_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        assert (output / "ai" / "tasks").is_dir()

    def test_creates_all_standard_dirs(self, tmp_path: Path):
        """Verify the full set of standard directories."""
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        expected = [
            ".claude/agents",
            ".claude/commands",
            ".claude/hooks",
            ".claude/skills",
            "ai/context",
            "ai/outputs",
            "ai/beans",
            "ai/tasks",
        ]
        for d in expected:
            assert (output / d).is_dir(), f"Expected directory {d} not found"


# ---------------------------------------------------------------------------
# Per-persona output directories
# ---------------------------------------------------------------------------


class TestPersonaDirectories:

    def test_creates_persona_output_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        )
        scaffold_project(spec, output)
        assert (output / "ai" / "outputs" / "developer").is_dir()

    def test_creates_multiple_persona_dirs(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
                PersonaSelection(id="tech-qa"),
            ]),
        )
        scaffold_project(spec, output)
        assert (output / "ai" / "outputs" / "developer").is_dir()
        assert (output / "ai" / "outputs" / "architect").is_dir()
        assert (output / "ai" / "outputs" / "tech-qa").is_dir()

    def test_no_personas_creates_base_outputs_dir_only(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(team=TeamConfig(personas=[]))
        scaffold_project(spec, output)
        assert (output / "ai" / "outputs").is_dir()
        # Only the base ai/outputs dir, no subdirs
        subdirs = list((output / "ai" / "outputs").iterdir())
        assert subdirs == []


# ---------------------------------------------------------------------------
# StageResult
# ---------------------------------------------------------------------------


class TestStageResult:

    def test_result_lists_created_directories(self, tmp_path: Path):
        output = tmp_path / "my-project"
        result = scaffold_project(_make_spec(), output)
        assert len(result.wrote) > 0
        assert "." in result.wrote  # project root
        assert ".claude/agents" in result.wrote
        assert "ai/context" in result.wrote

    def test_result_includes_persona_dirs(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
        )
        result = scaffold_project(spec, output)
        assert "ai/outputs/developer" in result.wrote
        assert "ai/outputs/architect" in result.wrote

    def test_result_has_no_warnings_with_personas(self, tmp_path: Path):
        output = tmp_path / "my-project"
        result = scaffold_project(_make_spec(), output)
        assert result.warnings == []

    def test_result_warns_when_no_personas(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = scaffold_project(spec, output)
        assert len(result.warnings) == 1
        assert "No personas" in result.warnings[0]

    def test_result_wrote_count_matches_dirs_created(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        )
        result = scaffold_project(spec, output)
        # root + 4 .claude dirs + 4 ai dirs + 1 persona dir = 10
        assert len(result.wrote) == 10


# ---------------------------------------------------------------------------
# Overlay mode (existing directories)
# ---------------------------------------------------------------------------


class TestOverlayMode:

    def test_existing_root_not_duplicated_in_result(self, tmp_path: Path):
        output = tmp_path / "my-project"
        output.mkdir()
        result = scaffold_project(_make_spec(), output)
        # Root already existed, so "." should NOT be in wrote
        assert "." not in result.wrote

    def test_existing_claude_dir_skipped(self, tmp_path: Path):
        output = tmp_path / "my-project"
        (output / ".claude" / "agents").mkdir(parents=True)
        result = scaffold_project(_make_spec(), output)
        assert ".claude/agents" not in result.wrote
        # But other .claude dirs should still be created
        assert ".claude/commands" in result.wrote
        assert ".claude/hooks" in result.wrote

    def test_existing_persona_dir_skipped(self, tmp_path: Path):
        output = tmp_path / "my-project"
        (output / "ai" / "outputs" / "developer").mkdir(parents=True)
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
        )
        result = scaffold_project(spec, output)
        assert "ai/outputs/developer" not in result.wrote
        assert "ai/outputs/architect" in result.wrote

    def test_overlay_does_not_destroy_existing_files(self, tmp_path: Path):
        output = tmp_path / "my-project"
        (output / "ai" / "context").mkdir(parents=True)
        existing_file = output / "ai" / "context" / "existing.md"
        existing_file.write_text("keep me")
        scaffold_project(_make_spec(), output)
        assert existing_file.read_text() == "keep me"

    def test_fully_scaffolded_project_returns_empty_wrote(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        )
        # First scaffold creates everything
        scaffold_project(spec, output)
        # Second scaffold should create nothing new
        result = scaffold_project(spec, output)
        assert result.wrote == []

    def test_overlay_adds_new_persona_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec1 = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        )
        scaffold_project(spec1, output)
        # Now add a persona
        spec2 = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
        )
        result = scaffold_project(spec2, output)
        assert "ai/outputs/architect" in result.wrote
        assert "ai/outputs/developer" not in result.wrote


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_accepts_string_output_dir(self, tmp_path: Path):
        output = str(tmp_path / "my-project")
        result = scaffold_project(_make_spec(), output)
        assert len(result.wrote) > 0
        assert Path(output).is_dir()

    def test_accepts_path_output_dir(self, tmp_path: Path):
        output = tmp_path / "my-project"
        result = scaffold_project(_make_spec(), output)
        assert len(result.wrote) > 0

    def test_deeply_nested_output_dir(self, tmp_path: Path):
        output = tmp_path / "a" / "b" / "c" / "project"
        result = scaffold_project(_make_spec(), output)
        assert output.is_dir()
        assert len(result.wrote) > 0

    def test_empty_stacks_still_creates_standard_dirs(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(stacks=[])
        scaffold_project(spec, output)
        assert (output / ".claude" / "agents").is_dir()
        assert (output / "ai" / "context").is_dir()

    def test_many_personas(self, tmp_path: Path):
        output = tmp_path / "my-project"
        personas = [PersonaSelection(id=f"persona-{i}") for i in range(10)]
        spec = _make_spec(team=TeamConfig(personas=personas))
        result = scaffold_project(spec, output)
        for i in range(10):
            assert (output / "ai" / "outputs" / f"persona-{i}").is_dir()
            assert f"ai/outputs/persona-{i}" in result.wrote
