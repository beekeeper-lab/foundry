"""Asset copier service — copies library assets into a generated project."""

from __future__ import annotations

import filecmp
import logging
import shutil
from pathlib import Path

from foundry_app.core.models import CompositionSpec, LibraryIndex, StageResult

logger = logging.getLogger(__name__)

# Library subdirectories that are always copied (source_subdir, dest_subdir)
_GLOBAL_ASSET_DIRS = [
    ("claude/commands", ".claude/commands"),
    ("claude/hooks", ".claude/hooks"),
]


def copy_assets(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
) -> StageResult:
    """Copy library assets (templates, commands, hooks) into a generated project.

    Copies three categories of assets:
    1. **Persona templates** — per-persona, only when ``include_templates=True``
    2. **Commands** — from ``library/claude/commands/`` to ``.claude/commands/``
    3. **Hooks** — from ``library/claude/hooks/`` to ``.claude/hooks/``

    Overlay-safe: existing identical files are skipped; conflicts produce warnings.

    Args:
        spec: The composition spec describing the project.
        library_index: Index of library contents (from library indexer).
        library_root: Absolute path to the library root directory.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing all files copied and any warnings.
    """
    lib_root = Path(library_root)
    out_root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    # --- Persona templates ---
    _copy_persona_templates(spec, library_index, lib_root, out_root, wrote, warnings)

    # --- Global assets (commands, hooks) ---
    for src_subdir, dest_subdir in _GLOBAL_ASSET_DIRS:
        _copy_directory_files(
            lib_root / src_subdir,
            out_root / dest_subdir,
            out_root,
            wrote,
            warnings,
        )

    logger.info(
        "Asset copy complete: %d files copied, %d warnings",
        len(wrote),
        len(warnings),
    )

    return StageResult(wrote=wrote, warnings=warnings)


def _copy_persona_templates(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    lib_root: Path,
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy persona template files for each persona with include_templates=True."""
    for persona in spec.team.personas:
        if not persona.include_templates:
            logger.debug(
                "Skipping templates for persona '%s' (include_templates=False)",
                persona.id,
            )
            continue

        persona_info = library_index.persona_by_id(persona.id)
        if persona_info is None:
            warnings.append(f"Persona '{persona.id}' not found in library index")
            continue

        src_dir = lib_root / "personas" / persona.id / "templates"
        dest_dir = out_root / "ai" / "outputs" / persona.id

        if not src_dir.is_dir():
            warnings.append(f"No templates directory for persona '{persona.id}'")
            continue

        if not persona_info.templates:
            warnings.append(f"Persona '{persona.id}' has no template files")
            continue

        _copy_directory_files(src_dir, dest_dir, out_root, wrote, warnings)


def _copy_directory_files(
    src_dir: Path,
    dest_dir: Path,
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy all files from src_dir to dest_dir, overlay-safe."""
    if not src_dir.is_dir():
        logger.debug("Source directory does not exist, skipping: %s", src_dir)
        return

    dest_dir.mkdir(parents=True, exist_ok=True)

    for src_file in sorted(src_dir.iterdir()):
        if src_file.is_symlink():
            warnings.append(f"Skipping symlink: {src_file.name}")
            continue
        if not src_file.is_file():
            continue

        dest_file = dest_dir / src_file.name
        rel_path = str(dest_file.relative_to(out_root))

        if dest_file.exists():
            if filecmp.cmp(str(src_file), str(dest_file), shallow=False):
                logger.debug("File already exists (identical), skipping: %s", rel_path)
            else:
                warnings.append(f"File already exists with different content: {rel_path}")
                logger.warning("File conflict, skipping: %s", rel_path)
            continue

        shutil.copy2(src_file, dest_file)
        wrote.append(rel_path)
        logger.info("Copied asset: %s", rel_path)
