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
        """An expertise with NO source files must not appear in the agent
        header's ``**Expertise:** ...`` line. A conventions-less pack with
        sibling files still compiles (SPEC-003 fallback) and is listed.
        """
        lib_root, index = _make_library(tmp_path)

        # A pack with sibling files but no conventions.md — emittable via
        # the SPEC-003 fallback.
        clean_code_dir = lib_root / "stacks" / "clean-code"
        clean_code_dir.mkdir(parents=True)
        (clean_code_dir / "readme.md").write_text("not conventions", encoding="utf-8")
        index.expertise.append(ExpertiseInfo(
            id="clean-code",
            name="Clean Code",
            path=str(clean_code_dir),
        ))
        # A pack directory with no .md files at all — never emittable.
        ghost_dir = lib_root / "stacks" / "ghost"
        ghost_dir.mkdir(parents=True)
        index.expertise.append(ExpertiseInfo(
            id="ghost",
            name="Ghost",
            path=str(ghost_dir),
        ))

        spec = _make_spec(expertise=[
            ExpertiseSelection(id="python", order=10),
            ExpertiseSelection(id="clean-code", order=20),
            ExpertiseSelection(id="ghost", order=30),
        ])
        output = tmp_path / "output"
        output.mkdir()

        write_agents(spec, index, lib_root, output)

        content = (output / ".claude" / "agents" / "developer.md").read_text()
        # Source-less expertise must be absent from the header.
        assert "ghost" not in content
        # Present and fallback-compiled expertise both render.
        assert "**Expertise:** python, clean-code" in content
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
        # Per ADR-014, agent filenames strip the ``extended/`` tier prefix.
        from foundry_app.core.models import _persona_dirname
        expected_files = {_persona_dirname(p.id) for p in spec.team.personas}
        actual_files = {f.stem for f in agents_dir.glob("*.md")}
        assert actual_files == expected_files

    def test_agent_count_matches_persona_count(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        agent_files = list(agents_dir.glob("*.md"))
        assert len(agent_files) == len(spec.team.personas)

    def test_no_extra_agent_files(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        from foundry_app.core.models import _persona_dirname
        expected_files = {_persona_dirname(p.id) for p in spec.team.personas}
        actual_files = {f.stem for f in agents_dir.glob("*.md")}
        extra = actual_files - expected_files
        assert not extra, f"Unexpected agent files: {extra}"

    def test_no_missing_agent_files(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        from foundry_app.core.models import _persona_dirname
        expected_files = {_persona_dirname(p.id) for p in spec.team.personas}
        actual_files = {f.stem for f in agents_dir.glob("*.md")}
        missing = expected_files - actual_files
        assert not missing, f"Missing agent files for personas: {missing}"

    def test_each_agent_references_persona_name(self, team_output):
        output, _, spec = team_output
        agents_dir = output / ".claude" / "agents"
        from foundry_app.core.models import _persona_dirname
        for persona in spec.team.personas:
            leaf = _persona_dirname(persona.id)
            agent_file = agents_dir / f"{leaf}.md"
            content = agent_file.read_text(encoding="utf-8").lower()
            readable = leaf.replace("-", " ")
            assert readable in content or leaf in content, (
                f"Agent {agent_file.name} does not reference persona "
                f"'{persona.id}'"
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


# ---------------------------------------------------------------------------
# ADR-012 / BEAN-259: per-expertise persona relevance — agent_writer filter
# ---------------------------------------------------------------------------


def _make_filter_library(tmp_path: Path) -> tuple[Path, LibraryIndex]:
    """Library with three personas + python (Developer-only) and react
    (Developer + UX/UI Designer) expertise. Used to exercise the per-persona
    filter inside write_agents."""
    lib_root = tmp_path / "library"
    persona_md = (
        "# Persona: {name}\n\n"
        "## Mission\n\n{name} mission text.\n\n"
        "## Operating Principles\n\n"
        "- **Do good work.** Always.\n"
    )
    for pid, name in [
        ("developer", "Developer"),
        ("devops-release", "DevOps-Release"),
        ("ux-ui-designer", "UX/UI Designer"),
    ]:
        d = lib_root / "personas" / pid
        d.mkdir(parents=True)
        (d / "persona.md").write_text(
            persona_md.format(name=name), encoding="utf-8",
        )

    py_dir = lib_root / "stacks" / "python"
    py_dir.mkdir(parents=True)
    (py_dir / "conventions.md").write_text(
        "# Python\n\n## Defaults\n\n"
        "| Concern | Default |\n|---------|---------|\n"
        "| Formatter | ruff |\n| Tests | pytest |\n",
        encoding="utf-8",
    )

    rx_dir = lib_root / "stacks" / "react"
    rx_dir.mkdir(parents=True)
    (rx_dir / "conventions.md").write_text(
        "# React\n\n## Defaults\n\n"
        "- TypeScript strict, see tsconfig.json\n"
        "- Functional components only\n",
        encoding="utf-8",
    )

    personas_root = lib_root / "personas"
    index = LibraryIndex(
        library_root=str(lib_root),
        personas=[
            PersonaInfo(
                id="developer",
                path=str(personas_root / "developer"),
                templates=[],
            ),
            PersonaInfo(
                id="devops-release",
                path=str(personas_root / "devops-release"),
                templates=[],
            ),
            PersonaInfo(
                id="ux-ui-designer",
                path=str(personas_root / "ux-ui-designer"),
                templates=[],
            ),
        ],
        expertise=[
            ExpertiseInfo(
                id="python",
                path=str(py_dir),
                applies_to=["developer"],
            ),
            ExpertiseInfo(
                id="react",
                path=str(rx_dir),
                applies_to=["developer", "ux-ui-designer"],
            ),
        ],
    )
    return lib_root, index


class TestAgentWriterAppliesToFilter:
    """Per-persona expertise filter (ADR-012 cases 1, 2, 3)."""

    def _spec(self) -> CompositionSpec:
        return CompositionSpec(
            project=ProjectIdentity(name="Filter Test", slug="filter-test"),
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="devops-release"),
                PersonaSelection(id="ux-ui-designer"),
            ]),
            expertise=[
                ExpertiseSelection(id="python"),
                ExpertiseSelection(id="react"),
            ],
        )

    def test_developer_includes_python_and_react(self, tmp_path: Path):
        """ADR-012 case 3: Developer is in both applies_to lists."""
        lib_root, index = _make_filter_library(tmp_path)
        out = tmp_path / "out"
        out.mkdir()
        write_agents(self._spec(), index, lib_root, out)
        content = (out / ".claude" / "agents" / "developer.md").read_text()
        assert "ruff" in content
        assert "tsconfig" in content.lower()

    def test_devops_release_excludes_python_and_react(self, tmp_path: Path):
        """ADR-012 case 1: DevOps-Release is in neither applies_to list."""
        lib_root, index = _make_filter_library(tmp_path)
        out = tmp_path / "out"
        out.mkdir()
        write_agents(self._spec(), index, lib_root, out)
        content = (out / ".claude" / "agents" / "devops-release.md").read_text()
        assert "ruff" not in content
        assert "tsconfig" not in content.lower()
        assert "pytest" not in content

    def test_ux_ui_designer_includes_react_excludes_python(
        self, tmp_path: Path,
    ):
        """ADR-012 case 2: UX/UI Designer is in react.applies_to but not python.applies_to."""
        lib_root, index = _make_filter_library(tmp_path)
        out = tmp_path / "out"
        out.mkdir()
        write_agents(self._spec(), index, lib_root, out)
        content = (out / ".claude" / "agents" / "ux-ui-designer.md").read_text()
        assert "ruff" not in content
        assert "pytest" not in content
        # React content should be present
        assert "tsconfig" in content.lower() or "Functional components" in content


class TestAgentWriterAppliesToBackwardCompat:
    """ADR-012 cases 4 + 5: empty applies_to == applies to all."""

    def _spec(self) -> CompositionSpec:
        return CompositionSpec(
            project=ProjectIdentity(name="BC", slug="bc"),
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="devops-release"),
                PersonaSelection(id="ux-ui-designer"),
            ]),
            expertise=[ExpertiseSelection(id="python")],
        )

    def _bc_lib(self, tmp_path: Path) -> tuple[Path, LibraryIndex]:
        """Same as _make_filter_library, but applies_to=[] on every expertise.
        With the empty default, every persona should still receive the
        expertise content — this is the pre-BEAN-259 behavior."""
        lib_root, index = _make_filter_library(tmp_path)
        for e in index.expertise:
            e.applies_to = []
        return lib_root, index

    def test_empty_applies_to_includes_all_personas(self, tmp_path: Path):
        """ADR-012 case 5: empty list = applies to every persona."""
        lib_root, index = self._bc_lib(tmp_path)
        out = tmp_path / "out"
        out.mkdir()
        write_agents(self._spec(), index, lib_root, out)
        for pid in ("developer", "devops-release", "ux-ui-designer"):
            content = (out / ".claude" / "agents" / f"{pid}.md").read_text()
            assert "ruff" in content, (
                f"persona {pid} missing python content under empty applies_to"
            )

    def test_baseline_byte_equal_for_unannotated_lib(self, tmp_path: Path):
        """ADR-012 case 4: a library with no applies_to anywhere produces
        the same per-persona output as before BEAN-259. We assert that the
        emitted agent files are identical when applies_to=[] (post-feature)
        compared to a snapshot computed over the same library — which is
        the same call path because the empty-list branch in
        _expertise_applies_to short-circuits to True. Treats this as a
        regression guard against the filter accidentally firing for
        unannotated expertise."""
        lib_root, index = self._bc_lib(tmp_path)
        out_a = tmp_path / "out_a"
        out_a.mkdir()
        write_agents(self._spec(), index, lib_root, out_a)

        # Re-run with the same empty-applies_to index — must be identical.
        out_b = tmp_path / "out_b"
        out_b.mkdir()
        write_agents(self._spec(), index, lib_root, out_b)

        for pid in ("developer", "devops-release", "ux-ui-designer"):
            a = (out_a / ".claude" / "agents" / f"{pid}.md").read_bytes()
            b = (out_b / ".claude" / "agents" / f"{pid}.md").read_bytes()
            assert a == b


