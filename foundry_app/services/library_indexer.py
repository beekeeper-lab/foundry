"""Library indexer — scans an ai-team-library directory and builds a LibraryIndex."""

from __future__ import annotations

import logging
from pathlib import Path

from foundry_app.core.models import (
    ExpertiseInfo,
    HookPackInfo,
    LibraryIndex,
    PersonaInfo,
)

logger = logging.getLogger(__name__)


def _parse_persona_category(path: Path) -> str:
    """Extract the category from a persona markdown file.

    Looks for a ``## Category`` heading followed by the category value on the next line.
    Returns empty string if not found.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for i, line in enumerate(lines):
        if line.strip().lower() == "## category" and i + 1 < len(lines):
            cat = lines[i + 1].strip()
            if cat:
                return cat
    return ""


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

        persona_md = entry / "persona.md"
        personas.append(
            PersonaInfo(
                id=entry.name,
                path=str(entry),
                has_persona_md=persona_md.is_file(),
                has_outputs_md=(entry / "outputs.md").is_file(),
                has_prompts_md=(entry / "prompts.md").is_file(),
                templates=templates,
                category=_parse_persona_category(persona_md),
            )
        )

    return personas


def _scan_expertise(expertise_dir: Path) -> list[ExpertiseInfo]:
    """Scan the expertise/ directory and return ExpertiseInfo for each subdirectory."""
    if not expertise_dir.is_dir():
        logger.warning("Expertise directory not found: %s", expertise_dir)
        return []

    items: list[ExpertiseInfo] = []
    for entry in sorted(expertise_dir.iterdir()):
        if not entry.is_dir():
            continue

        files = sorted(f.name for f in entry.iterdir() if f.is_file())
        items.append(
            ExpertiseInfo(
                id=entry.name,
                path=str(entry),
                files=files,
            )
        )

    return items


def _parse_hook_category(path: Path) -> str:
    """Extract the category from a hook pack markdown file.

    Looks for a ``## Category`` heading followed by the category value on the next line.
    Returns empty string if not found.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for i, line in enumerate(lines):
        if line.strip().lower() == "## category" and i + 1 < len(lines):
            cat = lines[i + 1].strip()
            if cat:
                return cat
    return ""


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
                category=_parse_hook_category(entry),
            )
        )

    return packs


def build_library_index(library_root: str | Path) -> LibraryIndex:
    """Scan a library directory and return a structured LibraryIndex.

    Args:
        library_root: Path to the root of an ai-team-library directory.

    Returns:
        A LibraryIndex containing all discovered personas, expertise, and hook packs.
    """
    root = Path(library_root).resolve()
    if not root.is_dir():
        logger.warning("Library root does not exist: %s", root)
        return LibraryIndex(library_root=str(root))

    personas = _scan_personas(root / "personas")
    expertise = _scan_expertise(root / "expertise")
    hook_packs = _scan_hook_packs(root / "claude" / "hooks")

    logger.info(
        "Indexed library: %d personas, %d expertise, %d hook packs",
        len(personas),
        len(expertise),
        len(hook_packs),
    )

    return LibraryIndex(
        library_root=str(root),
        personas=personas,
        expertise=expertise,
        hook_packs=hook_packs,
    )
