"""Tests for foundry_app.services.compiler — CLAUDE.md compilation from library."""

from pathlib import Path

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
from foundry_app.services.compiler import (
    _build_context,
    _build_persona_name_map,
    _filter_collaboration_table,
    _filter_defer_references,
    _filter_persona_references,
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
        stacks=[StackSelection(id="python", order=10)],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


def _make_library(tmp_path: Path, personas=None, stacks=None) -> tuple[LibraryIndex, Path]:
    """Create a minimal library on disk and return (index, library_root).

    Args:
        tmp_path: pytest tmp_path fixture.
        personas: dict mapping persona_id -> dict of files.
            e.g. {"developer": {"persona.md": "# Dev", "outputs.md": "# Out"}}
        stacks: dict mapping stack_id -> dict of files.
            e.g. {"python": {"conventions.md": "# Python Conventions"}}

    Returns:
        Tuple of (LibraryIndex, library_root_path).
    """
    lib_root = tmp_path / "library"
    personas = personas or {}
    stacks = stacks or {}

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

    stack_infos: list[StackInfo] = []
    for sid, files in stacks.items():
        stack_dir = lib_root / "stacks" / sid
        stack_dir.mkdir(parents=True, exist_ok=True)
        for fname, content in files.items():
            (stack_dir / fname).write_text(content, encoding="utf-8")
        stack_infos.append(StackInfo(
            id=sid,
            path=str(stack_dir),
            files=list(files.keys()),
        ))

    index = LibraryIndex(
        library_root=str(lib_root),
        personas=persona_infos,
        stacks=stack_infos,
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
            '{{ stacks | join(", ") }}',
            {"stacks": "python,typescript"},
        )
        assert result == "python, typescript"

    def test_join_single_item(self):
        result = _substitute(
            '{{ stacks | join(", ") }}',
            {"stacks": "python"},
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

    def test_includes_stacks_comma_separated(self):
        spec = _make_spec(stacks=[
            StackSelection(id="python", order=10),
            StackSelection(id="typescript", order=20),
        ])
        ctx = _build_context(spec)
        assert "python" in ctx["stacks"]
        assert "typescript" in ctx["stacks"]

    def test_stacks_sorted_by_order(self):
        spec = _make_spec(stacks=[
            StackSelection(id="typescript", order=20),
            StackSelection(id="python", order=10),
        ])
        ctx = _build_context(spec)
        parts = ctx["stacks"].split(",")
        assert parts[0] == "python"
        assert parts[1] == "typescript"

    def test_empty_stacks(self):
        spec = _make_spec(stacks=[])
        ctx = _build_context(spec)
        assert ctx["stacks"] == ""

    def test_single_stack(self):
        spec = _make_spec(stacks=[StackSelection(id="python", order=10)])
        ctx = _build_context(spec)
        assert ctx["stacks"] == "python"


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

    def test_wrote_contains_only_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert result.wrote == ["CLAUDE.md"]

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

    def test_contains_persona_content(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer\n\nBuild great code."},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "Build great code." in content

    def test_contains_stack_heading(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            stacks={"python": {"conventions.md": "# Python Conventions"}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Technology Stacks" in content

    def test_contains_stack_content(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            stacks={"python": {"conventions.md": "Use type hints everywhere."}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "Use type hints everywhere." in content

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

    def test_includes_persona_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "PERSONA_CONTENT"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "PERSONA_CONTENT" in content

    def test_includes_outputs_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "PERSONA",
                "outputs.md": "OUTPUTS_CONTENT",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "OUTPUTS_CONTENT" in content

    def test_includes_prompts_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "PERSONA",
                "prompts.md": "PROMPTS_CONTENT",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "PROMPTS_CONTENT" in content

    def test_persona_files_in_order(self, tmp_path: Path):
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
        content = (output / "CLAUDE.md").read_text()
        assert content.index("AAA_PERSONA") < content.index("BBB_OUTPUTS")
        assert content.index("BBB_OUTPUTS") < content.index("CCC_PROMPTS")

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

    def test_all_personas_included(self, tmp_path: Path):
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
        content = (output / "CLAUDE.md").read_text()
        assert "DEV_CONTENT" in content
        assert "ARCH_CONTENT" in content

    def test_persona_order_matches_spec(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "DEV_FIRST"},
            "architect": {"persona.md": "ARCH_SECOND"},
        })
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(id="architect"),
        ]))
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert content.index("DEV_FIRST") < content.index("ARCH_SECOND")

    def test_reversed_persona_order(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "DEV_SECOND"},
            "architect": {"persona.md": "ARCH_FIRST"},
        })
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id="architect"),
            PersonaSelection(id="developer"),
        ]))
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert content.index("ARCH_FIRST") < content.index("DEV_SECOND")

    def test_three_personas(self, tmp_path: Path):
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
        content = (output / "CLAUDE.md").read_text()
        assert "AAA" in content
        assert "BBB" in content
        assert "CCC" in content


# ---------------------------------------------------------------------------
# compile_project — multiple stacks
# ---------------------------------------------------------------------------


