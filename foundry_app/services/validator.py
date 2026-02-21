"""Pre-generation validator — checks a CompositionSpec against a LibraryIndex."""

from __future__ import annotations

import logging

from foundry_app.core.models import (
    CompositionSpec,
    LibraryIndex,
    Severity,
    Strictness,
    ValidationMessage,
    ValidationResult,
)

logger = logging.getLogger(__name__)


def _check_personas(
    composition: CompositionSpec,
    library_index: LibraryIndex,
    messages: list[ValidationMessage],
) -> None:
    """Validate that all referenced personas exist in the library."""
    for ps in composition.team.personas:
        persona = library_index.persona_by_id(ps.id)
        if persona is None:
            messages.append(ValidationMessage(
                severity=Severity.ERROR,
                code="missing-persona",
                message=f"Persona '{ps.id}' not found in library",
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
