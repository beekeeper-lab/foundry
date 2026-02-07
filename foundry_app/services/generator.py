"""Generator service: orchestrates the full Foundry pipeline.

Runs: Validate -> Compile -> Scaffold -> Seed -> Write Manifest
Overlay mode: generate to temp dir, compare against target, apply plan.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    GenerationManifest,
    OverlayPlan,
)
from foundry_app.io.composition_io import save_manifest
from foundry_app.services.asset_copier import (
    copy_commands,
    copy_skills,
    write_hooks_config,
)
from foundry_app.services.compiler import compile_team
from foundry_app.services.diff_reporter import (
    backup_previous_manifest,
    generate_diff_report,
)
from foundry_app.services.overlay import (
    apply_plan,
    collect_all_wrote_paths,
    compare_trees,
    detect_orphans,
    load_previous_manifest,
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
    overlay: bool = False,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[GenerationManifest, ValidationResult, OverlayPlan | None]:
    """Run the full Foundry generation pipeline.

    Args:
        composition: The project composition spec.
        library_root: Path to the ai-team-library root.
        output_root: Override for the output directory. If None, uses
            composition.project.output_root / composition.project.output_folder.
        strictness: Validation mode -- "light", "standard", or "strict".
        overlay: If True, generate to a temp dir and overlay onto output_root.
        dry_run: If True (requires overlay), report planned changes without
            writing to the target directory.
        force: If True (requires overlay), overwrite conflicting files instead
            of writing .foundry-new sidecars.

    Returns:
        A tuple of (manifest, validation_result, overlay_plan).
        overlay_plan is None when overlay=False.
    """
    # Step 1: Validate
    logger.info(
        "Pipeline start: %s (strictness=%s)", composition.project.slug, strictness
    )
    validation = run_pre_generation_validation(
        composition, library_root, strictness
    )
    if not validation.is_valid:
        logger.warning("Validation failed: %s", validation.errors)
        return GenerationManifest(), validation, None

    # Determine output directory
    if output_root is None:
        folder = composition.project.output_folder or composition.project.slug
        output_root = Path(composition.project.output_root) / folder

    # In overlay mode, generate to a temp dir; target_dir is the real destination
    if overlay:
        target_dir = output_root
        temp_dir = Path(tempfile.mkdtemp(prefix="foundry-overlay-"))
        project_dir = temp_dir
    else:
        target_dir = None
        temp_dir = None
        project_dir = output_root

    try:
        return _run_pipeline(
            composition=composition,
            library_root=library_root,
            project_dir=project_dir,
            target_dir=target_dir,
            temp_dir=temp_dir,
            validation=validation,
            overlay=overlay,
            dry_run=dry_run,
            force=force,
        )
    finally:
        # Always clean up the temp directory in overlay mode
        if temp_dir is not None and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def _run_pipeline(
    *,
    composition: CompositionSpec,
    library_root: Path,
    project_dir: Path,
    target_dir: Path | None,
    temp_dir: Path | None,
    validation: ValidationResult,
    overlay: bool,
    dry_run: bool,
    force: bool,
) -> tuple[GenerationManifest, ValidationResult, OverlayPlan | None]:
    """Execute pipeline stages and optionally apply overlay.

    Separated from generate_project() so the try/finally for temp dir
    cleanup stays clean.
    """
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

    # In non-overlay mode, back up previous manifest before generation
    if not overlay:
        backup_previous_manifest(project_dir)

    # Step 2: Scaffold
    logger.info("Scaffolding project to %s", project_dir)
    scaffold_result = scaffold_project(composition, project_dir)
    manifest.stages["scaffold"] = scaffold_result
    logger.info("Scaffold: %d file(s)", len(scaffold_result.wrote))

    # Step 3: Compile
    members_dir = project_dir / "ai" / "generated" / "members"
    project_context = ""
    if composition.generation.inject_project_context:
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
    hooks_result = write_hooks_config(
        library_root, project_dir, composition.hooks
    )
    manifest.stages["copy_hooks"] = hooks_result
    logger.info("Hooks: %d file(s)", len(hooks_result.wrote))

    # Step 5: Seed (optional)
    if not composition.generation.seed_tasks:
        logger.debug("Task seeding skipped (disabled)")
    if composition.generation.seed_tasks:
        seed_mode = composition.generation.seed_mode
        if seed_mode == "beans":
            tasks_dir = project_dir / "ai" / "beans"
        else:
            tasks_dir = project_dir / "ai" / "tasks"
        seed_result = seed_tasks(composition, tasks_dir, mode=seed_mode)
        manifest.stages["seed"] = seed_result
        logger.info(
            "Seed: %d task(s) (mode=%s)", len(seed_result.wrote), seed_mode
        )

    # --- Overlay mode: Phase 2 (compare and apply) ---
    if overlay:
        assert target_dir is not None
        assert temp_dir is not None

        previous_manifest = load_previous_manifest(target_dir)
        current_files = collect_all_wrote_paths(manifest)

        logger.info("Comparing against overlay target: %s", target_dir)
        plan = compare_trees(
            temp_dir=temp_dir,
            target_dir=target_dir,
            previous_manifest=previous_manifest,
            force=force,
        )

        # Detect orphans
        orphans = detect_orphans(previous_manifest, current_files)
        plan.orphans = orphans

        if dry_run:
            # Build summary for the manifest (informational only)
            from foundry_app.core.models import OverlaySummary

            manifest.overlay_summary = OverlaySummary(
                mode="dry_run",
                target_dir=str(target_dir),
                files_created=len(plan.creates),
                files_unchanged=len(plan.unchanged),
                files_conflicted=len(plan.conflicts),
                orphaned_files=orphans,
            )
            logger.info("Dry-run complete: no files written to target")
        else:
            # Back up previous manifest in the target dir
            backup_previous_manifest(target_dir)

            # Apply the overlay plan
            logger.info("Applying overlay plan to %s", target_dir)
            overlay_summary = apply_plan(plan, temp_dir, target_dir)
            manifest.overlay_summary = overlay_summary

            # Write manifest to the target directory
            if composition.generation.write_manifest:
                manifest_path = (
                    target_dir / "ai" / "generated" / "manifest.json"
                )
                save_manifest(manifest, manifest_path)

            # Diff report in overlay mode (optional)
            if composition.generation.write_diff_report:
                diff_result = generate_diff_report(target_dir, manifest)
                manifest.stages["diff"] = diff_result

        logger.info("Pipeline complete (overlay): %d stage(s)", len(manifest.stages))
        return manifest, validation, plan

    # --- Standard (non-overlay) mode ---
    # Step 6: Write manifest
    if composition.generation.write_manifest:
        manifest_path = project_dir / "ai" / "generated" / "manifest.json"
        save_manifest(manifest, manifest_path)

    # Step 7: Diff report (optional)
    if composition.generation.write_diff_report:
        diff_result = generate_diff_report(project_dir, manifest)
        manifest.stages["diff"] = diff_result

    logger.info("Pipeline complete: %d stage(s)", len(manifest.stages))
    return manifest, validation, None