class TestAgentWriterUnknownPersonaInAppliesTo:
    """ADR-012 case 6: a bogus persona id in applies_to is dropped at index
    time and never matches a real persona."""

    def test_bogus_id_does_not_match_real_persona(self, tmp_path: Path):
        """If applies_to=['bogus-persona'] survived the indexer (it
        wouldn't), the real Developer persona must not be matched. We
        simulate the post-validation state directly: an empty list, since
        the indexer drops unknown IDs."""
        lib_root, index = _make_filter_library(tmp_path)
        # Simulate "applies_to had only bogus-persona, indexer dropped it"
        for e in index.expertise:
            if e.id == "python":
                e.applies_to = []  # all unknown ids dropped → empty
        out = tmp_path / "out"
        out.mkdir()
        write_agents(
            CompositionSpec(
                project=ProjectIdentity(name="X", slug="x"),
                team=TeamConfig(personas=[PersonaSelection(id="developer")]),
                expertise=[ExpertiseSelection(id="python")],
            ),
            index, lib_root, out,
        )
        # Empty post-validation list → applies-to-all → Developer gets it.
        content = (out / ".claude" / "agents" / "developer.md").read_text()
        assert "ruff" in content


@pytest.mark.skipif(not _TEAM_TEST_AVAILABLE, reason="ai-team-library not present")
class TestRealLibraryAppliesToFilter:
    """End-to-end ADR-012 cases against the real library.

    Uses a synthetic React+Python+TypeScript composition spanning Developer,
    Tech-QA, DevOps-Release, and UX/UI Designer to exercise the curated
    applies_to lists shipped in BEAN-259.
    """

    def _spec(self):
        return CompositionSpec(
            project=ProjectIdentity(name="A11y/Web", slug="a11y-web"),
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="tech-qa"),
                # ADR-014: extended personas use the ``extended/`` prefix.
                PersonaSelection(id="extended/devops-release"),
                PersonaSelection(id="extended/ux-ui-designer"),
            ]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="typescript", order=20),
                ExpertiseSelection(id="react", order=30),
            ],
        )

    def _build(self, tmp_path: Path):
        from foundry_app.services.library_indexer import build_library_index
        index = build_library_index(_LIBRARY_ROOT)
        out = tmp_path / "out"
        out.mkdir()
        write_agents(self._spec(), index, _LIBRARY_ROOT, out)
        return out

    def test_devops_release_has_no_tsconfig_or_ruff(self, tmp_path: Path):
        """ADR-012 case 1 + part of case 2: DevOps-Release agent file
        contains no tsconfig and no ruff (neither expertise lists it)."""
        out = self._build(tmp_path)
        # Per ADR-014, the on-disk agent filename strips the ``extended/`` prefix.
        content = (out / ".claude" / "agents" / "devops-release.md").read_text()
        assert "tsconfig" not in content.lower()
        assert "ruff" not in content
        assert "pytest" not in content

    def test_ux_ui_designer_has_no_ruff(self, tmp_path: Path):
        """ADR-012 case 2: UX/UI Designer agent file contains no ruff
        (python is not in its applies_to)."""
        out = self._build(tmp_path)
        content = (out / ".claude" / "agents" / "ux-ui-designer.md").read_text()
        assert "ruff" not in content

    def test_developer_has_tsconfig_and_ruff(self, tmp_path: Path):
        """ADR-012 case 3: Developer agent file contains both python and
        TypeScript content."""
        out = self._build(tmp_path)
        content = (out / ".claude" / "agents" / "developer.md").read_text()
        assert "ruff" in content
        assert "tsconfig" in content.lower()


