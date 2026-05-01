"""Tests for foundry_app.services.compiler — CLAUDE.md compilation from library."""

import json
import re
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseInfo,
    ExpertiseSelection,
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    ProjectIdentity,
    Strictness,
    TeamConfig,
)
from foundry_app.services.compiler import (
    _build_context,
    _build_persona_context,
    _build_persona_name_map,
    _canonicalize_persona_header,
    _display_name_from_id,
    _expertise_applies_to,
    _filter_collaboration_table,
    _filter_defer_references,
    _filter_persona_references,
    _persona_display_name,
    _resolve_persona_name,
    _substitute,
    compile_project,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a CompositionSpec with sensible defaults."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        expertise=[ExpertiseSelection(id="python", order=10)],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


def _make_library(tmp_path: Path, personas=None, expertise=None) -> tuple[LibraryIndex, Path]:
    """Create a minimal library on disk and return (index, library_root).

    Args:
        tmp_path: pytest tmp_path fixture.
        personas: dict mapping persona_id -> dict of files.
            e.g. {"developer": {"persona.md": "# Dev", "outputs.md": "# Out"}}
        expertise: dict mapping expertise_id -> dict of files.
            e.g. {"python": {"conventions.md": "# Python Conventions"}}

    Returns:
        Tuple of (LibraryIndex, library_root_path).
    """
    lib_root = tmp_path / "library"
    personas = personas or {}
    expertise = expertise or {}

    persona_infos: list[PersonaInfo] = []
    for pid, files in personas.items():
        persona_dir = lib_root / "personas" / pid
        persona_dir.mkdir(parents=True, exist_ok=True)
        for fname, content in files.items():
            (persona_dir / fname).write_text(content, encoding="utf-8")
        persona_infos.append(PersonaInfo(
            id=pid,
            path=str(persona_dir),
            has_persona_md="persona.md" in files,
            has_outputs_md="outputs.md" in files,
            has_prompts_md="prompts.md" in files,
            templates=[],
        ))

    expertise_infos: list[ExpertiseInfo] = []
    for sid, files in expertise.items():
        expertise_dir = lib_root / "stacks" / sid
        expertise_dir.mkdir(parents=True, exist_ok=True)
        for fname, content in files.items():
            (expertise_dir / fname).write_text(content, encoding="utf-8")
        expertise_infos.append(ExpertiseInfo(
            id=sid,
            path=str(expertise_dir),
            files=list(files.keys()),
        ))

    index = LibraryIndex(
        library_root=str(lib_root),
        personas=persona_infos,
        expertise=expertise_infos,
    )
    return index, lib_root


# ---------------------------------------------------------------------------
# Template variable substitution
# ---------------------------------------------------------------------------


class TestSubstitute:

    def test_replaces_project_name(self):
        result = _substitute("Project: {{ project_name }}", {"project_name": "Acme"})
        assert result == "Project: Acme"

    def test_replaces_multiple_occurrences(self):
        result = _substitute(
            "{{ project_name }} is {{ project_name }}",
            {"project_name": "Acme"},
        )
        assert result == "Acme is Acme"

    def test_leaves_unknown_placeholders(self):
        result = _substitute("{{ unknown_var }}", {"project_name": "Acme"})
        assert result == "{{ unknown_var }}"

    def test_handles_join_filter(self):
        result = _substitute(
            '{{ expertise | join(", ") }}',
            {"expertise": "python,typescript"},
        )
        assert result == "python, typescript"

    def test_join_single_item(self):
        result = _substitute(
            '{{ expertise | join(", ") }}',
            {"expertise": "python"},
        )
        assert result == "python"

    def test_no_placeholders(self):
        text = "No variables here."
        result = _substitute(text, {"project_name": "Acme"})
        assert result == text

    def test_empty_string(self):
        result = _substitute("", {"project_name": "Acme"})
        assert result == ""

    def test_placeholder_with_extra_spaces(self):
        result = _substitute("{{  project_name  }}", {"project_name": "Acme"})
        assert result == "Acme"

    def test_join_filter_unknown_var(self):
        result = _substitute('{{ unknown | join(", ") }}', {})
        assert result == '{{ unknown | join(", ") }}'


# ---------------------------------------------------------------------------
# Build context
# ---------------------------------------------------------------------------


class TestBuildContext:

    def test_includes_project_name(self):
        spec = _make_spec()
        ctx = _build_context(spec)
        assert ctx["project_name"] == "Test Project"

    def test_includes_expertise_comma_separated(self):
        spec = _make_spec(expertise=[
            ExpertiseSelection(id="python", order=10),
            ExpertiseSelection(id="typescript", order=20),
        ])
        ctx = _build_context(spec)
        assert "python" in ctx["expertise"]
        assert "typescript" in ctx["expertise"]

    def test_expertise_sorted_by_order(self):
        spec = _make_spec(expertise=[
            ExpertiseSelection(id="typescript", order=20),
            ExpertiseSelection(id="python", order=10),
        ])
        ctx = _build_context(spec)
        parts = ctx["expertise"].split(",")
        assert parts[0] == "python"
        assert parts[1] == "typescript"

    def test_empty_expertise(self):
        spec = _make_spec(expertise=[])
        ctx = _build_context(spec)
        assert ctx["expertise"] == ""

    def test_single_expertise(self):
        spec = _make_spec(expertise=[ExpertiseSelection(id="python", order=10)])
        ctx = _build_context(spec)
        assert ctx["expertise"] == "python"


class TestBuildPersonaContext:
    """Per-persona context must carry the persona's strictness into substitution."""

    def test_includes_strictness_default(self):
        spec = _make_spec()
        persona_sel = spec.team.personas[0]
        ctx = _build_persona_context(spec, persona_sel)
        assert ctx["strictness"] == Strictness.STANDARD.value

    def test_strictness_per_persona(self):
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer", strictness=Strictness.STRICT),
            ]),
        )
        ctx = _build_persona_context(spec, spec.team.personas[0])
        assert ctx["strictness"] == "strict"

    def test_includes_shared_keys(self):
        spec = _make_spec()
        ctx = _build_persona_context(spec, spec.team.personas[0])
        assert ctx["project_name"] == "Test Project"
        assert "python" in ctx["expertise"]


class TestCompilePersonaRendering:
    """Persona source files must be fully rendered — no unresolved placeholders
    in the compiled ai/generated/members/<persona>.md output.
    """

    def test_strictness_resolves_in_member_file(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": (
                    "# Developer\n\n"
                    "Reviews for **{{ project_name }}** are calibrated at "
                    "**{{ strictness }}** strictness."
                ),
            },
        })
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer", strictness=Strictness.STRICT),
            ]),
        )
        result = compile_project(spec, index, lib_root, output)
        assert not any("Unresolved" in w for w in result.warnings), (
            f"Unexpected unresolved-placeholder warning: {result.warnings}"
        )

        member = (output / "ai" / "generated" / "members" / "developer.md").read_text()
        assert "{{" not in member and "}}" not in member
        assert "strict" in member
        assert "Test Project" in member

    def test_strictness_varies_per_persona(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "Level=[{{ strictness }}]"},
            "tech-qa": {"persona.md": "Level=[{{ strictness }}]"},
        })
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer", strictness=Strictness.STANDARD),
                PersonaSelection(id="tech-qa", strictness=Strictness.STRICT),
            ]),
        )
        compile_project(spec, index, lib_root, output)

        dev = (output / "ai" / "generated" / "members" / "developer.md").read_text()
        qa = (output / "ai" / "generated" / "members" / "tech-qa.md").read_text()
        assert "Level=[standard]" in dev
        assert "Level=[strict]" in qa


# ---------------------------------------------------------------------------
# compile_project — basic operation
# ---------------------------------------------------------------------------


