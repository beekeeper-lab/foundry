"""Tests for foundry_app.services.scaffold — directory skeleton creation."""

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseSelection,
    PersonaSelection,
    ProjectIdentity,
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
        expertise=[ExpertiseSelection(id="python")],
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
            "ai/generated/members",
            "ai/generated/expertise",
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
        # root + 4 .claude dirs + 7 ai dirs (incl. ai/team) + 1 persona dir
        # + ai/team/composition.yml + README.md + project-charter.md
        # + MEMORY.md (SPEC-009) = 17
        assert len(result.wrote) == 17


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

    def test_empty_expertise_still_creates_standard_dirs(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(expertise=[])
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


# ---------------------------------------------------------------------------
# Composition snapshot + starter README (BEAN-244)
# ---------------------------------------------------------------------------


class TestCompositionSnapshot:
    """Scaffold must emit ai/team/composition.yml so the generated project
    round-trips and satisfies validate-repo's structural contract.
    """

    def test_writes_composition_yml(self, tmp_path: Path):
        import yaml

        output = tmp_path / "my-project"
        spec = _make_spec()
        result = scaffold_project(spec, output)

        composition = output / "ai" / "team" / "composition.yml"
        assert composition.is_file()
        assert "ai/team/composition.yml" in result.wrote

        data = yaml.safe_load(composition.read_text(encoding="utf-8"))
        assert data["project"]["slug"] == spec.project.slug
        assert data["project"]["name"] == spec.project.name
        assert "team" in data
        assert "expertise" in data

    def test_composition_roundtrip(self, tmp_path: Path):
        """The emitted composition.yml must be loadable via load_composition
        and produce an equivalent spec.
        """
        from foundry_app.io.composition_io import load_composition

        output = tmp_path / "my-project"
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        )
        scaffold_project(spec, output)

        reloaded = load_composition(output / "ai" / "team" / "composition.yml")
        assert reloaded.project.slug == spec.project.slug
        assert [p.id for p in reloaded.team.personas] == ["developer"]

    def test_idempotent_second_pass(self, tmp_path: Path):
        """Re-running scaffold with an unchanged spec must not list the
        composition snapshot as newly written."""
        output = tmp_path / "my-project"
        spec = _make_spec()
        scaffold_project(spec, output)
        result = scaffold_project(spec, output)
        assert "ai/team/composition.yml" not in result.wrote

    def test_reemits_when_spec_changes(self, tmp_path: Path):
        """If the spec changed between runs, the composition snapshot is
        rewritten and appears in the wrote list."""
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        new_spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
        )
        result = scaffold_project(new_spec, output)
        assert "ai/team/composition.yml" in result.wrote

    def test_composition_yml_has_orchestration_block(self, tmp_path: Path):
        """BEAN-269: composition.yml must carry the static orchestration
        policy block so cold-start agents and tooling can read the team
        model machine-readably."""
        import yaml

        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        composition = output / "ai" / "team" / "composition.yml"
        data = yaml.safe_load(composition.read_text(encoding="utf-8"))
        orch = data["orchestration"]
        assert orch["orchestrator_role"] == "team-lead"
        assert orch["team_model"] == "available-bench"
        required = orch["required_roles"]["software-development"]
        assert "developer" in required
        assert "tech-qa" in required
        optional = orch["optional_roles"]
        assert "architect" in optional
        assert "ba" in optional


