"""Tests for foundry_app.services.compiler: compile_team member prompt generation."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    HookPackSelection,
    HooksConfig,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    StageResult,
    TeamConfig,
)
from foundry_app.services.compiler import compile_team

LIBRARY_ROOT = Path(__file__).parent.parent / "ai-team-library"


def _make_spec(personas: list[str], stacks: list[str] | None = None) -> CompositionSpec:
    """Build a minimal CompositionSpec for compiler tests."""
    if stacks is None:
        stacks = ["python"]
    return CompositionSpec(
        project=ProjectIdentity(name="Compiler Test", slug="compiler-test"),
        stacks=[StackSelection(id=sid) for sid in stacks],
        team=TeamConfig(personas=[PersonaSelection(id=pid) for pid in personas]),
        hooks=HooksConfig(),
    )


def test_compile_produces_member_files(tmp_path: Path):
    """compile_team should create one .md file per selected persona."""
    spec = _make_spec(["team-lead", "developer"])
    output_dir = tmp_path / "members"

    compile_team(spec, LIBRARY_ROOT, output_dir)

    assert (output_dir / "team-lead.md").is_file()
    assert (output_dir / "developer.md").is_file()


def test_compiled_member_contains_persona_content(tmp_path: Path):
    """Compiled member file should embed content from the persona's persona.md."""
    spec = _make_spec(["team-lead"])
    output_dir = tmp_path / "members"

    compile_team(spec, LIBRARY_ROOT, output_dir)

    compiled_text = (output_dir / "team-lead.md").read_text()

    # The compiled prompt should contain the persona's own content.
    # Read the source persona.md to grab a representative snippet.
    source_text = (LIBRARY_ROOT / "personas" / "team-lead" / "persona.md").read_text()
    # Use the first non-empty, non-heading line as a probe.
    probe_lines = [
        line.strip()
        for line in source_text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert probe_lines, "persona.md has no content lines to verify"
    # At least one content line from the source should appear in the compiled output.
    assert any(line in compiled_text for line in probe_lines)


def test_compile_returns_stage_result(tmp_path: Path):
    """compile_team should return a StageResult listing written files."""
    spec = _make_spec(["team-lead", "developer"])
    output_dir = tmp_path / "members"

    result = compile_team(spec, LIBRARY_ROOT, output_dir)

    assert isinstance(result, StageResult)
    assert "team-lead.md" in result.wrote
    assert "developer.md" in result.wrote
    assert len(result.wrote) == 2


def test_compile_warns_for_missing_persona(tmp_path: Path):
    """compile_team should warn (not crash) when a persona directory is missing."""
    spec = _make_spec(["team-lead", "ghost-persona"])
    output_dir = tmp_path / "members"

    result = compile_team(spec, LIBRARY_ROOT, output_dir)

    # team-lead should still be written
    assert "team-lead.md" in result.wrote
    # ghost-persona should produce a warning
    assert any("ghost-persona" in w for w in result.warnings)


def test_compile_includes_stack_context(tmp_path: Path):
    """Compiled member file should contain stack context from the library."""
    spec = _make_spec(["developer"], stacks=["python"])
    output_dir = tmp_path / "members"

    compile_team(spec, LIBRARY_ROOT, output_dir)

    compiled_text = (output_dir / "developer.md").read_text()
    assert "Stack Context" in compiled_text
    # The python stack section should be referenced
    assert "python" in compiled_text.lower()


# ---------------------------------------------------------------------------
# Increment 9/10 Tests — self-contained with tmp_path library fixtures
# ---------------------------------------------------------------------------


def _create_persona_dir(library_root: Path, persona_id: str) -> None:
    """Create a minimal persona directory with persona.md, outputs.md, prompts.md."""
    persona_dir = library_root / "personas" / persona_id
    persona_dir.mkdir(parents=True, exist_ok=True)
    (persona_dir / "persona.md").write_text(
        f"# {persona_id.replace('-', ' ').title()}\n\n"
        f"You are the {persona_id} on this team.\n"
    )
    (persona_dir / "outputs.md").write_text(
        f"# Expected Outputs for {persona_id}\n\n"
        f"- Deliver artifacts relevant to the {persona_id} role.\n"
    )
    (persona_dir / "prompts.md").write_text(
        f"# Invocation Prompts for {persona_id}\n\n"
        f"Use these prompts to invoke the {persona_id}.\n"
    )


def _create_stack_dir(library_root: Path, stack_id: str) -> None:
    """Create a minimal stack directory with a stack.md file."""
    stack_dir = library_root / "stacks" / stack_id
    stack_dir.mkdir(parents=True, exist_ok=True)
    (stack_dir / "stack.md").write_text(
        f"# {stack_id.title()} Stack\n\n"
        f"Follow {stack_id} best practices.\n"
    )


def _make_spec_local(
    personas: list[PersonaSelection] | None = None,
    stacks: list[str] | None = None,
    project_name: str = "Test Project",
    slug: str = "test-project",
    hooks: HooksConfig | None = None,
) -> CompositionSpec:
    """Build a minimal CompositionSpec for self-contained compiler tests."""
    if personas is None:
        personas = []
    if stacks is None:
        stacks = []
    if hooks is None:
        hooks = HooksConfig()
    return CompositionSpec(
        project=ProjectIdentity(name=project_name, slug=slug),
        stacks=[StackSelection(id=sid) for sid in stacks],
        team=TeamConfig(personas=personas),
        hooks=hooks,
    )


# ---- Test 6: compile_team produces member files (self-contained) ----


def test_compile_team_produces_member_files(tmp_path: Path):
    """compile_team should create a compiled .md file for each agent persona."""
    library_root = tmp_path / "library"
    output_dir = tmp_path / "output"

    _create_persona_dir(library_root, "developer")
    _create_stack_dir(library_root, "python")

    spec = _make_spec_local(
        personas=[PersonaSelection(id="developer", include_agent=True)],
        stacks=["python"],
    )

    result = compile_team(spec, library_root, output_dir)

    assert isinstance(result, StageResult)
    # The compiled file should exist
    compiled_file = output_dir / "developer.md"
    assert compiled_file.is_file(), "Expected compiled member file developer.md"

    content = compiled_file.read_text()
    # Header contains "Compiled Member Prompt"
    assert "Compiled Member Prompt" in content
    # Contains the persona id reference
    assert "developer" in content
    # Recorded in the result
    assert "developer.md" in result.wrote


# ---- Test 7: compile_team includes hooks and policies ----


def test_compile_team_includes_hooks_and_policies(tmp_path: Path):
    """compile_team should embed Hooks & Policies section when hook packs are configured."""
    library_root = tmp_path / "library"
    output_dir = tmp_path / "output"

    _create_persona_dir(library_root, "developer")
    _create_stack_dir(library_root, "python")

    hooks = HooksConfig(
        posture="hardened",
        packs=[
            HookPackSelection(
                id="pre-commit-lint",
                mode="enforcing",
                enabled=True,
            ),
        ],
    )
    spec = _make_spec_local(
        personas=[PersonaSelection(id="developer", include_agent=True)],
        stacks=["python"],
        hooks=hooks,
    )

    compile_team(spec, library_root, output_dir)

    compiled_file = output_dir / "developer.md"
    assert compiled_file.is_file()

    content = compiled_file.read_text()
    assert "Hooks & Policies" in content
    assert "pre-commit-lint" in content


# ---- Test 8: compile_team skips non-agent personas ----


def test_compile_team_skips_non_agent_personas(tmp_path: Path):
    """compile_team should not generate a file for personas with include_agent=False."""
    library_root = tmp_path / "library"
    output_dir = tmp_path / "output"

    _create_persona_dir(library_root, "ba")

    spec = _make_spec_local(
        personas=[PersonaSelection(id="ba", include_agent=False)],
        stacks=[],
    )

    result = compile_team(spec, library_root, output_dir)

    assert isinstance(result, StageResult)
    # No file should be generated for ba
    ba_file = output_dir / "ba.md"
    assert not ba_file.exists(), "ba.md should not exist when include_agent=False"
    # Nothing written
    assert "ba.md" not in result.wrote


# ---- Test 9: compile_team warns on missing persona directory ----


def test_compile_team_warns_on_missing_persona_dir(tmp_path: Path):
    """compile_team should add a warning when a persona's library directory is missing."""
    library_root = tmp_path / "library"
    output_dir = tmp_path / "output"

    # Ensure the library root exists but do NOT create the persona directory
    library_root.mkdir(parents=True, exist_ok=True)

    spec = _make_spec_local(
        personas=[PersonaSelection(id="ghost-persona", include_agent=True)],
        stacks=[],
    )

    result = compile_team(spec, library_root, output_dir)

    assert isinstance(result, StageResult)
    assert len(result.warnings) > 0, "Expected at least one warning for missing persona dir"
    # The warning should reference the missing persona id
    assert any("ghost-persona" in w for w in result.warnings), (
        f"Expected warning about 'ghost-persona', got: {result.warnings}"
    )
    # No file should have been written for the missing persona
    ghost_file = output_dir / "ghost-persona.md"
    assert not ghost_file.exists()


# ---------------------------------------------------------------------------
# Jinja2 rendering edge cases — self-contained with tmp_path library fixtures
# ---------------------------------------------------------------------------


def test_jinja2_renders_project_name(tmp_path: Path):
    """Jinja2 should replace {{ project_name }} with the actual project name."""
    library_root = tmp_path / "library"
    output_dir = tmp_path / "output"

    persona_id = "dev"
    persona_dir = library_root / "personas" / persona_id
    persona_dir.mkdir(parents=True, exist_ok=True)
    (persona_dir / "persona.md").write_text(
        "# Developer\n\nYou are working on {{ project_name }}.\n"
    )
    (persona_dir / "outputs.md").write_text("# Outputs\n")
    (persona_dir / "prompts.md").write_text("# Prompts\n")

    spec = _make_spec_local(
        personas=[PersonaSelection(id=persona_id, include_agent=True)],
        stacks=[],
        project_name="My Cool App",
    )

    compile_team(spec, library_root, output_dir)

    compiled_text = (output_dir / f"{persona_id}.md").read_text()
    assert "My Cool App" in compiled_text, (
        "Expected {{ project_name }} to be rendered as 'My Cool App'"
    )
    assert "{{ project_name }}" not in compiled_text, (
        "Raw Jinja2 placeholder should not appear in compiled output"
    )


def test_jinja2_undefined_variable_renders_empty(tmp_path: Path):
    """Undefined Jinja2 variables render as empty strings (Jinja2 default behavior).

    The default Jinja2 Environment uses ``Undefined`` which silently renders to
    an empty string. The ``_render_template`` catch for ``UndefinedError`` is a
    safety net but doesn't fire with default settings.
    """
    library_root = tmp_path / "library"
    output_dir = tmp_path / "output"

    persona_id = "dev"
    persona_dir = library_root / "personas" / persona_id
    persona_dir.mkdir(parents=True, exist_ok=True)
    (persona_dir / "persona.md").write_text(
        "# Developer\n\nValue: {{ nonexistent_var }}.\n"
    )
    (persona_dir / "outputs.md").write_text("# Outputs\n")
    (persona_dir / "prompts.md").write_text("# Prompts\n")

    spec = _make_spec_local(
        personas=[PersonaSelection(id=persona_id, include_agent=True)],
        stacks=[],
    )

    compile_team(spec, library_root, output_dir)

    compiled_text = (output_dir / f"{persona_id}.md").read_text()
    # Jinja2's default Environment silently renders undefined variables as ""
    assert "{{ nonexistent_var }}" not in compiled_text, (
        "Raw placeholder should not appear — Jinja2 replaces undefined vars with ''"
    )
    # The surrounding text should still be present with the variable gone
    assert "Value: ." in compiled_text, (
        "The surrounding text should remain with the undefined variable rendered as empty"
    )


def test_jinja2_syntax_error_returns_original(tmp_path: Path):
    """Invalid Jinja2 syntax should fall back gracefully to the raw template text."""
    library_root = tmp_path / "library"
    output_dir = tmp_path / "output"

    persona_id = "dev"
    persona_dir = library_root / "personas" / persona_id
    persona_dir.mkdir(parents=True, exist_ok=True)
    (persona_dir / "persona.md").write_text(
        "# Developer\n\nBroken: {% invalid syntax %}.\n"
    )
    (persona_dir / "outputs.md").write_text("# Outputs\n")
    (persona_dir / "prompts.md").write_text("# Prompts\n")

    spec = _make_spec_local(
        personas=[PersonaSelection(id=persona_id, include_agent=True)],
        stacks=[],
    )

    # Should not crash
    result = compile_team(spec, library_root, output_dir)

    assert isinstance(result, StageResult)
    compiled_file = output_dir / f"{persona_id}.md"
    assert compiled_file.is_file(), "Compiled file should still be written"
    compiled_text = compiled_file.read_text()
    # The raw broken text should be preserved since _render_template catches TemplateSyntaxError
    assert "{% invalid syntax %}" in compiled_text, (
        "Broken Jinja2 syntax should be preserved as raw text"
    )


def test_jinja2_renders_stacks_list(tmp_path: Path):
    """Jinja2 should render {{ stacks | join(', ') }} with the actual stack list."""
    library_root = tmp_path / "library"
    output_dir = tmp_path / "output"

    persona_id = "dev"
    persona_dir = library_root / "personas" / persona_id
    persona_dir.mkdir(parents=True, exist_ok=True)
    (persona_dir / "persona.md").write_text(
        "# Developer\n\nStacks: {{ stacks | join(\", \") }}.\n"
    )
    (persona_dir / "outputs.md").write_text("# Outputs\n")
    (persona_dir / "prompts.md").write_text("# Prompts\n")

    _create_stack_dir(library_root, "python")
    _create_stack_dir(library_root, "react")

    spec = _make_spec_local(
        personas=[PersonaSelection(id=persona_id, include_agent=True)],
        stacks=["python", "react"],
    )

    compile_team(spec, library_root, output_dir)

    compiled_text = (output_dir / f"{persona_id}.md").read_text()
    assert "python, react" in compiled_text, (
        "Expected stacks list to be rendered as 'python, react'"
    )
    assert "{{ stacks" not in compiled_text, (
        "Raw Jinja2 placeholder should not appear in compiled output"
    )