class TestCompileProjectBasic:

    def test_creates_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        assert (output / "CLAUDE.md").exists()

    def test_returns_stage_result(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert isinstance(result, type(result))
        assert "CLAUDE.md" in result.wrote

    def test_wrote_contains_claude_md_and_generated_files(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert "CLAUDE.md" in result.wrote
        assert "ai/generated/members/developer.md" in result.wrote

    def test_creates_output_dir_if_missing(self, tmp_path: Path):
        output = tmp_path / "deep" / "nested" / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        assert output.is_dir()
        assert (output / "CLAUDE.md").exists()

    def test_accepts_string_paths(self, tmp_path: Path):
        output = str(tmp_path / "project")
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, str(lib_root), output)
        assert "CLAUDE.md" in result.wrote


# ---------------------------------------------------------------------------
# compile_project — content structure
# ---------------------------------------------------------------------------


class TestCompileProjectContent:

    def test_starts_with_project_header(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert content.startswith("# Test Project")

    def test_contains_team_heading(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Team" in content

    def test_persona_content_in_generated_file(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer\n\nBuild great code."},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        # Full content should be in generated file, not CLAUDE.md
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "Build great code." in gen
        # CLAUDE.md should have pointer to the file
        content = (output / "CLAUDE.md").read_text()
        assert "ai/generated/members/developer.md" in content

    def test_contains_tech_stack_heading(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={"python": {"conventions.md": "# Python Conventions"}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Tech Stack" in content

    def test_expertise_content_in_generated_file(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={"python": {"conventions.md": "Use type hints everywhere."}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        # Expertise content should be in generated file, not CLAUDE.md
        gen_content = (output / "ai/generated/expertise/python.md").read_text()
        assert "Use type hints everywhere." in gen_content
        # CLAUDE.md should have a pointer to the expertise file
        claude_content = (output / "CLAUDE.md").read_text()
        assert "ai/generated/expertise/python.md" in claude_content

    def test_ends_with_newline(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert content.endswith("\n")


# ---------------------------------------------------------------------------
# compile_project — persona file assembly
# ---------------------------------------------------------------------------


class TestPersonaFileAssembly:

    def test_includes_persona_md_in_generated(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "PERSONA_CONTENT"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "PERSONA_CONTENT" in gen

    def test_includes_outputs_md_in_generated(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "PERSONA",
                "outputs.md": "OUTPUTS_CONTENT",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "OUTPUTS_CONTENT" in gen

    def test_includes_prompts_md_in_generated(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "PERSONA",
                "prompts.md": "PROMPTS_CONTENT",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "PROMPTS_CONTENT" in gen

    def test_persona_files_in_order_in_generated(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "AAA_PERSONA",
                "outputs.md": "BBB_OUTPUTS",
                "prompts.md": "CCC_PROMPTS",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert gen.index("AAA_PERSONA") < gen.index("BBB_OUTPUTS")
        assert gen.index("BBB_OUTPUTS") < gen.index("CCC_PROMPTS")

    def test_missing_outputs_md_still_compiles(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert "CLAUDE.md" in result.wrote

    def test_missing_prompts_md_still_compiles(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "# Developer",
                "outputs.md": "# Outputs",
            },
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert "CLAUDE.md" in result.wrote


# ---------------------------------------------------------------------------
# compile_project — multiple personas
# ---------------------------------------------------------------------------


class TestMultiplePersonas:

    def test_all_personas_in_generated_files(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "DEV_CONTENT"},
            "architect": {"persona.md": "ARCH_CONTENT"},
        })
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(id="architect"),
        ]))
        compile_project(spec, index, lib_root, output)
        dev = (output / "ai/generated/members/developer.md").read_text()
        arch = (output / "ai/generated/members/architect.md").read_text()
        assert "DEV_CONTENT" in dev
        assert "ARCH_CONTENT" in arch

    def test_persona_order_matches_spec_in_wrote(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "DEV_FIRST"},
            "architect": {"persona.md": "ARCH_SECOND"},
        })
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(id="architect"),
        ]))
        result = compile_project(spec, index, lib_root, output)
        member_files = [w for w in result.wrote if "members" in w]
        assert member_files.index("ai/generated/members/developer.md") < \
            member_files.index("ai/generated/members/architect.md")

    def test_reversed_persona_order_in_wrote(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "DEV_SECOND"},
            "architect": {"persona.md": "ARCH_FIRST"},
        })
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="architect"),
            PersonaSelection(id="developer"),
        ]))
        result = compile_project(spec, index, lib_root, output)
        member_files = [w for w in result.wrote if "members" in w]
        assert member_files.index("ai/generated/members/architect.md") < \
            member_files.index("ai/generated/members/developer.md")

    def test_three_personas_all_generated(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "AAA"},
            "architect": {"persona.md": "BBB"},
            "tech-qa": {"persona.md": "CCC"},
        })
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(id="architect"),
            PersonaSelection(id="tech-qa"),
        ]))
        compile_project(spec, index, lib_root, output)
        assert "AAA" in (output / "ai/generated/members/developer.md").read_text()
        assert "BBB" in (output / "ai/generated/members/architect.md").read_text()
        assert "CCC" in (output / "ai/generated/members/tech-qa.md").read_text()


# ---------------------------------------------------------------------------
# compile_project — multiple expertise
# ---------------------------------------------------------------------------