class TestMultipleStacks:

    def test_all_stacks_included(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            stacks={
                "python": {"conventions.md": "PYTHON_CONV"},
                "typescript": {"conventions.md": "TS_CONV"},
            },
        )
        spec = _make_spec(stacks=[
            StackSelection(id="python", order=10),
            StackSelection(id="typescript", order=20),
        ])
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "PYTHON_CONV" in content
        assert "TS_CONV" in content

    def test_stacks_sorted_by_order(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            stacks={
                "python": {"conventions.md": "PYTHON_FIRST"},
                "typescript": {"conventions.md": "TS_SECOND"},
            },
        )
        spec = _make_spec(stacks=[
            StackSelection(id="typescript", order=20),
            StackSelection(id="python", order=10),
        ])
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert content.index("PYTHON_FIRST") < content.index("TS_SECOND")

    def test_stacks_same_order_sorted_alphabetically(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            stacks={
                "typescript": {"conventions.md": "TS_CONTENT"},
                "python": {"conventions.md": "PY_CONTENT"},
            },
        )
        spec = _make_spec(stacks=[
            StackSelection(id="typescript", order=0),
            StackSelection(id="python", order=0),
        ])
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        # python comes before typescript alphabetically
        assert content.index("PY_CONTENT") < content.index("TS_CONTENT")

    def test_personas_before_stacks(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "PERSONA_SECTION"}},
            stacks={"python": {"conventions.md": "STACK_SECTION"}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert content.index("PERSONA_SECTION") < content.index("STACK_SECTION")


# ---------------------------------------------------------------------------
# compile_project — template substitution in content
# ---------------------------------------------------------------------------


class TestTemplateSubstitutionInContent:

    def test_project_name_substituted_in_persona(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "Working on {{ project_name }}"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "Working on Test Project" in content
        assert "{{ project_name }}" not in content

    def test_stacks_join_substituted_in_persona(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": 'Stack: {{ stacks | join(", ") }}',
            },
        })
        spec = _make_spec(stacks=[
            StackSelection(id="python", order=10),
            StackSelection(id="typescript", order=20),
        ])
        # Need stacks in library too for them to compile
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "Stack: python, typescript" in content

    def test_substitution_in_outputs_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "# Dev",
                "outputs.md": "Deliver for {{ project_name }}",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "Deliver for Test Project" in content

    def test_substitution_in_prompts_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {
                "persona.md": "# Dev",
                "prompts.md": "Context for {{ project_name }}",
            },
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "Context for Test Project" in content

    def test_substitution_in_stack_conventions(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            stacks={"python": {"conventions.md": "For {{ project_name }}"}},
        )
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "For Test Project" in content


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
        assert any("nonexistent" in w and "not found" in w for w in result.warnings)

    def test_warns_on_missing_persona_md(self, tmp_path: Path):
        output = tmp_path / "project"
        # Persona dir exists but has no persona.md
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"outputs.md": "# Outputs only"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert any("missing persona.md" in w for w in result.warnings)

    def test_warns_on_missing_stack_in_index(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })  # no stacks in library
        spec = _make_spec(stacks=[StackSelection(id="nonexistent")])
        result = compile_project(spec, index, lib_root, output)
        assert any("nonexistent" in w and "not found" in w for w in result.warnings)

    def test_warns_on_missing_conventions_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            stacks={"python": {"readme.md": "Not conventions"}},
        )
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        assert any("missing conventions.md" in w for w in result.warnings)

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
            stacks={"python": {"conventions.md": "# Python"}},
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
# compile_project — no personas / no stacks
# ---------------------------------------------------------------------------


