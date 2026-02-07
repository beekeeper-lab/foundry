"""Tests for foundry_app.services.scaffold.scaffold_project."""

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
from foundry_app.services.scaffold import scaffold_project


def _make_spec(
    personas: list[PersonaSelection] | None = None,
    stacks: list[str] | None = None,
    project_name: str = "Test Project",
    slug: str = "test-project",
) -> CompositionSpec:
    """Build a minimal CompositionSpec for scaffold tests."""
    if personas is None:
        personas = []
    if stacks is None:
        stacks = []
    return CompositionSpec(
        project=ProjectIdentity(name=project_name, slug=slug),
        stacks=[StackSelection(id=sid) for sid in stacks],
        team=TeamConfig(personas=personas),
        hooks=HooksConfig(),
    )


# ---- Test 1: Creates CLAUDE.md with project name and team member list ----


def test_creates_claude_md_with_project_name_and_members(tmp_path: Path):
    """scaffold_project should create CLAUDE.md containing the project name and member list."""
    personas = [
        PersonaSelection(id="developer"),
        PersonaSelection(id="architect", include_agent=False),
    ]
    spec = _make_spec(personas=personas, project_name="My Awesome App")
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    claude_md = (project_dir / "CLAUDE.md").read_text()
    assert "My Awesome App" in claude_md
    assert "developer" in claude_md
    assert "architect" in claude_md
    # developer has include_agent=True by default
    assert "(agent)" in claude_md


# ---- Test 2: Creates README.md ----


def test_creates_readme_md(tmp_path: Path):
    """scaffold_project should create a README.md in the project directory."""
    spec = _make_spec(project_name="Readme Test")
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    readme = project_dir / "README.md"
    assert readme.is_file()
    content = readme.read_text()
    assert "Readme Test" in content
    assert "Foundry" in content


# ---- Test 3: Creates .claude/agents/ with one .md per persona that has include_agent=True ----


def test_creates_agent_files_for_included_personas(tmp_path: Path):
    """scaffold_project should create agent .md files only for personas with include_agent=True."""
    personas = [
        PersonaSelection(id="developer", include_agent=True),
        PersonaSelection(id="architect", include_agent=True),
        PersonaSelection(id="ba", include_agent=False),
    ]
    spec = _make_spec(personas=personas)
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    agents_dir = project_dir / ".claude" / "agents"
    assert agents_dir.is_dir()
    assert (agents_dir / "developer.md").is_file()
    assert (agents_dir / "architect.md").is_file()
    # ba has include_agent=False, so no agent file
    assert not (agents_dir / "ba.md").exists()


# ---- Test 4: Creates ai/context/project.md with stack and persona references ----


def test_creates_project_context_with_stacks_and_personas(tmp_path: Path):
    """scaffold_project should create ai/context/project.md referencing stacks and personas."""
    personas = [
        PersonaSelection(id="developer"),
        PersonaSelection(id="tech-qa"),
    ]
    spec = _make_spec(personas=personas, stacks=["python", "react"])
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    project_ctx = project_dir / "ai" / "context" / "project.md"
    assert project_ctx.is_file()
    content = project_ctx.read_text()
    assert "python" in content
    assert "react" in content
    assert "developer" in content
    assert "tech-qa" in content


# ---- Test 5: Creates ai/team/composition.yml ----


def test_creates_composition_yml(tmp_path: Path):
    """scaffold_project should create ai/team/composition.yml with the spec contents."""
    spec = _make_spec(project_name="Comp Test", slug="comp-test", stacks=["python"])
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    comp_file = project_dir / "ai" / "team" / "composition.yml"
    assert comp_file.is_file()
    content = comp_file.read_text()
    assert "comp-test" in content
    assert "python" in content


# ---- Test 6: Creates ai/outputs/<role>/README.md per persona ----


def test_creates_output_readmes_per_persona(tmp_path: Path):
    """scaffold_project should create ai/outputs/<role>/README.md for every persona."""
    personas = [
        PersonaSelection(id="developer"),
        PersonaSelection(id="architect"),
        PersonaSelection(id="tech-qa"),
    ]
    spec = _make_spec(personas=personas)
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    for persona in ["developer", "architect", "tech-qa"]:
        readme = project_dir / "ai" / "outputs" / persona / "README.md"
        assert readme.is_file(), f"Expected README.md in ai/outputs/{persona}/"
        content = readme.read_text()
        assert persona in content


# ---- Test 7: Returns StageResult with correct wrote list ----


def test_returns_stage_result_with_wrote_list(tmp_path: Path):
    """scaffold_project should return a StageResult listing all written files."""
    personas = [
        PersonaSelection(id="developer", include_agent=True),
        PersonaSelection(id="ba", include_agent=False),
    ]
    spec = _make_spec(personas=personas, stacks=["python"])
    project_dir = tmp_path / "project"

    result = scaffold_project(spec, project_dir)

    assert isinstance(result, StageResult)
    # Must include CLAUDE.md, README.md, agent for developer (not ba),
    # project.md, stack.md, decisions.md, composition.yml, and output READMEs
    assert "CLAUDE.md" in result.wrote
    assert "README.md" in result.wrote
    assert ".claude/agents/developer.md" in result.wrote  # agent file
    # ba has include_agent=False, so no ba agent file should exist
    assert ".claude/agents/ba.md" not in result.wrote
    assert "ai/context/project.md" in result.wrote
    # composition.yml is recorded with its relative path by the scaffold code
    assert "ai/team/composition.yml" in result.wrote
    # Two output READMEs (developer, ba) plus the top-level README
    readme_entries = [w for w in result.wrote if w.endswith("README.md")]
    assert len(readme_entries) >= 3