class TestMultipleExpertise:

    def test_all_expertise_in_generated_files(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={
                "python": {"conventions.md": "PYTHON_CONV"},
                "typescript": {"conventions.md": "TS_CONV"},
            },
        )
        spec = _make_spec(expertise=[
            ExpertiseSelection(id="python", order=10),
            ExpertiseSelection(id="typescript", order=20),
        ])
        compile_project(spec, index, lib_root, output)
        py = (output / "ai/generated/expertise/python.md").read_text()
        ts = (output / "ai/generated/expertise/typescript.md").read_text()
        assert "PYTHON_CONV" in py
        assert "TS_CONV" in ts

    def test_expertise_sorted_by_order_in_wrote(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={
                "python": {"conventions.md": "PYTHON_FIRST"},
                "typescript": {"conventions.md": "TS_SECOND"},
            },
        )
        spec = _make_spec(expertise=[
            ExpertiseSelection(id="typescript", order=20),
            ExpertiseSelection(id="python", order=10),
        ])
        result = compile_project(spec, index, lib_root, output)
        # python should be written before typescript (sorted by order)
        exp_files = [w for w in result.wrote if "expertise" in w]
        assert exp_files.index("ai/generated/expertise/python.md") < \
            exp_files.index("ai/generated/expertise/typescript.md")

    def test_expertise_same_order_sorted_alphabetically_in_wrote(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={
                "typescript": {"conventions.md": "TS_CONTENT"},
                "python": {"conventions.md": "PY_CONTENT"},
            },
        )
        spec = _make_spec(expertise=[
            ExpertiseSelection(id="typescript", order=0),
            ExpertiseSelection(id="python", order=0),
        ])
        result = compile_project(spec, index, lib_root, output)
        exp_files = [w for w in result.wrote if "expertise" in w]
        # python comes before typescript alphabetically
        assert exp_files.index("ai/generated/expertise/python.md") < \
            exp_files.index("ai/generated/expertise/typescript.md")

    def test_team_before_tech_stack_in_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "PERSONA_SECTION"}},
            expertise={"python": {"conventions.md": "STACK_SECTION"}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        # In lean CLAUDE.md, Tech Stack comes before Team
        assert "## Tech Stack" in content
        assert "## Team" in content


# ---------------------------------------------------------------------------
# compile_project — template substitution in content
# ---------------------------------------------------------------------------


class TestTemplateSubstitutionInContent:

    def test_project_name_substituted_in_generated_persona(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "Working on {{ project_name }}"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "Working on Test Project" in gen
        assert "{{ project_name }}" not in gen

    def test_expertise_join_substituted_in_generated_persona(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={
                "developer": {
                    "persona.md": 'Stack: {{ expertise | join(", ") }}',
                },
            },
            expertise={
                "python": {"conventions.md": "# Python"},
                "typescript": {"conventions.md": "# TS"},
            },
        )
        spec = _make_spec(expertise=[
            ExpertiseSelection(id="python", order=10),
            ExpertiseSelection(id="typescript", order=20),
        ])
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "Stack: python, typescript" in gen

    def test_substitution_in_generated_outputs_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "# Dev",
                "outputs.md": "Deliver for {{ project_name }}",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "Deliver for Test Project" in gen

    def test_substitution_in_generated_prompts_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "# Dev",
                "prompts.md": "Context for {{ project_name }}",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "Context for Test Project" in gen

    def test_substitution_in_expertise_conventions(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={"python": {"conventions.md": "For {{ project_name }}"}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/expertise/python.md").read_text()
        assert "For Test Project" in gen


# ---------------------------------------------------------------------------
# compile_project — warnings
# ---------------------------------------------------------------------------


class TestCompileWarnings:

    def test_warns_on_missing_persona_in_index(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path)  # no personas in library
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="nonexistent"),
        ]))
        result = compile_project(spec, index, lib_root, output)
        # ADR-014: unknown persona ids surface as
        # "Unknown persona '<id>' in composition.yml. Core personas (...)..."
        assert any(
            "nonexistent" in w and "Unknown persona" in w
            for w in result.warnings
        )

    def test_warns_on_missing_persona_md(self, tmp_path: Path):
        output = tmp_path / "project"
        # Persona dir exists but has no persona.md
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"outputs.md": "# Outputs only"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert any("missing persona.md" in w for w in result.warnings)

    def test_warns_on_missing_expertise_in_index(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })  # no expertise in library
        spec = _make_spec(expertise=[ExpertiseSelection(id="nonexistent")])
        result = compile_project(spec, index, lib_root, output)
        assert any("nonexistent" in w and "not found" in w for w in result.warnings)

    def test_warns_on_missing_conventions_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={"python": {"readme.md": "Not conventions"}},
        )
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert any("missing conventions.md" in w for w in result.warnings)

    def test_missing_expertise_excluded_from_claude_md(self, tmp_path: Path):
        """When an expertise has no conventions.md, CLAUDE.md must not
        reference the expertise's ai/generated/expertise/<id>.md path
        (the file is never written). The warning is still emitted.
        """
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={
                "python": {"conventions.md": "# Python"},
                "clean-code": {"readme.md": "Not conventions"},
            },
        )
        spec = _make_spec(
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="clean-code", order=20),
            ],
        )
        result = compile_project(spec, index, lib_root, output)

        # Warning is still surfaced.
        assert any("clean-code" in w and "missing" in w for w in result.warnings)

        # Missing-source file must not exist on disk.
        assert not (output / "ai/generated/expertise/clean-code.md").exists()

        # Generated CLAUDE.md must not reference the missing file.
        claude_md = (output / "CLAUDE.md").read_text(encoding="utf-8")
        assert "ai/generated/expertise/clean-code.md" not in claude_md

        # The present expertise is still referenced.
        assert "ai/generated/expertise/python.md" in claude_md

    def test_all_expertise_references_in_claude_md_exist_on_disk(
        self, tmp_path: Path,
    ):
        """Every `ai/generated/expertise/<id>.md` reference in the generated
        CLAUDE.md must correspond to a file that was actually written.
        """
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={
                "python": {"conventions.md": "# Python"},
                "clean-code": {"readme.md": "Not conventions"},
                "rust": {"conventions.md": "# Rust"},
            },
        )
        spec = _make_spec(
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="clean-code", order=20),
                ExpertiseSelection(id="rust", order=30),
            ],
        )
        compile_project(spec, index, lib_root, output)

        claude_md = (output / "CLAUDE.md").read_text(encoding="utf-8")
        import re as _re
        referenced = _re.findall(
            r"ai/generated/expertise/([A-Za-z0-9_-]+)\.md",
            claude_md,
        )
        assert referenced, "expected at least one expertise reference in CLAUDE.md"
        for eid in referenced:
            assert (output / "ai/generated/expertise" / f"{eid}.md").is_file(), (
                f"CLAUDE.md references ai/generated/expertise/{eid}.md but "
                f"the file was not written"
            )

    def test_missing_expertise_excluded_from_member_file(self, tmp_path: Path):
        """When an expertise has no conventions.md, the generated member
        file's ``{{ expertise | join(", ") }}`` substitution must not list
        the missing-source expertise ID.
        """
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={
                "developer": {
                    "persona.md": (
                        "# Dev\n\nStack: **{{ expertise | join(\", \") }}**"
                    ),
                },
            },
            expertise={
                "python": {"conventions.md": "# Python"},
                "clean-code": {"readme.md": "Not conventions"},
            },
        )
        spec = _make_spec(
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="clean-code", order=20),
            ],
        )
        compile_project(spec, index, lib_root, output)

        member = (output / "ai/generated/members/developer.md").read_text(
            encoding="utf-8",
        )
        # Missing-source expertise must not appear in the substituted list.
        assert "clean-code" not in member
        # Present expertise is still rendered.
        assert "Stack: **python**" in member

    def test_warns_on_unresolved_placeholders(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "Use {{ custom_var }} here"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert any("Unresolved" in w for w in result.warnings)

    def test_no_warnings_for_clean_compilation(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {
                "persona.md": "# Dev for {{ project_name }}",
                "outputs.md": "# Outputs",
                "prompts.md": "# Prompts",
            }},
            expertise={"python": {"conventions.md": "# Python"}},
        )
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert result.warnings == []

    def test_warns_on_persona_with_no_files(self, tmp_path: Path):
        output = tmp_path / "project"
        # Create persona in index but with no files on disk
        lib_root = tmp_path / "library"
        persona_dir = lib_root / "personas" / "developer"
        persona_dir.mkdir(parents=True)
        index = LibraryIndex(
            library_root=str(lib_root),
            personas=[PersonaInfo(
                id="developer",
                path=str(persona_dir),
                has_persona_md=False,
                has_outputs_md=False,
                has_prompts_md=False,
            )],
        )
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert any("no source files" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# compile_project — no personas / no expertise
# ---------------------------------------------------------------------------


class TestEmptySelections:

    def test_no_personas_still_creates_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            expertise={"python": {"conventions.md": "# Python"}},
        )
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = compile_project(spec, index, lib_root, output)
        assert (output / "CLAUDE.md").exists()
        assert "CLAUDE.md" in result.wrote

    def test_no_personas_no_team_heading(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            expertise={"python": {"conventions.md": "# Python"}},
        )
        spec = _make_spec(team=TeamConfig(personas=[]))
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        # The Team roster section is suppressed when no personas are
        # selected. The Team Orchestration Model section (BEAN-269) is
        # policy and always emitted, so match the roster heading
        # specifically.
        assert "## Team\n" not in content

    def test_no_expertise_still_creates_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec(expertise=[])
        result = compile_project(spec, index, lib_root, output)
        assert (output / "CLAUDE.md").exists()
        assert "CLAUDE.md" in result.wrote

    def test_no_expertise_no_tech_stack_heading(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec(expertise=[])
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Tech Stack" not in content

    def test_no_personas_no_expertise(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path)
        spec = _make_spec(team=TeamConfig(personas=[]), expertise=[])
        result = compile_project(spec, index, lib_root, output)
        assert (output / "CLAUDE.md").exists()
        content = (output / "CLAUDE.md").read_text()
        assert content.startswith("# Test Project")


# ---------------------------------------------------------------------------
# compile_project — overlay mode
# ---------------------------------------------------------------------------


class TestOverlayMode:

    def test_overwrites_existing_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        output.mkdir()
        (output / "CLAUDE.md").write_text("OLD CONTENT")
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "NEW CONTENT"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "NEW CONTENT" in content
        assert "OLD CONTENT" not in content

    def test_does_not_destroy_other_files(self, tmp_path: Path):
        output = tmp_path / "project"
        output.mkdir()
        other_file = output / "README.md"
        other_file.write_text("keep me")
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        assert other_file.read_text() == "keep me"

    def test_overlay_returns_claude_md_in_wrote(self, tmp_path: Path):
        output = tmp_path / "project"
        output.mkdir()
        (output / "CLAUDE.md").write_text("OLD")
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert "CLAUDE.md" in result.wrote


# ---------------------------------------------------------------------------
# compile_project — determinism
# ---------------------------------------------------------------------------


class TestDeterminism:

    def test_same_input_same_output(self, tmp_path: Path):
        index, lib_root = _make_library(
            tmp_path,
            personas={
                "developer": {"persona.md": "# Dev", "outputs.md": "# Out"},
                "architect": {"persona.md": "# Arch"},
            },
            expertise={
                "python": {"conventions.md": "# Python"},
                "typescript": {"conventions.md": "# TS"},
            },
        )
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="typescript", order=20),
            ],
        )
        output1 = tmp_path / "run1"
        output2 = tmp_path / "run2"
        compile_project(spec, index, lib_root, output1)
        compile_project(spec, index, lib_root, output2)
        content1 = (output1 / "CLAUDE.md").read_text()
        content2 = (output2 / "CLAUDE.md").read_text()
        assert content1 == content2

    def test_deterministic_across_three_runs(self, tmp_path: Path):
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={"python": {"conventions.md": "# Python"}},
        )
        spec = _make_spec()
        outputs = []
        for i in range(3):
            out = tmp_path / f"run{i}"
            compile_project(spec, index, lib_root, out)
            outputs.append((out / "CLAUDE.md").read_text())
        assert outputs[0] == outputs[1] == outputs[2]