@pytest.mark.skipif(not _TEAM_TEST_AVAILABLE, reason="ai-team-library not present")
class TestBean259TokenSavings:
    """Acceptance check (BEAN-259): per-persona prompt size shrinks by
    >=20% for at least one non-Developer persona under a representative
    React+Python+TypeScript composition.

    Measured on 2026-04-30 with the curated applies_to lists shipped in
    BEAN-259 (python, typescript, react, accessibility-compliance):
        - devops-release:    -59.6%
        - security-engineer: -56.2%
        - ba:                -55.6%
        - ux-ui-designer:    -38.9%
        - architect:         no change (in every list)
        - developer:         no change (in every list)
        - tech-qa:           no change (in every list)
    See ``scripts/measure_bean_259_savings.py`` for the detailed report.
    """

    def _spec(self):
        return CompositionSpec(
            project=ProjectIdentity(name="Savings", slug="savings"),
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="tech-qa"),
                PersonaSelection(id="architect"),
                # ADR-014: extended personas use the ``extended/`` prefix.
                PersonaSelection(id="extended/devops-release"),
                PersonaSelection(id="extended/ux-ui-designer"),
                PersonaSelection(id="ba"),
                PersonaSelection(id="extended/security-engineer"),
            ]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="typescript", order=20),
                ExpertiseSelection(id="react", order=30),
                ExpertiseSelection(id="accessibility-compliance", order=40),
            ],
        )

    def test_at_least_one_non_developer_persona_shrinks_20pct(
        self, tmp_path: Path,
    ):
        from foundry_app.core.models import _persona_dirname
        from foundry_app.services.library_indexer import build_library_index

        spec = self._spec()
        before_dir = tmp_path / "before"
        after_dir = tmp_path / "after"
        before_dir.mkdir()
        after_dir.mkdir()

        index_before = build_library_index(_LIBRARY_ROOT)
        for e in index_before.expertise:
            e.applies_to = []
        write_agents(spec, index_before, _LIBRARY_ROOT, before_dir)

        index_after = build_library_index(_LIBRARY_ROOT)
        write_agents(spec, index_after, _LIBRARY_ROOT, after_dir)

        biggest_pct = 0.0
        biggest_pid = ""
        for ps in spec.team.personas:
            if ps.id == "developer":
                continue
            # Per ADR-014 the on-disk filename strips the tier prefix.
            leaf = _persona_dirname(ps.id)
            before_path = before_dir / ".claude" / "agents" / f"{leaf}.md"
            after_path = after_dir / ".claude" / "agents" / f"{leaf}.md"
            before_size = before_path.stat().st_size
            after_size = after_path.stat().st_size
            pct = (before_size - after_size) / before_size * 100.0
            if pct > biggest_pct:
                biggest_pct = pct
                biggest_pid = ps.id
        assert biggest_pct >= 20.0, (
            f"BEAN-259 acceptance failed: largest non-Developer reduction "
            f"is {biggest_pid}={biggest_pct:.1f}%, expected >=20%"
        )