# ---- Test 8: Handles empty personas list gracefully ----


def test_handles_empty_personas_list(tmp_path: Path):
    """scaffold_project should work correctly with no personas selected."""
    spec = _make_spec(personas=[], stacks=["python"])
    project_dir = tmp_path / "project"

    result = scaffold_project(spec, project_dir)

    assert isinstance(result, StageResult)
    assert (project_dir / "CLAUDE.md").is_file()
    claude_md = (project_dir / "CLAUDE.md").read_text()
    assert "No personas selected" in claude_md
    # No agent files created
    agents_dir = project_dir / ".claude" / "agents"
    agent_files = list(agents_dir.glob("*.md"))
    assert len(agent_files) == 0
    # No output directories
    outputs_dir = project_dir / "ai" / "outputs"
    output_subdirs = [d for d in outputs_dir.iterdir() if d.is_dir()] if outputs_dir.exists() else []
    assert len(output_subdirs) == 0


# ---- Test 9: Handles empty stacks list gracefully ----


def test_handles_empty_stacks_list(tmp_path: Path):
    """scaffold_project should work correctly with no stacks selected."""
    spec = _make_spec(
        personas=[PersonaSelection(id="developer")],
        stacks=[],
    )
    project_dir = tmp_path / "project"

    result = scaffold_project(spec, project_dir)

    assert isinstance(result, StageResult)
    assert (project_dir / "CLAUDE.md").is_file()
    claude_md = (project_dir / "CLAUDE.md").read_text()
    assert "No stacks selected" in claude_md
    # Project context should still be created
    project_ctx = project_dir / "ai" / "context" / "project.md"
    assert project_ctx.is_file()
    content = project_ctx.read_text()
    assert "none" in content  # stacks_str defaults to "none"


# ---- Test 10: project.md contains Team Responsibilities with markers ----


def test_project_md_contains_team_responsibilities(tmp_path: Path):
    """project.md should list each persona under Team Responsibilities with role markers."""
    personas = [
        PersonaSelection(id="developer", include_agent=True, include_templates=False),
        PersonaSelection(id="architect", include_agent=False, include_templates=True),
    ]
    spec = _make_spec(personas=personas, stacks=["python"])
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    project_md = (project_dir / "ai" / "context" / "project.md").read_text()

    # Section header
    assert "## Team Responsibilities" in project_md

    # Display names (id.replace('-', ' ').title())
    assert "Developer" in project_md
    assert "Architect" in project_md

    # Role markers
    assert "agent" in project_md
    assert "templates" in project_md

    # Output path reference for developer
    assert "ai/outputs/developer/" in project_md


# ---- Test 11: project.md contains Conventions from selected stacks ----


def test_project_md_contains_conventions(tmp_path: Path):
    """project.md should list selected stacks under the Conventions section."""
    spec = _make_spec(
        personas=[PersonaSelection(id="developer")],
        stacks=["python", "react"],
    )
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    project_md = (project_dir / "ai" / "context" / "project.md").read_text()

    assert "## Conventions" in project_md
    assert "python" in project_md
    assert "react" in project_md


# ---- Test 12: project.md contains hooks detail with packs ----


def test_project_md_contains_hooks_detail(tmp_path: Path):
    """project.md should include Hook Packs section when packs are configured."""
    spec = CompositionSpec(
        project=ProjectIdentity(name="Hooks Test", slug="hooks-test"),
        stacks=[StackSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        hooks=HooksConfig(
            posture="hardened",
            packs=[
                HookPackSelection(
                    id="pre-commit-lint",
                    enabled=True,
                    mode="enforcing",
                ),
            ],
        ),
    )
    project_dir = tmp_path / "project"

    scaffold_project(spec, project_dir)

    project_md = (project_dir / "ai" / "context" / "project.md").read_text()

    assert "Hook Packs" in project_md
    assert "pre-commit-lint" in project_md


# ---- Test 13: result.wrote uses relative paths (no leading slash) ----


def test_scaffold_wrote_uses_relative_paths(tmp_path: Path):
    """All paths in result.wrote should be relative (no leading '/')."""
    spec = _make_spec(
        personas=[PersonaSelection(id="developer", include_agent=True)],
        stacks=["python"],
    )
    project_dir = tmp_path / "project"

    result = scaffold_project(spec, project_dir)

    assert len(result.wrote) > 0, "Expected at least one written file"
    for path_str in result.wrote:
        assert not path_str.startswith("/"), (
            f"Path should be relative but got absolute: {path_str}"
        )
