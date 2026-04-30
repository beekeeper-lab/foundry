"""Library indexer — scans an ai-team-library directory and builds a LibraryIndex."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from foundry_app.core.models import (
    ArtifactTypeInfo,
    ExpertiseInfo,
    HookPackInfo,
    LibraryIndex,
    PersonaInfo,
)

logger = logging.getLogger(__name__)

# Artifact-type registry fields (kebab-case in YAML, snake_case on the model).
_REGISTRY_REQUIRED_FIELDS = ("name", "description", "format", "required-fields")


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


def _load_artifact_type_registry(contracts_dir: Path) -> list[ArtifactTypeInfo]:
    """Load and parse ``contracts/artifact-types.yml``.

    Returns an empty list (with a logger.warning) if the file is missing,
    malformed, or has no ``types:`` key. Per ADR-013, every name referenced
    by a persona's ``contracts.yml`` must resolve to an entry returned here.

    Each entry must have ``name``, ``description``, ``format``, and
    ``required-fields`` keys; ``template-path`` is optional and may be null.
    A missing required key on an entry raises ``ValueError`` naming the
    offending entry so the failure is actionable.
    """
    registry_file = contracts_dir / "artifact-types.yml"
    if not registry_file.is_file():
        logger.warning(
            "Artifact-type registry not found: %s — contracts emission will be empty",
            registry_file,
        )
        return []

    try:
        data = yaml.safe_load(registry_file.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        logger.warning("Artifact-type registry is malformed YAML: %s — %s", registry_file, exc)
        return []
    except OSError as exc:
        logger.warning("Cannot read artifact-type registry: %s — %s", registry_file, exc)
        return []

    if not isinstance(data, dict) or "types" not in data:
        logger.warning(
            "Artifact-type registry has no 'types:' key: %s",
            registry_file,
        )
        return []

    raw_types = data.get("types") or []
    if not isinstance(raw_types, list):
        logger.warning(
            "Artifact-type registry 'types:' is not a list: %s",
            registry_file,
        )
        return []

    artifact_types: list[ArtifactTypeInfo] = []
    for idx, entry in enumerate(raw_types):
        if not isinstance(entry, dict):
            raise ValueError(
                f"Artifact-type registry entry #{idx} in {registry_file} "
                f"is not a mapping: {entry!r}"
            )
        for required in _REGISTRY_REQUIRED_FIELDS:
            if required not in entry:
                name_for_msg = entry.get("name", f"<entry #{idx}>")
                raise ValueError(
                    f"Artifact-type registry entry '{name_for_msg}' in "
                    f"{registry_file} is missing required field "
                    f"'{required}'"
                )
        required_fields = entry.get("required-fields") or []
        if not isinstance(required_fields, list):
            raise ValueError(
                f"Artifact-type registry entry '{entry.get('name')}' in "
                f"{registry_file} has non-list 'required-fields'"
            )
        artifact_types.append(
            ArtifactTypeInfo(
                name=str(entry["name"]),
                description=str(entry.get("description") or ""),
                format=str(entry.get("format") or "markdown"),
                required_fields=[str(f) for f in required_fields],
                template_path=(
                    str(entry["template-path"])
                    if entry.get("template-path") is not None
                    else None
                ),
            )
        )
    return artifact_types


def _load_persona_contracts(
    persona_dir: Path,
    known_artifact_names: set[str],
) -> tuple[list[str], list[str]]:
    """Read ``<persona_dir>/contracts.yml`` and return (produces, consumes).

    Validates each name against ``known_artifact_names`` and drops unknown
    names with a logger.warning ("Artifact type '<name>' not found in
    registry (referenced by persona '<id>' contracts.yml)"). Duplicates
    within a list are deduped silently while preserving first-seen order.

    Returns ``([], [])`` if the file is missing or malformed.
    """
    contracts_file = persona_dir / "contracts.yml"
    if not contracts_file.is_file():
        return [], []

    try:
        data = yaml.safe_load(contracts_file.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        logger.warning(
            "Persona contracts.yml is malformed YAML: %s — %s",
            contracts_file,
            exc,
        )
        return [], []
    except OSError as exc:
        logger.warning(
            "Cannot read persona contracts.yml: %s — %s", contracts_file, exc,
        )
        return [], []

    if not isinstance(data, dict):
        logger.warning(
            "Persona contracts.yml is not a mapping: %s", contracts_file,
        )
        return [], []

    persona_id = persona_dir.name

    def _clean(key: str) -> list[str]:
        raw = data.get(key) or []
        if not isinstance(raw, list):
            logger.warning(
                "Persona '%s' contracts.yml '%s:' is not a list",
                persona_id,
                key,
            )
            return []
        seen: set[str] = set()
        out: list[str] = []
        for item in raw:
            name = str(item).strip()
            if not name or name in seen:
                continue
            if name not in known_artifact_names:
                logger.warning(
                    "Artifact type '%s' not found in registry "
                    "(referenced by persona '%s' contracts.yml)",
                    name,
                    persona_id,
                )
                continue
            seen.add(name)
            out.append(name)
        return out

    return _clean("produces"), _clean("consumes")


def _log_dangling_producers(personas: list[PersonaInfo]) -> None:
    """Emit INFO log entries for produced artifact types with no consumer.

    Per ADR-013: ``dev-decision`` and similar types are legal but warned —
    we surface them as INFO (not WARNING) so reviewers can see them in CI
    output without failing the build. ``handoff-packet`` is excluded from
    this check because it is universally produced and consumed implicitly
    by team-lead at handoff time.
    """
    consumed: set[str] = set()
    for persona in personas:
        consumed.update(persona.consumes)

    for persona in personas:
        for name in persona.produces:
            if name == "handoff-packet":
                continue
            if name not in consumed:
                logger.info(
                    "Dangling producer: artifact type '%s' is produced by "
                    "persona '%s' but no persona consumes it",
                    name,
                    persona.id,
                )


def _scan_personas(
    personas_dir: Path,
    known_artifact_names: set[str],
) -> list[PersonaInfo]:
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
        produces, consumes = _load_persona_contracts(entry, known_artifact_names)
        personas.append(
            PersonaInfo(
                id=entry.name,
                path=str(entry),
                has_persona_md=persona_md.is_file(),
                has_outputs_md=(entry / "outputs.md").is_file(),
                has_prompts_md=(entry / "prompts.md").is_file(),
                templates=templates,
                category=_parse_persona_category(persona_md),
                produces=produces,
                consumes=consumes,
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

    artifact_types = _load_artifact_type_registry(root / "contracts")
    known_artifact_names = {a.name for a in artifact_types}

    personas = _scan_personas(root / "personas", known_artifact_names)
    expertise = _scan_expertise(root / "expertise")
    expertise = _validate_expertise_applies_to(
        expertise, {p.id for p in personas},
    )
    hook_packs = _scan_hook_packs(root / "claude" / "hooks")

    # Dangling-producer pass — INFO log per ADR-013 ambiguity resolution.
    _log_dangling_producers(personas)

    logger.info(
        "Indexed library: %d personas, %d expertise, %d hook packs, %d artifact types",
        len(personas),
        len(expertise),
        len(hook_packs),
        len(artifact_types),
    )

    return LibraryIndex(
        library_root=str(root),
        personas=personas,
        expertise=expertise,
        hook_packs=hook_packs,
        artifact_types=artifact_types,
    )