# ---------------------------------------------------------------------------
# compile_project — edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_persona_with_only_outputs_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"outputs.md": "OUTPUTS_ONLY"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "OUTPUTS_ONLY" in gen
        assert any("missing persona.md" in w for w in result.warnings)

    def test_persona_with_only_prompts_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"prompts.md": "PROMPTS_ONLY"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "PROMPTS_ONLY" in gen

    def test_whitespace_stripping(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "\n\n  # Dev  \n\n"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        # Should not have leading/trailing whitespace in persona section
        assert "\n\n\n\n" not in content

    def test_special_characters_in_project_name(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "For {{ project_name }}"},
        })
        spec = _make_spec(
            project=ProjectIdentity(name="Acme & Sons (v2.0)", slug="acme-sons"),
        )
        compile_project(spec, index, lib_root, output)
        # Check CLAUDE.md header
        content = (output / "CLAUDE.md").read_text()
        assert "Acme & Sons (v2.0)" in content
        # Check substitution in generated file
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "Acme & Sons (v2.0)" in gen

    def test_unicode_in_generated_content(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer \u2014 Build \u2728"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "\u2014" in gen
        assert "\u2728" in gen

    def test_large_number_of_personas_in_generated(self, tmp_path: Path):
        output = tmp_path / "project"
        personas = {f"persona-{i}": {"persona.md": f"CONTENT_{i}"} for i in range(10)}
        index, lib_root = _make_library(tmp_path, personas=personas)
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id=f"persona-{i}") for i in range(10)
        ]))
        result = compile_project(spec, index, lib_root, output)
        for i in range(10):
            gen = (output / f"ai/generated/members/persona-{i}.md").read_text()
            assert f"CONTENT_{i}" in gen
        assert "CLAUDE.md" in result.wrote

    def test_large_number_of_expertise_in_generated(self, tmp_path: Path):
        output = tmp_path / "project"
        expertise_items = {f"stack-{i}": {"conventions.md": f"STACK_{i}"} for i in range(10)}
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise=expertise_items,
        )
        spec = _make_spec(expertise=[
            ExpertiseSelection(id=f"stack-{i}", order=i) for i in range(10)
        ])
        result = compile_project(spec, index, lib_root, output)
        for i in range(10):
            gen = (output / f"ai/generated/expertise/stack-{i}.md").read_text()
            assert f"STACK_{i}" in gen
        assert f"ai/generated/expertise/stack-0.md" in result.wrote

    def test_empty_persona_md_file(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": ""},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert (output / "CLAUDE.md").exists()

    def test_empty_conventions_md_file(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={"python": {"conventions.md": ""}},
        )
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert (output / "CLAUDE.md").exists()


# ---------------------------------------------------------------------------
# compile_project — project header
# ---------------------------------------------------------------------------


class TestProjectHeader:

    def test_header_uses_project_name(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec(
            project=ProjectIdentity(name="My Cool Project", slug="cool"),
        )
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "# My Cool Project" in content

    def test_header_is_first_line(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        first_line = content.split("\n")[0]
        assert first_line == "# Test Project"

    def test_header_includes_description_when_set(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec(
            project=ProjectIdentity(
                name="My Project",
                slug="my-project",
                description="A modern web framework for building APIs.",
            ),
        )
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "A modern web framework for building APIs." in content

    def test_header_omits_description_when_none(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()  # default has no description
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        lines = content.splitlines()
        # Second line should be empty (no description), then next section
        assert lines[0] == "# Test Project"
        assert lines[1] == ""


# ---------------------------------------------------------------------------
# compile_project — lean CLAUDE.md structure
# ---------------------------------------------------------------------------


class TestLeanClaudeMd:

    def test_claude_md_under_100_lines(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={
                "team-lead": {"persona.md": "# TL\n\nLead the team."},
                "developer": {"persona.md": "# Dev\n\nBuild stuff."},
                "architect": {"persona.md": "# Arch\n\nDesign systems."},
                "tech-qa": {"persona.md": "# QA\n\nTest everything."},
            },
            expertise={
                "python": {"conventions.md": "# Python\n\nUse type hints."},
                "typescript": {"conventions.md": "# TS\n\nUse strict mode."},
                "clean-code": {"conventions.md": "# CC\n\nSmall functions."},
            },
        )
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="team-lead"),
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
                PersonaSelection(id="tech-qa"),
            ]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="typescript", order=20),
                ExpertiseSelection(id="clean-code", order=30),
            ],
        )
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        line_count = len(content.splitlines())
        assert line_count <= 100, f"CLAUDE.md has {line_count} lines, expected <= 100"

    def test_claude_md_has_directory_structure(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Directory Structure" in content
        assert ".claude/" in content
        assert "ai/" in content

    def test_claude_md_has_documentation_pointers(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            expertise={"python": {"conventions.md": "# Python"}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Documentation" in content
        assert "ai/generated/members/" in content
        assert "ai/generated/expertise/" in content

    def test_persona_content_not_in_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        long_content = "# Developer\n\n" + "\n".join(
            f"Rule {i}: Do something important." for i in range(50)
        )
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": long_content},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        # The detailed persona rules should NOT be in CLAUDE.md
        assert "Rule 10: Do something important." not in content
        # But should be in the generated file
        gen = (output / "ai/generated/members/developer.md").read_text()
        assert "Rule 10: Do something important." in gen

    def test_claude_md_has_team_orchestration_model(self, tmp_path: Path):
        """BEAN-269: generated CLAUDE.md must state the four-bullet
        orchestration policy explicitly so cold-start agents can read
        the team model without external context.
        """
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "team-lead": {"persona.md": "# TL"},
            "developer": {"persona.md": "# Dev"},
            "tech-qa": {"persona.md": "# QA"},
            "architect": {"persona.md": "# Arch"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Team Orchestration Model" in content
        assert "Team Lead is the orchestrator" in content
        assert "available bench of specialists" in content
        # Mandatory roles for software development
        assert "**Developer**" in content
        assert "**Tech-QA**" in content
        # At least one opt-in specialist named
        assert "**Architect**" in content

    def test_claude_md_orchestration_model_emitted_without_personas(
        self, tmp_path: Path,
    ):
        """The orchestration model is policy, not roster — it is emitted
        even when no personas are selected."""
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path, expertise={"python": {"conventions.md": "# Py"}},
        )
        spec = _make_spec(team=TeamConfig(personas=[]))
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Team Orchestration Model" in content

    def test_claude_md_no_contradicting_phrases(self, tmp_path: Path):
        """BEAN-269 acceptance: the generated CLAUDE.md must not contain
        wording that contradicts the available-bench model."""
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
            "tech-qa": {"persona.md": "# QA"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text().lower()
        for phrase in ("all members", "entire team", "full team wave"):
            assert phrase not in content, (
                f"CLAUDE.md contains contradicting phrase {phrase!r}"
            )

    def test_team_lead_library_source_has_orchestration_rules(self):
        """BEAN-269: the team-lead library persona source must state the
        orchestration rules operationally. Downstream regenerations
        propagate this to .claude/agents/team-lead.md."""
        import foundry_app
        repo_root = Path(foundry_app.__file__).resolve().parent.parent
        # Per ADR-014, core personas live under personas/core/<id>.
        persona = (
            repo_root / "ai-team-library"
            / "personas" / "core" / "team-lead" / "persona.md"
        )
        text = persona.read_text(encoding="utf-8")
        assert "## Orchestration Rules" in text
        assert "bench of specialists" in text
        assert "Always assign Developer and Tech-QA" in text

    def test_claude_md_has_scope_section(self, tmp_path: Path):
        """BEAN-251 + BEAN-253: the generated CLAUDE.md must state the
        planning-only scope — agents work under ai/, humans own the
        application code. The section must name ai/ explicitly and
        point users at docs/starter-stacks.md for initialization."""
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Scope" in content
        assert "ai/" in content
        assert "Edit(ai/**)" in content
        assert "docs/starter-stacks.md" in content

    def test_claude_md_scope_precedes_orchestration(self, tmp_path: Path):
        """The Scope section answers 'what does this framework produce?'
        and must appear before 'how do the agents coordinate?' — i.e.
        before the Team Orchestration Model heading."""
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        scope_idx = content.index("## Scope")
        orch_idx = content.index("## Team Orchestration Model")
        assert scope_idx < orch_idx

    def test_claude_md_scope_emitted_without_personas(
        self, tmp_path: Path,
    ):
        """The Scope section is policy, not roster — it is emitted even
        when no personas are selected."""
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path, expertise={"python": {"conventions.md": "# Py"}},
        )
        spec = _make_spec(team=TeamConfig(personas=[]))
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Scope" in content
        assert "docs/starter-stacks.md" in content

    def test_claude_md_scope_matches_settings_edit_permissions(
        self, tmp_path: Path,
    ):
        # Drift guard: every directory root the library's
        # settings.local.json grants Edit access to must be named in the
        # generated CLAUDE.md Scope section. If someone widens the Edit
        # allow list (e.g. adds Edit(src/**)) without updating the Scope
        # text, this test fails — preventing the policy/permission
        # mismatch BEAN-251 was created to resolve.
        repo_root = Path(__file__).resolve().parent.parent
        settings_path = (
            repo_root
            / "ai-team-library"
            / "claude"
            / "settings"
            / "settings.local.json"
        )
        settings = json.loads(settings_path.read_text())
        edit_pattern = re.compile(r"^Edit\(([^/)]+)/")
        edit_roots = {
            m.group(1)
            for entry in settings["permissions"]["allow"]
            if (m := edit_pattern.match(entry))
        }
        assert edit_roots, (
            f"Expected at least one Edit(<dir>/**) in {settings_path}; "
            "test cannot meaningfully assert consistency without one."
        )

        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()

        scope_start = content.index("## Scope")
        next_heading = content.find("\n## ", scope_start + 1)
        scope_text = content[scope_start:next_heading]

        for root in edit_roots:
            assert f"{root}/" in scope_text, (
                f"Scope section omits Edit-permitted root '{root}/'. "
                f"{settings_path.name} grants Edit({root}/**) but the "
                "Scope section does not name it. Update the Scope text "
                "in compiler._build_lean_claude_md or the Edit allow "
                "list to keep them in sync."
            )

    def test_claude_md_workflow_section_present(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()

        assert "## Workflow" in content
        assert "ai/beans/_index.md" in content
        assert "/long-run" in content
        assert "/show-backlog" in content
        assert "/pick-bean" in content
        assert "/new-bean" in content
        assert "/spawn-task" in content
        assert "/review-beans" in content

    def test_claude_md_workflow_after_orchestration_before_docs(
        self, tmp_path: Path,
    ):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()

        orch_idx = content.index("## Team Orchestration Model")
        workflow_idx = content.index("## Workflow")
        docs_idx = content.index("## Documentation")
        assert orch_idx < workflow_idx < docs_idx

    def test_claude_md_workflow_section_under_25_lines(
        self, tmp_path: Path,
    ):
        # BEAN-268: signposts are cheap, full docs are expensive — the
        # Workflow section must stay a pointer, not re-expand into a
        # detailed walkthrough.
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()

        workflow_start = content.index("## Workflow")
        next_heading = content.find("\n## ", workflow_start + 1)
        section = content[workflow_start:next_heading]
        line_count = section.count("\n") + 1
        assert line_count <= 25, (
            f"Workflow section is {line_count} lines (limit: 25). "
            "Trim it; signposts only."
        )


# ---------------------------------------------------------------------------
# compile_project — full integration
# ---------------------------------------------------------------------------


class TestFullIntegration:

    def test_full_compilation_structure(self, tmp_path: Path):
        """Verify the full structure: lean CLAUDE.md + generated files."""
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={
                "team-lead": {
                    "persona.md": "# Team Lead for {{ project_name }}",
                    "outputs.md": "# Team Lead Outputs",
                    "prompts.md": "# Team Lead Prompts",
                },
                "developer": {
                    "persona.md": '# Developer using {{ expertise | join(", ") }}',
                    "outputs.md": "# Developer Outputs",
                    "prompts.md": "# Developer Prompts",
                },
            },
            expertise={
                "python": {"conventions.md": "# Python Conventions"},
                "clean-code": {"conventions.md": "# Clean Code"},
            },
        )
        spec = _make_spec(
            project=ProjectIdentity(name="Full Test", slug="full-test"),
            team=TeamConfig(personas=[
                PersonaSelection(id="team-lead"),
                PersonaSelection(id="developer"),
            ]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="clean-code", order=20),
            ],
        )
        result = compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()

        # Lean CLAUDE.md structure checks
        assert content.startswith("# Full Test")
        assert "## Team" in content
        assert "## Tech Stack" in content
        assert "## Directory Structure" in content
        assert "## Documentation" in content

        # CLAUDE.md should have pointers, not full content
        assert "ai/generated/members/team-lead.md" in content
        assert "ai/generated/members/developer.md" in content
        assert "ai/generated/expertise/python.md" in content

        # Full persona content in generated files
        tl = (output / "ai/generated/members/team-lead.md").read_text()
        assert "# Team Lead for Full Test" in tl
        assert "# Team Lead Outputs" in tl
        assert "# Team Lead Prompts" in tl
        dev = (output / "ai/generated/members/developer.md").read_text()
        assert "# Developer using python, clean-code" in dev

        # Full expertise content in generated files
        py = (output / "ai/generated/expertise/python.md").read_text()
        assert "# Python Conventions" in py
        cc = (output / "ai/generated/expertise/clean-code.md").read_text()
        assert "# Clean Code" in cc

        # CLAUDE.md should be lean (under 100 lines)
        assert len(content.splitlines()) <= 100

        # No warnings
        assert result.warnings == []
        assert "CLAUDE.md" in result.wrote

    def test_compilation_with_mixed_missing_files(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={
                "developer": {
                    "persona.md": "# Dev",
                    "outputs.md": "# Out",
                    # no prompts.md
                },
                "architect": {
                    "persona.md": "# Arch",
                    # no outputs.md, no prompts.md
                },
            },
            expertise={
                "python": {"conventions.md": "# Python"},
                # missing-stack not in library
            },
        )
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="missing-stack", order=20),
            ],
        )
        result = compile_project(spec, index, lib_root, output)

        # Both personas in generated files
        dev = (output / "ai/generated/members/developer.md").read_text()
        assert "# Dev" in dev
        arch = (output / "ai/generated/members/architect.md").read_text()
        assert "# Arch" in arch

        # Python expertise in generated file
        py = (output / "ai/generated/expertise/python.md").read_text()
        assert "# Python" in py

        # Warning for missing stack
        assert any("missing-stack" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Persona name map
# ---------------------------------------------------------------------------


class TestBuildPersonaNameMap:

    def test_extracts_name_from_header(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Persona: Developer\n\nContent"},
        })
        name_map = _build_persona_name_map(index)
        assert name_map == {"Developer": "developer"}

    def test_handles_multiple_personas(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Persona: Developer"},
            "architect": {"persona.md": "# Persona: Architect"},
        })
        name_map = _build_persona_name_map(index)
        assert name_map["Developer"] == "developer"
        assert name_map["Architect"] == "architect"

    def test_handles_slash_in_name(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "tech-qa": {"persona.md": "# Persona: Tech-QA / Test Engineer"},
        })
        name_map = _build_persona_name_map(index)
        assert name_map["Tech-QA / Test Engineer"] == "tech-qa"

    def test_handles_alternative_name(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "technical-writer": {
                "persona.md": "# Persona: Technical Writer / Doc Owner",
            },
        })
        name_map = _build_persona_name_map(index)
        assert name_map["Technical Writer / Doc Owner"] == "technical-writer"

    def test_skips_persona_without_persona_md(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "developer": {"outputs.md": "# Outputs only"},
        })
        name_map = _build_persona_name_map(index)
        assert name_map == {}

    def test_skips_persona_without_header(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "developer": {"persona.md": "No header here"},
        })
        name_map = _build_persona_name_map(index)
        assert name_map == {}


