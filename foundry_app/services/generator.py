"""Generator service: orchestrates the full Foundry pipeline.

Runs: Validate -> Compile -> Scaffold -> Seed -> Write Manifest
"""

from __future__ import annotations

import logging
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    GenerationManifest,
)
from foundry_app.io.composition_io import save_manifest
from foundry_app.services.asset_copier import copy_commands, copy_skills, write_hooks_config
from foundry_app.services.compiler import compile_team
from foundry_app.services.diff_reporter import (
    backup_previous_manifest,
    generate_diff_report,
)
from foundry_app.services.scaffold import scaffold_project
from foundry_app.services.seeder import seed_tasks
from foundry_app.services.validator import (
    ValidationResult,
    run_pre_generation_validation,
)

logger = logging.getLogger(__name__)


def generate_project(
    composition: CompositionSpec,
    library_root: Path,
    output_root: Path | None = None,
    strictness: str = "standard",
) -> tuple[GenerationManifest, ValidationResult]:
    """Run the full Foundry generation pipeline.

    Args:
        composition: The project composition spec.
        library_root: Path to the ai-team-library root.
        output_root: Override for the output directory. If None, uses
            composition.project.output_root / composition.project.output_folder.
        strictness: Validation mode — "light", "standard", or "strict".

    Returns:
        A tuple of (manifest, validation_result). If validation fails,
        the manifest will be empty and validation_result.is_valid is False.
    """
    # Step 1: Validate
    logger.info("Pipeline start: %s (strictness=%s)", composition.project.slug, strictness)
    validation = run_pre_generation_validation(composition, library_root, strictness)
    if not validation.is_valid:
        logger.warning("Validation failed: %s", validation.errors)
        return GenerationManifest(), validation

    # Determine output directory
    if output_root is None:
        folder = composition.project.output_folder or composition.project.slug
        output_root = Path(composition.project.output_root) / folder

    project_dir = output_root
    manifest = GenerationManifest(composition_snapshot=composition)

    # Try to capture library version
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=library_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            manifest.library_version = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Back up previous manifest before generation overwrites it
    backup_previous_manifest(project_dir)

    # Step 2: Scaffold
    logger.info("Scaffolding project to %s", project_dir)
    scaffold_result = scaffold_project(composition, project_dir)
    manifest.stages["scaffold"] = scaffold_result
    logger.info("Scaffold: %d file(s)", len(scaffold_result.wrote))

    # Step 3: Compile
    members_dir = project_dir / "ai" / "generated" / "members"
    project_context = ""
    context_file = project_dir / "ai" / "context" / "project.md"
    if context_file.is_file():
        project_context = context_file.read_text()

    logger.info("Compiling team members to %s", members_dir)
    compile_result = compile_team(
        composition=composition,
        library_root=library_root,
        output_dir=members_dir,
        project_context=project_context,
    )
    manifest.stages["compile"] = compile_result
    logger.info("Compile: %d file(s)", len(compile_result.wrote))

    # Step 4: Copy Assets (skills, commands, hooks from library)
    persona_ids = [p.id for p in composition.team.personas]

    logger.info("Copying skills from library")
    skills_result = copy_skills(library_root, project_dir, persona_ids)
    manifest.stages["copy_skills"] = skills_result
    logger.info("Skills: %d file(s)", len(skills_result.wrote))

    logger.info("Copying commands from library")
    commands_result = copy_commands(library_root, project_dir, persona_ids)
    manifest.stages["copy_commands"] = commands_result
    logger.info("Commands: %d file(s)", len(commands_result.wrote))

    logger.info("Copying hook docs from library")
    hooks_result = write_hooks_config(library_root, project_dir, composition.hooks)
    manifest.stages["copy_hooks"] = hooks_result
    logger.info("Hooks: %d file(s)", len(hooks_result.wrote))

    # Step 5: Seed (optional)
    if not composition.generation.seed_tasks:
        logger.debug("Task seeding skipped (disabled)")
    if composition.generation.seed_tasks:
        tasks_dir = project_dir / "ai" / "tasks"
        seed_mode = composition.generation.seed_mode
        seed_result = seed_tasks(composition, tasks_dir, mode=seed_mode)
        manifest.stages["seed"] = seed_result
        logger.info("Seed: %d task(s) (mode=%s)", len(seed_result.wrote), seed_mode)

    # Step 5: Write manifest
    if composition.generation.write_manifest:
        manifest_path = project_dir / "ai" / "generated" / "manifest.json"
        save_manifest(manifest, manifest_path)

    # Step 6: Diff report (optional)
    if composition.generation.write_diff_report:
        diff_result = generate_diff_report(project_dir, manifest)
        manifest.stages["diff"] = diff_result

    logger.info("Pipeline complete: %d stage(s)", len(manifest.stages))
    return manifest, validation
