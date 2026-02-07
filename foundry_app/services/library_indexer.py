"""Library indexer — scans an ai-team-library directory and builds a LibraryIndex."""

from __future__ import annotations

import logging
from pathlib import Path

from foundry_app.core.models import (
    HookPackInfo,
    LibraryIndex,
    PersonaInfo,
    StackInfo,
)

logger = logging.getLogger(__name__)


def _scan_personas(personas_dir: Path) -> list[PersonaInfo]:
    """Scan the personas/ directory and return PersonaInfo for each subdirectory."""
    if not personas_dir.is_dir():
        logger.warning("Personas directory not found: %s", personas_dir)
        return []

    personas: list[PersonaInfo] = []
    for entry in sorted(personas_dir.iterdir()):
        if not entry.is_dir():
            continue

        templates: list[str] = []
        templates_dir = entry / "templates"
        if templates_dir.is_dir():
            templates = sorted(
                f.name for f in templates_dir.iterdir() if f.is_file()
            )

        personas.append(
            PersonaInfo(
                id=entry.name,
                path=str(entry),
                has_persona_md=(entry / "persona.md").is_file(),
                has_outputs_md=(entry / "outputs.md").is_file(),
                has_prompts_md=(entry / "prompts.md").is_file(),
                templates=templates,
            )
        )

    return personas


def _scan_stacks(stacks_dir: Path) -> list[StackInfo]:
    """Scan the stacks/ directory and return StackInfo for each subdirectory."""
    if not stacks_dir.is_dir():
        logger.warning("Stacks directory not found: %s", stacks_dir)
        return []

    stacks: list[StackInfo] = []
    for entry in sorted(stacks_dir.iterdir()):
        if not entry.is_dir():
            continue

        files = sorted(f.name for f in entry.iterdir() if f.is_file())
        stacks.append(
            StackInfo(
                id=entry.name,
                path=str(entry),
                files=files,
            )
        )

    return stacks


def _scan_hook_packs(hooks_dir: Path) -> list[HookPackInfo]:
    """Scan the claude/hooks/ directory and return HookPackInfo for each .md file."""
    if not hooks_dir.is_dir():
        logger.warning("Hooks directory not found: %s", hooks_dir)
        return []

    packs: list[HookPackInfo] = []
    for entry in sorted(hooks_dir.iterdir()):
        if not entry.is_file() or entry.suffix != ".md":
            continue

        packs.append(
            HookPackInfo(
                id=entry.stem,
                path=str(entry),
                files=[entry.name],
            )
        )

    return packs


def build_library_index(library_root: str | Path) -> LibraryIndex:
    """Scan a library directory and return a structured LibraryIndex.

    Args:
        library_root: Path to the root of an ai-team-library directory.

    Returns:
        A LibraryIndex containing all discovered personas, stacks, and hook packs.
    """
    root = Path(library_root).resolve()
    if not root.is_dir():
        logger.warning("Library root does not exist: %s", root)
        return LibraryIndex(library_root=str(root))

    personas = _scan_personas(root / "personas")
    stacks = _scan_stacks(root / "stacks")
    hook_packs = _scan_hook_packs(root / "claude" / "hooks")

    logger.info(
        "Indexed library: %d personas, %d stacks, %d hook packs",
        len(personas),
        len(stacks),
        len(hook_packs),
    )

    return LibraryIndex(
        library_root=str(root),
        personas=personas,
        stacks=stacks,
        hook_packs=hook_packs,
    )