# ---------------------------------------------------------------------------
# Resolve persona name
# ---------------------------------------------------------------------------


class TestResolvePersonaName:

    def test_exact_match(self):
        name_to_id = {"Developer": "developer", "Architect": "architect"}
        assert _resolve_persona_name("Developer", name_to_id) == "developer"

    def test_short_form_match(self):
        name_to_id = {"Technical Writer / Doc Owner": "technical-writer"}
        assert _resolve_persona_name("Technical Writer", name_to_id) == "technical-writer"

    def test_no_match_returns_none(self):
        name_to_id = {"Developer": "developer"}
        assert _resolve_persona_name("Stakeholders", name_to_id) is None

    def test_strips_whitespace(self):
        name_to_id = {"Developer": "developer"}
        assert _resolve_persona_name("  Developer  ", name_to_id) == "developer"

    def test_slash_in_name_exact_match(self):
        name_to_id = {"Compliance / Risk Analyst": "compliance-risk"}
        assert _resolve_persona_name("Compliance / Risk Analyst", name_to_id) == "compliance-risk"


# ---------------------------------------------------------------------------
# Filter collaboration table
# ---------------------------------------------------------------------------


class TestFilterCollaborationTable:

    def test_removes_non_selected_personas(self):
        text = (
            "## Collaboration & Handoffs\n"
            "\n"
            "| Collaborator | Pattern |\n"
            "|---|---|\n"
            "| Developer | Code stuff |\n"
            "| Architect | Design stuff |\n"
        )
        name_to_id = {"Developer": "developer", "Architect": "architect"}
        result = _filter_collaboration_table(text, {"developer"}, name_to_id)
        assert "Developer" in result
        assert "Architect" not in result

    def test_keeps_unknown_entities(self):
        text = (
            "## Collaboration & Handoffs\n"
            "\n"
            "| Collaborator | Pattern |\n"
            "|---|---|\n"
            "| Stakeholders | Business decisions |\n"
            "| Developer | Code stuff |\n"
        )
        name_to_id = {"Developer": "developer"}
        result = _filter_collaboration_table(text, set(), name_to_id)
        assert "Stakeholders" in result
        assert "Developer" not in result

    def test_drops_entire_section_when_empty(self):
        text = (
            "## Collaboration & Handoffs\n"
            "\n"
            "| Collaborator | Pattern |\n"
            "|---|---|\n"
            "| Developer | Code stuff |\n"
            "| Architect | Design stuff |\n"
            "\n"
            "## Next Section"
        )
        name_to_id = {"Developer": "developer", "Architect": "architect"}
        result = _filter_collaboration_table(text, set(), name_to_id)
        assert "Collaboration" not in result
        assert "## Next Section" in result

    def test_preserves_text_before_and_after_table(self):
        text = (
            "Some text before.\n"
            "\n"
            "## Collaboration & Handoffs\n"
            "\n"
            "| Collaborator | Pattern |\n"
            "|---|---|\n"
            "| Developer | Code stuff |\n"
            "\n"
            "Some text after."
        )
        name_to_id = {"Developer": "developer"}
        result = _filter_collaboration_table(text, {"developer"}, name_to_id)
        assert "Some text before." in result
        assert "Some text after." in result
        assert "Developer" in result

    def test_handles_short_form_names(self):
        text = (
            "## Collaboration & Handoffs\n"
            "\n"
            "| Collaborator | Pattern |\n"
            "|---|---|\n"
            "| Technical Writer | Doc stuff |\n"
            "| Developer | Code stuff |\n"
        )
        name_to_id = {
            "Technical Writer / Doc Owner": "technical-writer",
            "Developer": "developer",
        }
        result = _filter_collaboration_table(
            text, {"technical-writer"}, name_to_id,
        )
        assert "Technical Writer" in result
        assert "Developer" not in result

    def test_no_collaboration_section(self):
        text = "# Persona: Developer\n\nJust content, no collab table."
        result = _filter_collaboration_table(text, set(), {})
        assert result == text

    def test_all_personas_selected(self):
        text = (
            "## Collaboration & Handoffs\n"
            "\n"
            "| Collaborator | Pattern |\n"
            "|---|---|\n"
            "| Developer | Code stuff |\n"
            "| Architect | Design stuff |\n"
        )
        name_to_id = {"Developer": "developer", "Architect": "architect"}
        result = _filter_collaboration_table(
            text, {"developer", "architect"}, name_to_id,
        )
        assert "Developer" in result
        assert "Architect" in result


