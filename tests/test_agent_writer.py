"""Tests for foundry_app.services.agent_writer — agent file generation."""

from pathlib import Path

import pytest

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseInfo,
    ExpertiseSelection,
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    ProjectIdentity,
    TeamConfig,
)
from foundry_app.services.agent_writer import (
    _extract_expertise_highlights,
    _extract_key_rules,
    _extract_mission,
    _extract_role_description,
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
# Python Expertise Conventions

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
    """Create a minimal library with one persona and one expertise."""
    lib_root = tmp_path / "library"
    persona_dir = lib_root / "personas" / "developer"
    persona_dir.mkdir(parents=True)
    (persona_dir / "persona.md").write_text(_SAMPLE_PERSONA_MD, encoding="utf-8")

    expertise_dir = lib_root / "stacks" / "python"
    expertise_dir.mkdir(parents=True)
    (expertise_dir / "conventions.md").write_text(_SAMPLE_CONVENTIONS_MD, encoding="utf-8")

    index = LibraryIndex(
        library_root=str(lib_root),
        personas=[PersonaInfo(
            id="developer",
            name="Developer",
            path=str(persona_dir),
            templates=[],
        )],
        expertise=[ExpertiseInfo(
            id="python",
            name="Python",
            path=str(expertise_dir),
        )],
    )
    return lib_root, index


def _make_spec(**overrides) -> CompositionSpec:
    """Create a minimal spec with one persona and one expertise."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        expertise=[ExpertiseSelection(id="python")],
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


class TestExtractExpertiseHighlights:

    def test_extracts_defaults_table(self):
        highlights = _extract_expertise_highlights(_SAMPLE_CONVENTIONS_MD)
        assert "Python version" in highlights
        assert "pytest" in highlights

    def test_empty_input(self):
        assert _extract_expertise_highlights("") == ""


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

    def test_agent_file_has_expertise_context(self, tmp_path: Path):
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

    def test_no_expertise(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec(expertise=[])
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        agent_file = output / ".claude" / "agents" / "developer.md"
        assert agent_file.is_file()
        content = agent_file.read_text()
        # Without expertise, role name should just be "Developer"
        assert "# Developer" in content

    def test_multiple_expertise(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)

        # Add a second expertise
        react_dir = lib_root / "stacks" / "react"
        react_dir.mkdir(parents=True)
        (react_dir / "conventions.md").write_text(
            "# React Conventions\n\n## Defaults\n\n| Concern | Default |\n"
            "|---------|--------|\n| Framework | React 18 |\n",
            encoding="utf-8",
        )
        index.expertise.append(ExpertiseInfo(
            id="react",
            name="React",
            path=str(react_dir),
        ))

        spec = _make_spec(expertise=[
            ExpertiseSelection(id="python"), ExpertiseSelection(id="react"),
        ])
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        # Primary expertise in role name
        assert "# Python Developer" in content
        # Both expertise in expertise names
        assert "python, react" in content

    def test_no_warnings_for_valid_spec(self, tmp_path: Path):
        lib_root, index = _make_library(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        result = write_agents(spec, index, lib_root, output)

        assert result.warnings == []

    def test_missing_expertise_excluded_from_agent_header(self, tmp_path: Path):
        """When an expertise has no conventions.md, its ID must not appear
        in the agent header's ``**Expertise:** ...`` line. Regression guard
        for BEAN-261: the CLAUDE.md drop must propagate to agent files.
        """
        lib_root, index = _make_library(tmp_path)

        # Add a second expertise directory without conventions.md so it is
        # indexed (present on disk) but not emittable.
        clean_code_dir = lib_root / "stacks" / "clean-code"
        clean_code_dir.mkdir(parents=True)
        (clean_code_dir / "readme.md").write_text("not conventions", encoding="utf-8")
        index.expertise.append(ExpertiseInfo(
            id="clean-code",
            name="Clean Code",
            path=str(clean_code_dir),
        ))

        spec = _make_spec(expertise=[
            ExpertiseSelection(id="python"),
            ExpertiseSelection(id="clean-code"),
        ])
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        # Missing-source expertise must be absent from the header.
        assert "clean-code" not in content
        # Present expertise still renders, as does the role name.
        assert "**Expertise:** python" in content
        assert "# Python Developer" in content


class TestAgentPlaceholderRendering:
    """Persona source Jinja expressions must be resolved before they reach
    the rendered agent file. Regression guard for BEAN-243.
    """

    def _make_persona_with_placeholders(self, tmp_path: Path) -> tuple[Path, LibraryIndex]:
        lib_root = tmp_path / "library"
        persona_dir = lib_root / "personas" / "developer"
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text(
            "# Persona: Developer\n\n"
            "## Mission\n\n"
            "Ship clean code for **{{ project_name }}** at "
            "**{{ strictness }}** strictness using "
            "**{{ expertise | join(\", \") }}**.\n\n"
            "## Operating Principles\n\n"
            "- **Match project.** Follow {{ project_name }} conventions.\n",
            encoding="utf-8",
        )
        expertise_dir = lib_root / "stacks" / "python"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Python\n\n## Defaults\n\n- Use pytest for {{ project_name }}.\n",
            encoding="utf-8",
        )
        index = LibraryIndex(
            library_root=str(lib_root),
            personas=[PersonaInfo(
                id="developer",
                name="Developer",
                path=str(persona_dir),
                templates=[],
            )],
            expertise=[ExpertiseInfo(
                id="python",
                name="Python",
                path=str(expertise_dir),
            )],
        )
        return lib_root, index

    def test_no_unresolved_placeholders_in_output(self, tmp_path: Path):
        lib_root, index = self._make_persona_with_placeholders(tmp_path)
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        result = write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        assert "{{" not in content, f"Unresolved Jinja in output:\n{content}"
        assert "}}" not in content
        assert "Test Project" in content
        assert "standard" in content  # default strictness
        assert "python" in content
        # Placeholder-warning scan found nothing.
        assert not any("Unresolved" in w for w in result.warnings), (
            f"Unexpected warning: {result.warnings}"
        )

    def test_warning_emitted_for_unknown_placeholder(self, tmp_path: Path):
        """If a persona uses an unknown variable, the agent writer still
        writes the file but surfaces the leak via a warning."""
        lib_root = tmp_path / "library"
        persona_dir = lib_root / "personas" / "developer"
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text(
            "# Persona: Developer\n\n## Mission\n\nTarget: {{ unknown_var }}.\n",
            encoding="utf-8",
        )
        expertise_dir = lib_root / "stacks" / "python"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            "# Python\n\n## Defaults\n\n- ok\n",
            encoding="utf-8",
        )
        index = LibraryIndex(
            library_root=str(lib_root),
            personas=[PersonaInfo(
                id="developer",
                name="Developer",
                path=str(persona_dir),
                templates=[],
            )],
            expertise=[ExpertiseInfo(
                id="python",
                name="Python",
                path=str(expertise_dir),
            )],
        )
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        result = write_agents(spec, index, lib_root, output)

        assert any(
            "Unresolved placeholders" in w and "developer.md" in w and "unknown_var" in w
            for w in result.warnings
        ), f"Expected unresolved-placeholder warning; got: {result.warnings}"


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


# ---------------------------------------------------------------------------
# Balanced code fences — regression guard for BEAN-267
# ---------------------------------------------------------------------------


class TestExpertiseHighlightsFenceBalance:
    """Regression guard for BEAN-267: an expertise Defaults section that
    embeds a fenced code block must not leak an unbalanced ``` into the
    agent header when the soft line cap is hit mid-fence.
    """

    _JSONC_CONVENTIONS = """\
# TypeScript Conventions

## Defaults

- **Strict mode:** `"strict": true`. No exceptions.
- **Target:** ES2022.
- **Module system:** ESM.
- **Linting:** ESLint.
- **Formatting:** Prettier.
- **Type preference:** `type` over `interface`.
- **No `any`:** Use `unknown`.

### tsconfig Baseline

```jsonc
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

## Next Section

Other stuff.
"""

    def test_jsonc_fence_closes_when_cap_hits_mid_block(self):
        highlights = _extract_expertise_highlights(self._JSONC_CONVENTIONS)
        assert highlights.count("```") % 2 == 0, (
            f"Unbalanced fence in highlights:\n{highlights}"
        )
        # The closing fence must be emitted when the source's fence closes.
        assert highlights.rstrip().endswith("```"), (
            f"Highlights must end with a closing fence:\n{highlights}"
        )

    def test_malformed_unclosed_fence_is_dropped(self):
        """If the source itself never closes a fence, the opener (and the
        lines after it) are dropped so the output remains balanced."""
        malformed = (
            "# Conv\n\n## Defaults\n\n- first\n- second\n\n"
            "```jsonc\n" + "line\n" * 80
        )
        highlights = _extract_expertise_highlights(malformed)
        assert highlights.count("```") % 2 == 0, (
            f"Unbalanced fence from malformed source:\n{highlights}"
        )
        assert "```jsonc" not in highlights
        # Bullets before the dangling fence survive.
        assert "first" in highlights
        assert "second" in highlights


class TestGeneratedAgentFilesHaveBalancedFences:
    """End-to-end guard: every .claude/agents/<persona>.md written by
    write_agents must contain a balanced number of ``` fences, regardless of
    which expertise is included. Exercises the BEAN-267 scenario: a persona
    built against a jsonc-embedded expertise.
    """

    _JSONC_CONVENTIONS = TestExpertiseHighlightsFenceBalance._JSONC_CONVENTIONS

    def _make_library_with_jsonc(
        self, tmp_path: Path,
    ) -> tuple[Path, LibraryIndex]:
        lib_root = tmp_path / "library"
        persona_dir = lib_root / "personas" / "developer"
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text(_SAMPLE_PERSONA_MD, encoding="utf-8")

        expertise_dir = lib_root / "stacks" / "typescript"
        expertise_dir.mkdir(parents=True)
        (expertise_dir / "conventions.md").write_text(
            self._JSONC_CONVENTIONS, encoding="utf-8",
        )

        index = LibraryIndex(
            library_root=str(lib_root),
            personas=[PersonaInfo(
                id="developer",
                name="Developer",
                path=str(persona_dir),
                templates=[],
            )],
            expertise=[ExpertiseInfo(
                id="typescript",
                name="TypeScript",
                path=str(expertise_dir),
            )],
        )
        return lib_root, index

    def test_agent_file_has_balanced_code_fences(self, tmp_path: Path):
        lib_root, index = self._make_library_with_jsonc(tmp_path)
        spec = _make_spec(expertise=[ExpertiseSelection(id="typescript")])
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text(
            encoding="utf-8",
        )
        fence_count = content.count("```")
        assert fence_count % 2 == 0, (
            f"Unbalanced ``` fences ({fence_count}) in agent file:\n{content}"
        )


@pytest.mark.skipif(not _TEAM_TEST_AVAILABLE, reason="ai-team-library not present")
class TestRealLibraryAgentFencesBalanced:
    """Regression guard for BEAN-267 against the shipped library. Uses the
    full-stack-web example which includes typescript (jsonc block) + react +
    node across ~9 personas — the exact composition shape the external
    review reported as truncated.
    """

    def test_full_stack_web_agents_have_balanced_fences(self, tmp_path: Path):
        from foundry_app.io.composition_io import load_composition
        from foundry_app.services.library_indexer import build_library_index

        example = _REPO_ROOT / "examples" / "full-stack-web.yml"
        if not example.is_file():
            pytest.skip("full-stack-web.yml not present")

        spec = load_composition(example)
        index = build_library_index(_LIBRARY_ROOT)
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, _LIBRARY_ROOT, output)

        agents_dir = output / ".claude" / "agents"
        unbalanced: list[str] = []
        for agent_file in sorted(agents_dir.glob("*.md")):
            content = agent_file.read_text(encoding="utf-8")
            if content.count("```") % 2 != 0:
                unbalanced.append(agent_file.name)
        assert not unbalanced, (
            f"Agent files with unbalanced ``` fences: {unbalanced}"
        )
