"""Smoke test: run the full Foundry pipeline end-to-end."""

from __future__ import annotations

import tempfile
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    HookPackSelection,
    HooksConfig,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    TeamConfig,
)
from foundry_app.services.generator import generate_project
from foundry_app.services.library_indexer import build_library_index
from foundry_app.services.validator import validate_generated_project

LIBRARY_ROOT = Path(__file__).parent.parent / "ai-team-library"


def test_library_index():
    """Library indexer finds personas and stacks."""
    index = build_library_index(LIBRARY_ROOT)
    persona_ids = [p.id for p in index.personas]
    assert "ba" in persona_ids
    assert "architect" in persona_ids
    assert "team-lead" in persona_ids

    stack_ids = [s.id for s in index.stacks]
    assert "python" in stack_ids
    assert "react" in stack_ids
    assert "node" in stack_ids


def _make_composition(output_root: str) -> CompositionSpec:
    return CompositionSpec(
        project=ProjectIdentity(
            name="test-project",
            slug="test-project",
            output_root=output_root,
            output_folder="test-project",
        ),
        stacks=[
            StackSelection(id="react", order=10),
            StackSelection(id="node", order=20),
        ],
        team=TeamConfig(
            personas=[
                PersonaSelection(id="ba", strictness="standard"),
                PersonaSelection(id="architect", strictness="standard"),
                PersonaSelection(id="developer", strictness="standard"),
                PersonaSelection(id="tech-qa", strictness="standard"),
            ]
        ),
        hooks=HooksConfig(
            posture="baseline",
            packs=[HookPackSelection(id="hook-policy", enabled=True, mode="enforcing")],
        ),
        generation=GenerationOptions(
            seed_tasks=True,
            write_manifest=True,
        ),
    )


def test_full_pipeline():
    """Full pipeline: validate, scaffold, compile, seed, manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        composition = _make_composition(tmpdir)
        manifest, validation = generate_project(
            composition=composition,
            library_root=LIBRARY_ROOT,
            output_root=Path(tmpdir) / "test-project",
        )

        # Validation should pass
        assert validation.is_valid, f"Validation errors: {validation.errors}"

        project_dir = Path(tmpdir) / "test-project"

        # Check scaffold outputs
        assert (project_dir / "CLAUDE.md").is_file()
        assert (project_dir / "README.md").is_file()
        assert (project_dir / "ai" / "team" / "composition.yml").is_file()

        # Check compiled members
        members_dir = project_dir / "ai" / "generated" / "members"
        assert (members_dir / "ba.md").is_file()
        assert (members_dir / "architect.md").is_file()
        assert (members_dir / "developer.md").is_file()
        assert (members_dir / "tech-qa.md").is_file()

        # Check agents
        agents_dir = project_dir / ".claude" / "agents"
        assert (agents_dir / "ba.md").is_file()
        assert (agents_dir / "architect.md").is_file()

        # Check seeded tasks
        assert (project_dir / "ai" / "tasks" / "seeded-tasks.md").is_file()

        # Check manifest
        assert (project_dir / "ai" / "generated" / "manifest.json").is_file()

        # Check output directories
        for role in ["ba", "architect", "developer", "tech-qa"]:
            assert (project_dir / "ai" / "outputs" / role).is_dir()

        # Post-generation validation should pass
        post_validation = validate_generated_project(project_dir)
        assert post_validation.is_valid, f"Post-gen errors: {post_validation.errors}"

        # Manifest should have stage data
        assert "scaffold" in manifest.stages
        assert "compile" in manifest.stages
        assert "seed" in manifest.stages
        assert len(manifest.stages["compile"].wrote) == 4  # 4 personas