# ---------------------------------------------------------------------------
# Filter defer references
# ---------------------------------------------------------------------------


class TestFilterDeferReferences:

    def test_removes_defer_for_non_selected(self):
        text = "- Write code (defer to Developer)"
        name_to_id = {"Developer": "developer"}
        result = _filter_defer_references(text, set(), name_to_id)
        assert result == "- Write code"

    def test_keeps_defer_for_selected(self):
        text = "- Write docs (defer to Technical Writer)"
        name_to_id = {"Technical Writer / Doc Owner": "technical-writer"}
        result = _filter_defer_references(
            text, {"technical-writer"}, name_to_id,
        )
        assert "(defer to Technical Writer)" in result

    def test_removes_defer_with_extra_text(self):
        text = "- Make decisions (defer to Architect; break ties only when needed)"
        name_to_id = {"Architect": "architect"}
        result = _filter_defer_references(text, set(), name_to_id)
        assert result == "- Make decisions"

    def test_keeps_unknown_entities(self):
        text = "- Report to stakeholders (defer to Stakeholders)"
        result = _filter_defer_references(text, set(), {})
        assert "(defer to Stakeholders)" in result

    def test_multiple_defer_references(self):
        text = (
            "- Write code (defer to Developer)\n"
            "- Write docs (defer to Technical Writer)\n"
            "- Design UI (defer to UX Designer)"
        )
        name_to_id = {
            "Developer": "developer",
            "Technical Writer / Doc Owner": "technical-writer",
            "UX Designer": "ux-designer",
        }
        result = _filter_defer_references(
            text, {"technical-writer"}, name_to_id,
        )
        assert "- Write code\n" in result
        assert "(defer to Technical Writer)" in result
        assert "- Design UI" in result
        assert "(defer to UX Designer)" not in result


