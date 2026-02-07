"""Generator orchestrator — coordinates the full project generation pipeline."""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    FileAction,
    FileActionType,
    GenerationManifest,
    LibraryIndex,
    OverlayPlan,
    StageResult,
    Strictness,
    ValidationResult,
)
from foundry_app.services.library_indexer import build_library_index
from foundry_app.services.scaffold import scaffold_project
from foundry_app.services.validator import run_pre_generation_validation

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Stub stages (to be replaced by real services in future beans)
# ---------------------------------------------------------------------------


def _stub_compile(spec: CompositionSpec, library: LibraryIndex, output_dir: Path) -> StageResult:
    """Stub for the compiler service (BEAN-027)."""
    logger.info("Compile stage: stub (BEAN-027 not yet implemented)")
    return StageResult()


def _stub_copy_assets(
    spec: CompositionSpec, library: LibraryIndex, output_dir: Path,
) -> StageResult:
    """Stub for the asset copier service (BEAN-028)."""
    logger.info("Copy assets stage: stub (BEAN-028 not yet implemented)")
    return StageResult()


def _stub_seed_tasks(spec: CompositionSpec, output_dir: Path) -> StageResult:
    """Stub for the seeder service (BEAN-029)."""
    logger.info("Seed tasks stage: stub (BEAN-029 not yet implemented)")
    return StageResult()


def _stub_write_safety(spec: CompositionSpec, output_dir: Path) -> StageResult:
    """Stub for the safety writer service (BEAN-030)."""
    logger.info("Write safety stage: stub (BEAN-030 not yet implemented)")
    return StageResult()


def _stub_diff_report(spec: CompositionSpec, output_dir: Path) -> StageResult:
    """Stub for the diff reporter service (BEAN-031)."""
    logger.info("Diff report stage: stub (BEAN-031 not yet implemented)")
    return StageResult()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_library_version(library_root: Path) -> str:
    """Get the git short-hash of the library directory, or empty string on failure."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(library_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        pass
    return ""


def _make_run_id() -> str:
    """Generate a unique run identifier from current timestamp."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _compare_trees(source: Path, target: Path) -> OverlayPlan:
    """Compare a freshly-generated tree against an existing target directory.

    Returns an OverlayPlan describing what actions would be taken.
    """
    actions: list[FileAction] = []

    # Walk the source tree to find creates and updates
    for src_file in sorted(source.rglob("*")):
        if src_file.is_dir():
            continue
        rel = str(src_file.relative_to(source))
        tgt_file = target / rel

        if not tgt_file.exists():
            actions.append(FileAction(
                path=rel,
                action=FileActionType.CREATE,
                reason="New file not present in target",
            ))
        else:
            src_content = src_file.read_bytes()
            tgt_content = tgt_file.read_bytes()
            if src_content != tgt_content:
                actions.append(FileAction(
                    path=rel,
                    action=FileActionType.UPDATE,
                    reason="File content differs",
                ))
            else:
                actions.append(FileAction(
                    path=rel,
                    action=FileActionType.SKIP,
                    reason="File unchanged",
                ))

    # Walk the target tree to find deletes (files in target but not in source)
    if target.exists():
        for tgt_file in sorted(target.rglob("*")):
            if tgt_file.is_dir():
                continue
            rel = str(tgt_file.relative_to(target))
            src_file = source / rel
            if not src_file.exists():
                actions.append(FileAction(
                    path=rel,
                    action=FileActionType.DELETE,
                    reason="File exists in target but not in new generation",
                ))

    return OverlayPlan(actions=actions)


def _apply_overlay_plan(plan: OverlayPlan, source: Path, target: Path) -> StageResult:
    """Apply an overlay plan: copy creates/updates from source, delete removals in target."""
    wrote: list[str] = []
    warnings: list[str] = []

    for action in plan.actions:
        src_file = source / action.path
        tgt_file = target / action.path

        if action.action == FileActionType.CREATE:
            tgt_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(tgt_file))
            wrote.append(action.path)

        elif action.action == FileActionType.UPDATE:
            tgt_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(tgt_file))
            wrote.append(action.path)

        elif action.action == FileActionType.DELETE:
            if tgt_file.exists():
                tgt_file.unlink()
                wrote.append(action.path)
            else:
                warnings.append(f"File already removed: {action.path}")

        # SKIP actions require no work

    return StageResult(wrote=wrote, warnings=warnings)


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------


