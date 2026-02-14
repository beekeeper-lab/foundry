"""Tests for foundry_app.services.agent_writer — agent file generation."""

from pathlib import Path

import pytest

from foundry_app.core.models import (
    CompositionSpec,
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    ProjectIdentity,
    StackInfo,
    StackSelection,
    TeamConfig,
)
from foundry_app.services.agent_writer import (
    _extract_key_rules,
    _extract_mission,
    _extract_role_description,
    _extract_stack_highlights,
    write_agents,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SAMPLE_PERSONA_MD = """\
# Persona: Developer

## Mission

Deliver clean, tested, incremental implementations that satisfy acceptance
criteria and conform to the project's architectural design. The Developer turns
designs into working code.

## Scope

**Does:**
- Implement features and fixes
- Write tests

**Does not:**
- Make architectural decisions

## Operating Principles

- **Read before you write.** Before implementing anything, read the full requirement.
- **Small, reviewable changes.** Every PR should be small enough to review in 15 minutes.
- **Tests are not optional.** Every behavior you add gets a test.
- **Follow the conventions.** The project has coding standards. Follow them.
- **Own your errors.** When a bug is found, fix it and add a regression test.
- **No magic.** Prefer explicit, readable code over clever abstractions.
"""

_SAMPLE_CONVENTIONS_MD = """\
# Python Stack Conventions

These conventions are non-negotiable defaults for Python projects.

---

## Defaults

| Concern | Default |
|---------|---------|
| Python version | 3.12+ |
| Package manager | uv |
| Formatter | ruff |
| Test framework | pytest |

## Project Structure

Standard layout with src/ directory.
"""


def _make_library(tmp_path: Path) -> tuple[Path, LibraryIndex]:
    """Create a minimal library with one persona and one stack."""
    lib_root = tmp_path / "library"
    persona_dir = lib_root / "personas" / "developer"
    persona_dir.mkdir(parents=True)
    (persona_dir / "persona.md").write_text(_SAMPLE_PERSONA_MD, encoding="utf-8")

    stack_dir = lib_root / "stacks" / "python"
    stack_dir.mkdir(parents=True)
    (stack_dir / "conventions.md").write_text(_SAMPLE_CONVENTIONS_MD, encoding="utf-8")

    index = LibraryIndex(
        library_root=str(lib_root),
        personas=[PersonaInfo(
            id="developer",
            name="Developer",
            path=str(persona_dir),
            templates=[],
        )],
        stacks=[StackInfo(
            id="python",
            name="Python",
            path=str(stack_dir),
        )],
    )
    return lib_root, index


def _make_spec(**overrides) -> CompositionSpec:
    """Create a minimal spec with one persona and one stack."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        stacks=[StackSelection(id="python")],
    )
    defaults.update(overrides)
    return CompositionSpec(**defaults)


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------


class TestExtractMission:

    def test_extracts_mission_section(self):
        result = _extract_mission(_SAMPLE_PERSONA_MD)
        assert "Deliver clean, tested" in result
        assert "working code" in result

    def test_empty_input(self):
        assert _extract_mission("") == ""

    def test_no_mission_section(self):
        text = "# Persona: Test\n\nSome text about the persona."
        result = _extract_mission(text)
        assert "Some text" in result


class TestExtractRoleDescription:

    def test_extracts_first_sentence(self):
        result = _extract_role_description(_SAMPLE_PERSONA_MD)
        assert "Deliver clean" in result
        # Should be one sentence
        assert result.endswith(".")

    def test_empty_input(self):
        assert _extract_role_description("") == ""


class TestExtractKeyRules:

    def test_extracts_rules(self):
        rules = _extract_key_rules(_SAMPLE_PERSONA_MD)
        assert len(rules) == 5  # max 5 rules
        assert any("Read before you write" in r for r in rules)
        assert any("Tests are not optional" in r for r in rules)

    def test_no_principles_section(self):
        rules = _extract_key_rules("# Persona\n\n## Mission\nDo stuff.")
        assert rules == []


class TestExtractStackHighlights:

    def test_extracts_defaults_table(self):
        highlights = _extract_stack_highlights(_SAMPLE_CONVENTIONS_MD)
        assert "Python version" in highlights
        assert "pytest" in highlights

    def test_empty_input(self):
        assert _extract_stack_highlights("") == ""


# ---------------------------------------------------------------------------
# write_agents — integration
# ---------------------------------------------------------------------------


class TestWriteAgents:

    def test_creates_agent_file(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        result = write_agents(spec, index, lib_root, output)

        agent_file = output / ".claude" / "agents" / "developer.md"
        assert agent_file.is_file()
        assert ".claude/agents/developer.md" in result.wrote

    def test_agent_file_has_role_name(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        assert "# Python Developer" in content

    def test_agent_file_has_mission(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        assert "Deliver clean" in content

    def test_agent_file_has_key_rules(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        assert "Read before you write" in content

    def test_agent_file_has_stack_context(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        assert "Python" in content
        assert "pytest" in content

    def test_agent_file_has_compiled_prompt_reference(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        assert "ai/generated/members/developer.md" in content

    def test_persona_not_found_warns(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec(team=TeamConfig(personas=[PersonaSelection(id="nonexistent")]))
        output = tmp_path / "output"
        output.mkdir()

        result = write_agents(spec, index, lib_root, output)

        assert len(result.wrote) == 0
        assert any("nonexistent" in w for w in result.warnings)

    def test_no_stacks(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec(stacks=[])
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        agent_file = output / ".claude" / "agents" / "developer.md"
        assert agent_file.is_file()
        content = agent_file.read_text()
        # Without stacks, role name should just be "Developer"
        assert "# Developer" in content

    def test_multiple_stacks(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)

        # Add a second stack
        react_dir = lib_root / "stacks" / "react"
        react_dir.mkdir(parents=True)
        (react_dir / "conventions.md").write_text(
            "# React Conventions\n\n## Defaults\n\n| Concern | Default |\n"
            "|---------|--------|\n| Framework | React 18 |\n",
            encoding="utf-8",
        )
        index.stacks.append(StackInfo(
            id="react",
            name="React",
            path=str(react_dir),
        ))

        spec = _make_spec(stacks=[StackSelection(id="python"), StackSelection(id="react")])
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        # Primary stack in role name
        assert "# Python Developer" in content
        # Both stacks in stack names
        assert "python, react" in content

    def test_no_warnings_for_valid_spec(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        result = write_agents(spec, index, lib_root, output)

        assert result.warnings == []


# ---------------------------------------------------------------------------
# Team agent verification — real library, multiple personas
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent
_LIBRARY_ROOT = _REPO_ROOT / "ai-team-library"
_EXAMPLE_YAML = _REPO_ROOT / "examples" / "small-python-team.yml"

_TEAM_TEST_AVAILABLE = _LIBRARY_ROOT.is_dir() and _EXAMPLE_YAML.is_file()


@pytest.mark.skipif(not _TEAM_TEST_AVAILABLE, reason="ai-team-library not present")
class TestTeamAgentVerification:
    """Verify agent files match the team composition using the real library."""

    @pytest.fixture()
    def team_output(self, tmp_path: Path):
        """Run write_agents with the real library for small-python-team personas."""
        from foundry_app.io.composition_io import load_composition
        from foundry_app.services.library_indexer import build_library_index

        spec = load_composition(_EXAMPLE_YAML)
        index = build_library_index(_LIBRARY_ROOT)
        output = tmp_path / "output"
        output.mkdir()

        result = write_agents(spec, index, _LIBRARY_ROOT, output)
        return output, result, spec

    def test_one_agent_file_per_persona(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        expected_ids = {p.id for p in spec.team.personas}
        actual_files = {f.stem for f in agents_dir.glob("*.md")}
        assert actual_files == expected_ids

    def test_agent_count_matches_persona_count(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        agent_files = list(agents_dir.glob("*.md"))
        assert len(agent_files) == len(spec.team.personas)

    def test_no_extra_agent_files(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        expected_ids = {p.id for p in spec.team.personas}
        actual_files = {f.stem for f in agents_dir.glob("*.md")}
        extra = actual_files - expected_ids
        assert not extra, f"Unexpected agent files: {extra}"

    def test_no_missing_agent_files(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        expected_ids = {p.id for p in spec.team.personas}
        actual_files = {f.stem for f in agents_dir.glob("*.md")}
        missing = expected_ids - actual_files
        assert not missing, f"Missing agent files for personas: {missing}"

    def test_each_agent_references_persona_name(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        for persona in spec.team.personas:
            agent_file = agents_dir / f"{persona.id}.md"
            content = agent_file.read_text(encoding="utf-8").lower()
            readable = persona.id.replace("-", " ")
            assert readable in content or persona.id in content, (
                f"Agent {agent_file.name} does not reference persona '{persona.id}'"
            )

    def test_all_agent_files_nonempty(self, team_output):
        output, _, _ = team_output
        agents_dir = output / ".claude" / "agents"
        for agent_file in agents_dir.glob("*.md"):
            assert agent_file.stat().st_size > 0, f"Agent file is empty: {agent_file.name}"

    def test_no_warnings_for_real_library(self, team_output):
        _, result, _ = team_output
        assert result.warnings == []