# ---------------------------------------------------------------------------
# Filter persona references (combined)
# ---------------------------------------------------------------------------


class TestFilterPersonaReferences:

    def test_filters_both_table_and_defer(self):
        text = (
            "**Does not:**\n"
            "- Write code (defer to Developer)\n"
            "- Write docs (defer to Technical Writer)\n"
            "\n"
            "## Collaboration & Handoffs\n"
            "\n"
            "| Collaborator | Pattern |\n"
            "|---|---|\n"
            "| Developer | Code stuff |\n"
            "| Technical Writer | Doc stuff |\n"
        )
        name_to_id = {
            "Developer": "developer",
            "Technical Writer / Doc Owner": "technical-writer",
        }
        result = _filter_persona_references(
            text, {"technical-writer"}, name_to_id,
        )
        # Defer: Developer removed, Technical Writer kept
        assert "- Write code\n" in result
        assert "(defer to Technical Writer)" in result
        # Table: Developer removed, Technical Writer kept
        assert "| Technical Writer" in result
        lines = result.split("\n")
        assert not any("| Developer" in line for line in lines)


# ---------------------------------------------------------------------------
# compile_project — persona reference filtering (integration)
# ---------------------------------------------------------------------------


class TestCompilePersonaFiltering:

    def _persona_with_collab(self, name: str, collabs: list[str]) -> str:
        """Build a persona.md with a Collaboration & Handoffs table."""
        rows = "\n".join(
            f"| {c} | Works with {c} |" for c in collabs
        )
        return (
            f"# Persona: {name}\n\n"
            f"Content for {name}.\n\n"
            f"## Collaboration & Handoffs\n\n"
            f"| Collaborator | Pattern |\n"
            f"|---|---|\n"
            f"{rows}\n"
        )

    def test_filters_non_selected_from_collab_table(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "team-lead": {
                "persona.md": self._persona_with_collab(
                    "Team Lead", ["Developer", "Architect", "Tech-QA"],
                ),
            },
            "developer": {"persona.md": "# Persona: Developer\n\nDev content."},
            "architect": {"persona.md": "# Persona: Architect\n\nArch content."},
            "tech-qa": {"persona.md": "# Persona: Tech-QA\n\nQA content."},
        })
        # Only select team-lead and developer — architect and tech-qa not selected
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="team-lead"),
            PersonaSelection(id="developer"),
        ]))
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/team-lead.md").read_text()

        # Developer should be in the collab table
        assert "| Developer" in gen
        # Architect and Tech-QA should NOT be in the collab table
        assert "| Architect" not in gen
        assert "| Tech-QA" not in gen

    def test_filters_defer_references_in_generated_output(self, tmp_path: Path):
        output = tmp_path / "project"
        persona_md = (
            "# Persona: Team Lead\n\n"
            "**Does not:**\n"
            "- Write code (defer to Developer)\n"
            "- Write docs (defer to Technical Writer)\n"
        )
        index, lib_root = _make_library(tmp_path, personas={
            "team-lead": {"persona.md": persona_md},
            "developer": {"persona.md": "# Persona: Developer"},
            "technical-writer": {
                "persona.md": "# Persona: Technical Writer / Doc Owner",
            },
        })
        # Only select team-lead and developer
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="team-lead"),
            PersonaSelection(id="developer"),
        ]))
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/team-lead.md").read_text()

        # "(defer to Developer)" should remain
        assert "(defer to Developer)" in gen
        # "(defer to Technical Writer)" should be removed
        assert "(defer to Technical Writer)" not in gen
        # But the constraint itself should remain
        assert "- Write docs" in gen

    def test_all_selected_nothing_filtered(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "team-lead": {
                "persona.md": self._persona_with_collab(
                    "Team Lead", ["Developer", "Architect"],
                ),
            },
            "developer": {"persona.md": "# Persona: Developer"},
            "architect": {"persona.md": "# Persona: Architect"},
        })
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="team-lead"),
            PersonaSelection(id="developer"),
            PersonaSelection(id="architect"),
        ]))
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/team-lead.md").read_text()

        assert "| Developer" in gen
        assert "| Architect" in gen

    def test_empty_collab_table_section_removed(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "team-lead": {
                "persona.md": self._persona_with_collab(
                    "Team Lead", ["Developer", "Architect"],
                ),
            },
            "developer": {"persona.md": "# Persona: Developer"},
            "architect": {"persona.md": "# Persona: Architect"},
        })
        # Only team-lead selected — both collaborators are non-selected
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="team-lead"),
        ]))
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/team-lead.md").read_text()

        assert "## Collaboration" not in gen

    def test_unknown_entities_preserved_in_generated_collab_table(self, tmp_path: Path):
        output = tmp_path / "project"
        persona_md = (
            "# Persona: Team Lead\n\n"
            "## Collaboration & Handoffs\n\n"
            "| Collaborator | Pattern |\n"
            "|---|---|\n"
            "| Developer | Code stuff |\n"
            "| Stakeholders | Business decisions |\n"
        )
        index, lib_root = _make_library(tmp_path, personas={
            "team-lead": {"persona.md": persona_md},
            "developer": {"persona.md": "# Persona: Developer"},
        })
        # Only team-lead selected — Developer not selected but Stakeholders unknown
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="team-lead"),
        ]))
        compile_project(spec, index, lib_root, output)
        gen = (output / "ai/generated/members/team-lead.md").read_text()

        # Stakeholders should remain (unknown entity)
        assert "Stakeholders" in gen
        # Developer should be removed (known, not selected)
        assert "| Developer" not in gen


# ---------------------------------------------------------------------------
# Display-name casing (BEAN-266)
# ---------------------------------------------------------------------------


class TestDisplayNameFromId:

    def test_tech_qa_uppercases_qa(self):
        assert _display_name_from_id("tech-qa") == "Tech QA"

    def test_ux_ui_designer_collapses_adjacent_acronyms_with_slash(self):
        assert _display_name_from_id("ux-ui-designer") == "UX/UI Designer"

    def test_sql_dba_two_acronyms(self):
        assert _display_name_from_id("sql-dba") == "SQL/DBA"

    def test_team_lead_non_acronyms(self):
        assert _display_name_from_id("team-lead") == "Team Lead"

    def test_single_acronym_id(self):
        assert _display_name_from_id("ba") == "BA"

    def test_no_hyphens(self):
        assert _display_name_from_id("developer") == "Developer"

    def test_technical_writer_title_cases(self):
        assert _display_name_from_id("technical-writer") == "Technical Writer"

    def test_api_design_acronym_then_word(self):
        assert _display_name_from_id("api-design") == "API Design"

    def test_empty_string(self):
        assert _display_name_from_id("") == ""


class TestCanonicalizePersonaHeader:

    def test_takes_first_segment_for_role_tail(self):
        assert (
            _canonicalize_persona_header("Tech-QA / Test Engineer") == "Tech-QA"
        )

    def test_merges_short_acronyms_around_slash(self):
        assert (
            _canonicalize_persona_header("UX / UI Designer") == "UX/UI Designer"
        )

    def test_strips_parenthetical_annotation(self):
        assert (
            _canonicalize_persona_header("Business Analyst (BA)")
            == "Business Analyst"
        )

    def test_single_segment_passes_through(self):
        assert _canonicalize_persona_header("Team Lead") == "Team Lead"

    def test_title_case_slash_non_acronym_tail_trimmed(self):
        assert (
            _canonicalize_persona_header("Integrator / Merge Captain")
            == "Integrator"
        )

    def test_mixed_case_tail_trimmed(self):
        assert (
            _canonicalize_persona_header("DevOps / Release Engineer")
            == "DevOps"
        )


