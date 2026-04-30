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


def _parse_expertise_category(expertise_dir: Path) -> str:
    """Extract the category from an expertise directory's primary markdown file.

    Checks ``conventions.md`` first, then falls back to the first ``.md`` file
    alphabetically.  Looks for a ``## Category`` heading followed by the category
    value on the next line.  Returns empty string if not found.
    """
    target = expertise_dir / "conventions.md"
    if not target.is_file():
        md_files = sorted(f for f in expertise_dir.iterdir() if f.suffix == ".md")
        if not md_files:
            return ""
        target = md_files[0]
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for i, line in enumerate(lines):
        if line.strip().lower() == "## category" and i + 1 < len(lines):
            cat = lines[i + 1].strip()
            if cat:
                return cat
    return ""


def _parse_expertise_applies_to(expertise_dir: Path) -> list[str]:
    """Extract persona IDs from an expertise's ``## Applies To`` section.

    Mirrors ``_parse_hook_conflicts``: scans the primary markdown file
    (``conventions.md`` or the alphabetically-first ``*.md`` for multi-file
    packs) for an ``## Applies To`` heading followed by a bulleted list. Each
    bullet line's first token (stripped of surrounding backticks) is taken as
    a persona id.

    Returns an empty list if the section is missing, present-but-empty, or the
    file is unreadable. Per ADR-012, an empty list signals "applies to every
    persona" — that interpretation lives in
    ``compiler._expertise_applies_to``, not here.
    """
    target = expertise_dir / "conventions.md"
    if not target.is_file():
        md_files = sorted(f for f in expertise_dir.iterdir() if f.suffix == ".md")
        if not md_files:
            return []
        target = md_files[0]
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    ids: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## "):
            if in_section:
                # Hit the next heading — stop collecting.
                break
            in_section = stripped.lower() == "## applies to"
            continue
        if not in_section:
            continue
        # Markdown horizontal rules (``---``, ``----``, etc.) start with ``-``
        # but aren't list items. Skip lines that are all dashes/asterisks.
        if stripped and set(stripped) <= {"-", "*", " "}:
            continue
        if stripped.startswith(("-", "*")):
            body = stripped[1:].strip()
            # Strip optional surrounding backticks: `- developer` or `- `developer``
            if body.startswith("`"):
                end = body.find("`", 1)
                if end > 1:
                    body = body[1:end]
            else:
                # Take first whitespace-delimited token so trailing prose
                # (`- developer — implementation`) doesn't bleed into the id.
                body = body.split()[0] if body.split() else ""
            persona_id = body.strip()
            if persona_id and persona_id not in ids:
                ids.append(persona_id)
    return ids


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
                category=_parse_expertise_category(entry),
                applies_to=_parse_expertise_applies_to(entry),
            )
        )

    return items


def _validate_expertise_applies_to(
    expertise: list[ExpertiseInfo],
    known_persona_ids: set[str],
) -> list[ExpertiseInfo]:
    """Drop unknown persona IDs from each expertise's ``applies_to`` list.

    Per ADR-012: unknown persona IDs are dropped with a warning at index time
    (mirrors the ``Persona '<id>' not found`` warning shape used by the
    compiler). Returns a new list of ExpertiseInfo with cleaned applies_to.
    """
    cleaned: list[ExpertiseInfo] = []
    for info in expertise:
        if not info.applies_to:
            cleaned.append(info)
            continue
        valid: list[str] = []
        for pid in info.applies_to:
            if pid in known_persona_ids:
                valid.append(pid)
            else:
                logger.warning(
                    "Persona '%s' not found in library index "
                    "(referenced by expertise '%s' applies_to)",
                    pid,
                    info.id,
                )
        cleaned.append(info.model_copy(update={"applies_to": valid}))
    return cleaned


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


def _parse_hook_conflicts(path: Path) -> list[str]:
    """Extract conflicting pack ids from a ``## Conflicts With`` section.

    Each bullet line's first backticked token is taken as a pack id, e.g.:
    ``- `az-limited-ops` — the read-only guard ...`` → ``az-limited-ops``.
    Returns an empty list if the section is missing or malformed.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    ids: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## "):
            in_section = stripped.lower() == "## conflicts with"
            continue
        if not in_section:
            continue
        if stripped.startswith(("-", "*")):
            body = stripped[1:].strip()
            if body.startswith("`"):
                end = body.find("`", 1)
                if end > 1:
                    pack_id = body[1:end].strip()
                    if pack_id and pack_id not in ids:
                        ids.append(pack_id)
    return ids


def _parse_hook_posture_compatibility(path: Path) -> dict[str, dict[str, str]]:
    """Extract the ``## Posture Compatibility`` table as structured metadata.

    Returns a dict keyed by lower-cased posture name. Each value is a dict
    with ``included`` (raw value as-written, e.g. ``Yes``, ``No``,
    ``Optional``, ``Yes (when ...)``) and ``default_mode`` (e.g.
    ``enforcing``, ``advisory``, ``—``). Rows whose posture cell is wrapped
    in backticks (``` `baseline` ```) are accepted. Returns an empty dict if
    the section or a well-formed table is missing.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}

    result: dict[str, dict[str, str]] = {}
    in_section = False
    header_seen = False
    separator_seen = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## "):
            if in_section:
                break
            in_section = stripped.lower() == "## posture compatibility"
            header_seen = False
            separator_seen = False
            continue
        if not in_section or not stripped:
            continue
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not header_seen:
            header_seen = True
            continue
        if not separator_seen:
            # separator row like |---|---|---|
            if all(set(c) <= {"-", ":"} for c in cells if c):
                separator_seen = True
            continue
        if len(cells) < 3:
            continue
        posture = cells[0].strip("`").strip().lower()
        if not posture:
            continue
        result[posture] = {
            "included": cells[1].strip(),
            "default_mode": cells[2].strip(),
        }
    return result


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
                conflicts_with=_parse_hook_conflicts(entry),
                posture_compatibility=_parse_hook_posture_compatibility(entry),
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
    expertise = _validate_expertise_applies_to(
        expertise, {p.id for p in personas},
    )
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