class TestEmptySelections:

    def test_no_personas_still_creates_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            stacks={"python": {"conventions.md": "# Python"}},
        )
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = compile_project(spec, index, lib_root, output)
        assert (output / "CLAUDE.md").exists()
        assert "CLAUDE.md" in result.wrote

    def test_no_personas_no_team_heading(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(
            tmp_path,
            stacks={"python": {"conventions.md": "# Python"}},
        )
        spec = _make_spec(team=TeamConfig(personas=[]))
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Team" not in content

    def test_no_stacks_still_creates_claude_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec(stacks=[])
        result = compile_project(spec, index, lib_root, output)
        assert (output / "CLAUDE.md").exists()
        assert "CLAUDE.md" in result.wrote

    def test_no_stacks_no_stacks_heading(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Dev"},
        })
        spec = _make_spec(stacks=[])
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "## Technology Stacks" not in content

    def test_no_personas_no_stacks(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path)
        spec = _make_spec(team=TeamConfig(personas=[]), stacks=[])
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
            stacks={
                "python": {"conventions.md": "# Python"},
                "typescript": {"conventions.md": "# TS"},
            },
        )
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
            stacks=[
                StackSelection(id="python", order=10),
                StackSelection(id="typescript", order=20),
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
            stacks={"python": {"conventions.md": "# Python"}},
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
        content = (output / "CLAUDE.md").read_text()
        assert "OUTPUTS_ONLY" in content
        assert any("missing persona.md" in w for w in result.warnings)

    def test_persona_with_only_prompts_md(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"prompts.md": "PROMPTS_ONLY"},
        })
        spec = _make_spec()
        result = compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "PROMPTS_ONLY" in content

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
        content = (output / "CLAUDE.md").read_text()
        assert "Acme & Sons (v2.0)" in content

    def test_unicode_in_content(self, tmp_path: Path):
        output = tmp_path / "project"
        index, lib_root = _make_library(tmp_path, personas={
            "developer": {"persona.md": "# Developer \u2014 Build \u2728"},
        })
        spec = _make_spec()
        compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        assert "\u2014" in content
        assert "\u2728" in content

    def test_large_number_of_personas(self, tmp_path: Path):
        output = tmp_path / "project"
        personas = {f"persona-{i}": {"persona.md": f"CONTENT_{i}"} for i in range(10)}
        index, lib_root = _make_library(tmp_path, personas=personas)
        spec = _make_spec(team=TeamConfig(personas=[
            PersonaSelection(id=f"persona-{i}") for i in range(10)
        ]))
        result = compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        for i in range(10):
            assert f"CONTENT_{i}" in content
        assert "CLAUDE.md" in result.wrote

    def test_large_number_of_stacks(self, tmp_path: Path):
        output = tmp_path / "project"
        stacks = {f"stack-{i}": {"conventions.md": f"STACK_{i}"} for i in range(10)}
        index, lib_root = _make_library(
            tmp_path,
            personas={"developer": {"persona.md": "# Dev"}},
            stacks=stacks,
        )
        spec = _make_spec(stacks=[
            StackSelection(id=f"stack-{i}", order=i) for i in range(10)
        ])
        result = compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()
        for i in range(10):
            assert f"STACK_{i}" in content

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
            stacks={"python": {"conventions.md": ""}},
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


# ---------------------------------------------------------------------------
# compile_project — full integration
# ---------------------------------------------------------------------------


class TestFullIntegration:

    def test_full_compilation_structure(self, tmp_path: Path):
        """Verify the full structure of a compiled CLAUDE.md."""
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
                    "persona.md": '# Developer using {{ stacks | join(", ") }}',
                    "outputs.md": "# Developer Outputs",
                    "prompts.md": "# Developer Prompts",
                },
            },
            stacks={
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
            stacks=[
                StackSelection(id="python", order=10),
                StackSelection(id="clean-code", order=20),
            ],
        )
        result = compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()

        # Structure checks
        assert content.startswith("# Full Test")
        assert "## Team" in content
        assert "## Technology Stacks" in content

        # Persona content
        assert "# Team Lead for Full Test" in content
        assert "# Team Lead Outputs" in content
        assert "# Team Lead Prompts" in content
        assert "# Developer using python, clean-code" in content
        assert "# Developer Outputs" in content
        assert "# Developer Prompts" in content

        # Stack content
        assert "# Python Conventions" in content
        assert "# Clean Code" in content

        # Order: header -> team -> stacks
        assert content.index("## Team") < content.index("## Technology Stacks")
        assert content.index("Team Lead") < content.index("Developer")
        assert content.index("Python Conventions") < content.index("Clean Code")

        # No warnings
        assert result.warnings == []
        assert result.wrote == ["CLAUDE.md"]

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
            stacks={
                "python": {"conventions.md": "# Python"},
                # missing-stack not in library
            },
        )
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
            stacks=[
                StackSelection(id="python", order=10),
                StackSelection(id="missing-stack", order=20),
            ],
        )
        result = compile_project(spec, index, lib_root, output)
        content = (output / "CLAUDE.md").read_text()

        # Both personas compiled
        assert "# Dev" in content
        assert "# Arch" in content

        # Python stack compiled
        assert "# Python" in content

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
        content = (output / "CLAUDE.md").read_text()

        # Developer should be in the collab table
        assert "| Developer" in content
        # Architect and Tech-QA should NOT be in the collab table
        assert "| Architect" not in content
        assert "| Tech-QA" not in content

    def test_filters_defer_references_in_compiled_output(self, tmp_path: Path):
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
        content = (output / "CLAUDE.md").read_text()

        # "(defer to Developer)" should remain
        assert "(defer to Developer)" in content
        # "(defer to Technical Writer)" should be removed
        assert "(defer to Technical Writer)" not in content
        # But the constraint itself should remain
        assert "- Write docs" in content

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
        content = (output / "CLAUDE.md").read_text()

        assert "| Developer" in content
        assert "| Architect" in content

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
        content = (output / "CLAUDE.md").read_text()

        assert "## Collaboration" not in content

    def test_unknown_entities_preserved_in_collab_table(self, tmp_path: Path):
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
        content = (output / "CLAUDE.md").read_text()

        # Stakeholders should remain (unknown entity)
        assert "Stakeholders" in content
        # Developer should be removed (known, not selected)
        assert "| Developer" not in content