class TestPersonaDisplayName:

    def test_reads_from_persona_header(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "tech-qa": {"persona.md": "# Persona: Tech-QA / Test Engineer\n"},
        })
        assert _persona_display_name("tech-qa", index) == "Tech-QA"

    def test_reads_ux_ui_header(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "ux-ui-designer": {"persona.md": "# Persona: UX / UI Designer\n"},
        })
        assert (
            _persona_display_name("ux-ui-designer", index) == "UX/UI Designer"
        )

    def test_falls_back_to_id_when_header_missing(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={
            "tech-qa": {"persona.md": "# Tech QA notes (no Persona header)\n"},
        })
        assert _persona_display_name("tech-qa", index) == "Tech QA"

    def test_falls_back_to_id_when_persona_missing(self, tmp_path: Path):
        index, _ = _make_library(tmp_path, personas={})
        assert _persona_display_name("ux-ui-designer", index) == "UX/UI Designer"


class TestClaudeMdTableCasing:

    def test_team_and_tech_stack_tables_use_correct_casing(
        self, tmp_path: Path,
    ):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={
                "tech-qa": {
                    "persona.md": "# Persona: Tech-QA / Test Engineer\n\nTest things.",
                },
                "ux-ui-designer": {
                    "persona.md": "# Persona: UX / UI Designer\n\nDesign screens.",
                },
                "ba": {
                    "persona.md": "# Persona: Business Analyst (BA)\n\nGather requirements.",
                },
            },
            expertise={
                "sql-dba": {"conventions.md": "# SQL DBA conventions"},
                "api-design": {"conventions.md": "# API design conventions"},
            },
        )
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="tech-qa"),
                PersonaSelection(id="ux-ui-designer"),
                PersonaSelection(id="ba"),
            ]),
            expertise=[
                ExpertiseSelection(id="sql-dba", order=10),
                ExpertiseSelection(id="api-design", order=20),
            ],
        )
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()

        # Team table — no lower-case acronym artefacts
        assert "Tech Qa" not in content
        assert "Ux Ui" not in content
        assert "| Tech-QA |" in content
        assert "| UX/UI Designer |" in content
        assert "| Business Analyst |" in content

        # Tech Stack table — acronyms uppercased
        assert "Sql Dba" not in content
        assert "Api Design" not in content
        assert "| SQL/DBA |" in content
        assert "| API Design |" in content


# ---------------------------------------------------------------------------
# ADR-012 / BEAN-259: per-expertise persona relevance
# ---------------------------------------------------------------------------


class TestExpertiseAppliesToHelper:
    """Pure unit tests for the ``_expertise_applies_to`` predicate."""

    def test_empty_applies_to_matches_every_persona(self):
        info = ExpertiseInfo(id="x", path="/tmp/x", applies_to=[])
        assert _expertise_applies_to("developer", info) is True
        assert _expertise_applies_to("ux-ui-designer", info) is True
        assert _expertise_applies_to("anything", info) is True

    def test_listed_persona_matches(self):
        info = ExpertiseInfo(id="x", path="/tmp/x", applies_to=["developer", "tech-qa"])
        assert _expertise_applies_to("developer", info) is True
        assert _expertise_applies_to("tech-qa", info) is True

    def test_unlisted_persona_does_not_match(self):
        info = ExpertiseInfo(id="x", path="/tmp/x", applies_to=["developer"])
        assert _expertise_applies_to("ux-ui-designer", info) is False
        assert _expertise_applies_to("devops-release", info) is False


class TestCompilerExpertiseFilterIntegration:
    """End-to-end checks that the per-persona filter does not leak into
    standalone expertise files or the lean CLAUDE.md (Tech Stack)."""

    def _build_python_ts_lib(self, tmp_path: Path):
        index, lib_root = _make_library(
            tmp_path,
            personas={
                "developer": {
                    "persona.md": "# Persona: Developer\n\n## Mission\nBuild.",
                },
                "devops-release": {
                    "persona.md": "# Persona: DevOps-Release\n\n## Mission\nShip.",
                },
                "ux-ui-designer": {
                    "persona.md": "# Persona: UX/UI Designer\n\n## Mission\nDesign.",
                },
            },
            expertise={
                "python": {
                    "conventions.md": (
                        "# Python\n\n## Category\nLanguages\n\n"
                        "## Applies To\n\n- developer\n\n"
                        "## Defaults\n\n- ruff is the formatter\n"
                    ),
                },
                "typescript": {
                    "conventions.md": (
                        "# TypeScript\n\n## Category\nLanguages\n\n"
                        "## Applies To\n\n- developer\n\n"
                        "## Defaults\n\n- tsconfig strict mode\n"
                    ),
                },
            },
        )
        # Manually set applies_to to mirror what build_library_index would
        # parse from the same files (the helper writes files to /stacks/
        # rather than /expertise/, so the real indexer can't find them).
        for e in index.expertise:
            if e.id in ("python", "typescript"):
                e.applies_to = ["developer"]
        return index, lib_root

    def test_lean_claude_md_lists_every_emitted_expertise(self, tmp_path: Path):
        """ADR-012 case 7: Tech Stack table is unfiltered."""
        index, lib_root = self._build_python_ts_lib(tmp_path)
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="devops-release"),
                PersonaSelection(id="ux-ui-designer"),
            ]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="typescript", order=20),
            ],
        )
        out = tmp_path / "project"
        compile_project(spec, index, lib_root, out)
        claude_md = (out / "CLAUDE.md").read_text()
        # Both expertise must appear in the Tech Stack table even though
        # ux-ui-designer and devops-release are not in either applies_to.
        assert "ai/generated/expertise/python.md" in claude_md
        assert "ai/generated/expertise/typescript.md" in claude_md

    def test_standalone_expertise_files_always_written(self, tmp_path: Path):
        """ADR-012 case 8: standalone expertise files are unfiltered."""
        index, lib_root = self._build_python_ts_lib(tmp_path)
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="ux-ui-designer"),  # neither expertise lists this persona
            ]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="typescript", order=20),
            ],
        )
        out = tmp_path / "project"
        compile_project(spec, index, lib_root, out)
        # Both standalone expertise files must be present.
        assert (out / "ai" / "generated" / "expertise" / "python.md").is_file()
        assert (out / "ai" / "generated" / "expertise" / "typescript.md").is_file()


class TestCompilePersonaSectionForwardCompat:
    """The forward-compat guard in _compile_persona_section is wired but a
    no-op today. Verify that passing spec= does not change persona file
    contents (regression guard for the no-op).
    """

    def test_persona_section_unchanged_with_or_without_spec(self, tmp_path: Path):
        from foundry_app.services.compiler import _compile_persona_section

        index, lib_root = _make_library(
            tmp_path,
            personas={
                "developer": {
                    "persona.md": "# Persona: Developer\n\n## Mission\nBuild.",
                },
            },
            expertise={
                "python": {
                    "conventions.md": (
                        "# Python\n\n## Applies To\n\n- developer\n\n"
                        "## Defaults\n- ruff\n"
                    ),
                },
                "typescript": {
                    "conventions.md": (
                        "# TS\n\n## Applies To\n\n- developer\n\n"
                        "## Defaults\n- tsconfig\n"
                    ),
                },
            },
        )
        # Mirror the on-disk applies_to into the index so the forward-compat
        # loop has realistic data even though _make_library doesn't index.
        for e in index.expertise:
            e.applies_to = ["developer"]
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="typescript", order=20),
            ],
        )
        ctx = _build_persona_context(spec, spec.team.personas[0], ["python", "typescript"])
        warnings_a: list[str] = []
        warnings_b: list[str] = []
        without_spec = _compile_persona_section(
            "developer", Path(lib_root), index, ctx, warnings_a,
        )
        with_spec = _compile_persona_section(
            "developer", Path(lib_root), index, ctx, warnings_b, spec=spec,
        )
        assert without_spec == with_spec
        # No additional warnings produced by passing spec.
        assert warnings_a == warnings_b
