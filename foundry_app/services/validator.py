"""Pre-generation validator — checks a CompositionSpec against a LibraryIndex."""

from __future__ import annotations

import logging

from foundry_app.core.models import (
    CompositionSpec,
    HookMode,
    LibraryIndex,
    Severity,
    Strictness,
    ValidationMessage,
    ValidationResult,
)
from foundry_app.services.library_indexer import format_unknown_persona_error

logger = logging.getLogger(__name__)


def _check_personas(
    composition: CompositionSpec,
    library_index: LibraryIndex,
    messages: list[ValidationMessage],
) -> None:
    """Validate that all referenced personas exist in the library.

    Per ADR-014, an unknown persona id (or a wrong-tier reference such as
    a bare extended-persona id) produces an ERROR with the canonical
    message text from ``format_unknown_persona_error``.
    """
    for ps in composition.team.personas:
        persona = library_index.persona_by_id(ps.id)
        if persona is None:
            messages.append(ValidationMessage(
                severity=Severity.ERROR,
                code="missing-persona",
                message=format_unknown_persona_error(ps.id, library_index),
            ))
        elif not persona.has_persona_md:
            messages.append(ValidationMessage(
                severity=Severity.WARNING,
                code="persona-no-persona-md",
                message=f"Persona '{ps.id}' has no persona.md file",
            ))


def _check_expertise(
    composition: CompositionSpec,
    library_index: LibraryIndex,
    messages: list[ValidationMessage],
) -> None:
    """Validate that all referenced expertise exist in the library."""
    for ss in composition.expertise:
        expertise = library_index.expertise_by_id(ss.id)
        if expertise is None:
            messages.append(ValidationMessage(
                severity=Severity.ERROR,
                code="missing-expertise",
                message=f"Expertise '{ss.id}' not found in library",
            ))
        elif not expertise.files:
            messages.append(ValidationMessage(
                severity=Severity.WARNING,
                code="expertise-no-files",
                message=f"Expertise '{ss.id}' has no convention files",
            ))


def _check_hook_packs(
    composition: CompositionSpec,
    library_index: LibraryIndex,
    messages: list[ValidationMessage],
) -> None:
    """Validate that all referenced hook packs exist in the library."""
    for hp in composition.hooks.packs:
        pack = library_index.hook_pack_by_id(hp.id)
        if pack is None:
            messages.append(ValidationMessage(
                severity=Severity.ERROR,
                code="missing-hook-pack",
                message=f"Hook pack '{hp.id}' not found in library",
            ))


def _check_hook_conflicts(
    composition: CompositionSpec,
    library_index: LibraryIndex,
    messages: list[ValidationMessage],
) -> None:
    """Validate that no pair of selected hook packs declare a mutual conflict.

    A conflict is detected when either side of a pair lists the other under
    its ``conflicts_with`` metadata. Declarations are expected to be symmetric,
    but one-sided declarations are treated as binding to guard against drift.
    Only enabled, non-disabled packs (as the writer would emit) are checked —
    a conflict between a disabled pack and an active one is not surfaced.
    """
    active_ids = [
        hp.id for hp in composition.hooks.packs
        if hp.enabled and hp.mode != HookMode.DISABLED
    ]
    if len(active_ids) < 2:
        return

    reported: set[tuple[str, str]] = set()
    for i, left_id in enumerate(active_ids):
        left_pack = library_index.hook_pack_by_id(left_id)
        for right_id in active_ids[i + 1:]:
            right_pack = library_index.hook_pack_by_id(right_id)
            left_conflicts = set(left_pack.conflicts_with) if left_pack else set()
            right_conflicts = set(right_pack.conflicts_with) if right_pack else set()
            if right_id in left_conflicts or left_id in right_conflicts:
                pair = tuple(sorted((left_id, right_id)))
                if pair in reported:
                    continue
                reported.add(pair)
                messages.append(ValidationMessage(
                    severity=Severity.ERROR,
                    code="hook-pack-conflict",
                    message=(
                        f"Hook packs '{pair[0]}' and '{pair[1]}' are mutually "
                        f"exclusive and cannot both be enabled in the same "
                        f"composition. Remove one of them."
                    ),
                ))