class TestStarterReadme:
    """Scaffold must emit a starter README.md at the project root on first run,
    and preserve any README the user has customized on later runs.
    """

    def test_writes_readme_at_root(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec()
        result = scaffold_project(spec, output)

        readme = output / "README.md"
        assert readme.is_file()
        assert "README.md" in result.wrote
        content = readme.read_text(encoding="utf-8")
        assert spec.project.name in content
        assert "CLAUDE.md" in content
        assert "Foundry" in content

    def test_preserves_existing_readme(self, tmp_path: Path):
        output = tmp_path / "my-project"
        output.mkdir()
        (output / "README.md").write_text("# Customized\n", encoding="utf-8")

        result = scaffold_project(_make_spec(), output)

        assert "README.md" not in result.wrote
        assert (output / "README.md").read_text() == "# Customized\n"

    def test_readme_points_at_starter_stacks(self, tmp_path: Path):
        """BEAN-253: the generated README's Getting Started section must
        tell users to initialize the app with the stack-appropriate
        command and link to docs/starter-stacks.md in the Foundry repo
        (not inside the generated project — the cheat sheet lives with
        Foundry, not with the project)."""
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        content = (output / "README.md").read_text(encoding="utf-8")
        assert "docs/starter-stacks.md" in content
        assert "stack-appropriate command" in content


# ---------------------------------------------------------------------------
# Project charter (BEAN-252 / ADR-003)
# ---------------------------------------------------------------------------


class TestProjectCharter:
    """Scaffold must emit a starter ai/context/project-charter.md so generated
    projects have a discoverable, structured purpose document. Personas read
    this file first when opening the project. Overlay-safe: an existing
    charter is never clobbered.
    """

    _CHARTER_REL = "ai/context/project-charter.md"

    def test_writes_charter_at_ai_context(self, tmp_path: Path):
        output = tmp_path / "my-project"
        result = scaffold_project(_make_spec(), output)

        charter = output / self._CHARTER_REL
        assert charter.is_file()
        assert self._CHARTER_REL in result.wrote

    def test_charter_has_all_required_sections(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        content = (output / self._CHARTER_REL).read_text(encoding="utf-8")

        for heading in (
            "## Purpose",
            "## Audience",
            "## Success Criteria",
            "## Non-Goals",
            "## Constraints",
        ):
            assert heading in content, f"Charter missing section: {heading}"

    def test_charter_header_includes_project_name(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(
            project=ProjectIdentity(name="Acme Widgets", slug="acme-widgets"),
        )
        scaffold_project(spec, output)
        content = (output / self._CHARTER_REL).read_text(encoding="utf-8")

        assert content.startswith("# Project Charter — Acme Widgets")

    def test_charter_status_todo_admonition_present(self, tmp_path: Path):
        """The greppable 'Status: TODO' token signals an unfilled charter."""
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        content = (output / self._CHARTER_REL).read_text(encoding="utf-8")

        assert "Status:** TODO" in content

    def test_charter_echoes_description_when_present(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(
            project=ProjectIdentity(
                name="Acme",
                slug="acme",
                description="A widget pipeline for the operations team.",
            ),
        )
        scaffold_project(spec, output)
        content = (output / self._CHARTER_REL).read_text(encoding="utf-8")

        assert "*A widget pipeline for the operations team.*" in content

    def test_charter_shows_todo_when_description_absent(self, tmp_path: Path):
        output = tmp_path / "my-project"
        spec = _make_spec(
            project=ProjectIdentity(name="Acme", slug="acme"),
        )
        scaffold_project(spec, output)
        content = (output / self._CHARTER_REL).read_text(encoding="utf-8")

        assert "TODO: Add a one-line project description" in content

    def test_charter_footer_attribution(self, tmp_path: Path):
        output = tmp_path / "my-project"
        scaffold_project(_make_spec(), output)
        content = (output / self._CHARTER_REL).read_text(encoding="utf-8")

        assert "Generated by Foundry v" in content

    def test_preserves_existing_charter(self, tmp_path: Path):
        """Overlay safety: a user-edited charter must not be clobbered."""
        output = tmp_path / "my-project"
        (output / "ai" / "context").mkdir(parents=True)
        custom = "# My Charter\n\nFilled in by hand.\n"
        (output / self._CHARTER_REL).write_text(custom, encoding="utf-8")

        result = scaffold_project(_make_spec(), output)

        assert self._CHARTER_REL not in result.wrote
        assert (output / self._CHARTER_REL).read_text() == custom