def _run_pipeline(
    spec: CompositionSpec,
    library: LibraryIndex,
    output_dir: Path,
) -> dict[str, StageResult]:
    """Execute all pipeline stages in order and return per-stage results."""
    stages: dict[str, StageResult] = {}

    # Stage 1: Scaffold
    stages["scaffold"] = scaffold_project(spec, output_dir)

    # Stage 2: Compile member prompts (stub)
    stages["compile"] = _stub_compile(spec, library, output_dir)

    # Stage 3: Copy assets (stub)
    stages["copy_assets"] = _stub_copy_assets(spec, library, output_dir)

    # Stage 4: Seed tasks (stub, only if enabled)
    if spec.generation.seed_tasks:
        stages["seed_tasks"] = _stub_seed_tasks(spec, output_dir)

    # Stage 5: Write safety config (stub)
    stages["safety"] = _stub_write_safety(spec, output_dir)

    # Stage 6: Diff report (stub, only if enabled)
    if spec.generation.write_diff_report:
        stages["diff_report"] = _stub_diff_report(spec, output_dir)

    return stages


def generate_project(
    composition: CompositionSpec,
    library_root: str | Path,
    output_root: str | Path | None = None,
    strictness: Strictness = Strictness.STANDARD,
    overlay: bool = False,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[GenerationManifest, ValidationResult, OverlayPlan | None]:
    """Orchestrate the full project generation pipeline.

    Args:
        composition: The composition spec describing what to generate.
        library_root: Path to the ai-team-library directory.
        output_root: Where to write the generated project. If None, uses
            the spec's project.output_root / project.resolved_output_folder.
        strictness: Validation strictness level.
        overlay: If True, use two-phase overlay mode for re-generation.
        dry_run: If True (and overlay=True), compute the overlay plan but
            don't apply it. Ignored when overlay=False.
        force: If True, proceed even when validation produces errors.

    Returns:
        A tuple of:
        - GenerationManifest: complete record of the generation run
        - ValidationResult: pre-generation validation findings
        - OverlayPlan | None: overlay plan (only when overlay=True)
    """
    library_path = Path(library_root)

    # Resolve output directory
    if output_root is not None:
        output_dir = Path(output_root)
    else:
        output_dir = (
            Path(composition.project.output_root)
            / composition.project.resolved_output_folder
        )

    # Step 1: Index the library
    library = build_library_index(library_path)

    # Step 2: Validate
    validation = run_pre_generation_validation(composition, library, strictness)

    # Build base manifest
    run_id = _make_run_id()
    lib_version = _get_library_version(library_path)
    manifest = GenerationManifest(
        run_id=run_id,
        library_version=lib_version,
        composition_snapshot=composition.model_dump(mode="json"),
    )

    # Check validation result
    if not validation.is_valid and not force:
        logger.warning(
            "Validation failed with %d errors — generation aborted",
            len(validation.errors),
        )
        return manifest, validation, None

    # Step 3: Run the pipeline
    overlay_plan: OverlayPlan | None = None

    if overlay:
        # Two-phase overlay mode
        with tempfile.TemporaryDirectory(prefix="foundry-gen-") as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Phase 1: Generate into temp directory
            stages = _run_pipeline(composition, library, tmp_path)
            manifest.stages = stages

            # Phase 2: Compare against target
            overlay_plan = _compare_trees(tmp_path, output_dir)
            overlay_plan.dry_run = dry_run

            if not dry_run:
                # Phase 3: Apply the overlay plan
                apply_result = _apply_overlay_plan(overlay_plan, tmp_path, output_dir)
                manifest.stages["overlay_apply"] = apply_result

        logger.info(
            "Overlay generation complete: %d creates, %d updates, %d deletes, %d skips",
            len(overlay_plan.creates),
            len(overlay_plan.updates),
            len(overlay_plan.deletes),
            len(overlay_plan.skips),
        )
    else:
        # Standard mode: write directly to output
        stages = _run_pipeline(composition, library, output_dir)
        manifest.stages = stages

    # Write manifest file if enabled
    if composition.generation.write_manifest and not dry_run:
        _write_manifest_file(manifest, output_dir)

    logger.info(
        "Generation complete: run_id=%s, files_written=%d, warnings=%d",
        manifest.run_id,
        manifest.total_files_written,
        len(manifest.all_warnings),
    )

    return manifest, validation, overlay_plan


def _write_manifest_file(manifest: GenerationManifest, output_dir: Path) -> None:
    """Write the manifest JSON file to the output directory."""
    from foundry_app.io.composition_io import save_manifest

    manifest_path = Path(output_dir) / "manifest.json"
    try:
        save_manifest(manifest, manifest_path)
        logger.info("Wrote manifest: %s", manifest_path)
    except OSError as exc:
        logger.warning("Failed to write manifest: %s", exc)