def _check_hook_posture_compatibility(
    composition: CompositionSpec,
    library_index: LibraryIndex,
    messages: list[ValidationMessage],
) -> None:
    """Validate that each active hook pack supports the composition's posture.

    Consults ``HookPackInfo.posture_compatibility`` (parsed from the pack's
    ``## Posture Compatibility`` table). A pack whose row for the selected
    posture has ``included == "No"`` is considered incompatible and surfaces
    an error. Packs whose metadata is missing (older libraries) are skipped
    so the check is backward compatible.
    """
    posture_key = composition.hooks.posture.value.lower()
    for hp in composition.hooks.packs:
        if not hp.enabled or hp.mode == HookMode.DISABLED:
            continue
        pack = library_index.hook_pack_by_id(hp.id)
        if pack is None or not pack.posture_compatibility:
            continue
        row = pack.posture_compatibility.get(posture_key)
        if row is None:
            continue
        if row.get("included", "").strip().lower() == "no":
            messages.append(ValidationMessage(
                severity=Severity.ERROR,
                code="hook-pack-posture-incompatible",
                message=(
                    f"Hook pack '{hp.id}' declares posture '{posture_key}' as "
                    f"incompatible (Posture Compatibility table says "
                    f"Included: No). Remove the pack, lower enforcement, or "
                    f"raise the composition's posture."
                ),
            ))


def _check_required_fields(
    composition: CompositionSpec,
    messages: list[ValidationMessage],
) -> None:
    """Validate required fields beyond Pydantic's own checks."""
    if not composition.team.personas:
        messages.append(ValidationMessage(
            severity=Severity.WARNING,
            code="no-personas",
            message="No personas selected — the generated project will have no team",
        ))

    if not composition.expertise:
        messages.append(ValidationMessage(
            severity=Severity.INFO,
            code="no-expertise",
            message="No expertise selected — no convention files will be included",
        ))


def _check_duplicates(
    composition: CompositionSpec,
    messages: list[ValidationMessage],
) -> None:
    """Check for duplicate references."""
    persona_ids = [ps.id for ps in composition.team.personas]
    seen_personas: set[str] = set()
    for pid in persona_ids:
        if pid in seen_personas:
            messages.append(ValidationMessage(
                severity=Severity.WARNING,
                code="duplicate-persona",
                message=f"Persona '{pid}' is selected more than once",
            ))
        seen_personas.add(pid)

    expertise_ids = [ss.id for ss in composition.expertise]
    seen_expertise: set[str] = set()
    for sid in expertise_ids:
        if sid in seen_expertise:
            messages.append(ValidationMessage(
                severity=Severity.WARNING,
                code="duplicate-expertise",
                message=f"Expertise '{sid}' is selected more than once",
            ))
        seen_expertise.add(sid)


def _apply_strictness(
    messages: list[ValidationMessage],
    strictness: Strictness,
) -> list[ValidationMessage]:
    """Apply strictness policy to the message list.

    - light: only errors are kept; warnings become info
    - standard: errors and warnings kept as-is
    - strict: warnings are promoted to errors
    """
    if strictness == Strictness.STANDARD:
        return messages

    adjusted: list[ValidationMessage] = []
    for msg in messages:
        if strictness == Strictness.LIGHT:
            if msg.severity == Severity.WARNING:
                adjusted.append(msg.model_copy(update={"severity": Severity.INFO}))
            else:
                adjusted.append(msg)
        elif strictness == Strictness.STRICT:
            if msg.severity == Severity.WARNING:
                adjusted.append(msg.model_copy(update={"severity": Severity.ERROR}))
            else:
                adjusted.append(msg)
    return adjusted


def run_pre_generation_validation(
    composition: CompositionSpec,
    library_index: LibraryIndex,
    strictness: Strictness = Strictness.STANDARD,
) -> ValidationResult:
    """Validate a composition spec against the library before generation.

    Args:
        composition: The composition spec to validate.
        library_index: The indexed library to validate against.
        strictness: How strictly to treat warnings.
            - light: warnings become info (never block)
            - standard: errors block, warnings are advisory
            - strict: warnings are promoted to errors (block on any issue)

    Returns:
        A ValidationResult with categorized messages.
    """
    messages: list[ValidationMessage] = []

    _check_required_fields(composition, messages)
    _check_personas(composition, library_index, messages)
    _check_expertise(composition, library_index, messages)
    _check_hook_packs(composition, library_index, messages)
    _check_hook_conflicts(composition, library_index, messages)
    _check_hook_posture_compatibility(composition, library_index, messages)
    _check_duplicates(composition, messages)

    messages = _apply_strictness(messages, strictness)

    result = ValidationResult(messages=messages)

    logger.info(
        "Validation complete: %d errors, %d warnings, %d info",
        len(result.errors),
        len(result.warnings),
        len(result.infos),
    )

    return result
