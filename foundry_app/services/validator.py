"""Pre-generation validator — checks a CompositionSpec against a LibraryIndex."""

from __future__ import annotations

import logging

from foundry_app.core.models import (
    CompositionSpec,
    HookMode,
    LibraryIndex,
    PersonaInfo,
    Severity,
    Strictness,
    ValidationMessage,
    ValidationResult,
)
from foundry_app.services.library_indexer import format_unknown_persona_error

logger = logging.getLogger(__name__)

# Artifact types intentionally excluded from contract-graph checks.
# ``handoff-packet`` is universally produced and implicitly consumed by
# Team Lead at handoff time (see ADR-013 ambiguity resolutions and
# ``library_indexer._log_dangling_producers``). Treat it as always
# satisfied so it does not generate noise on every team.
_CONTRACT_GRAPH_IGNORED_TYPES: frozenset[str] = frozenset({"handoff-packet"})


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


# ---------------------------------------------------------------------------
# Contract-graph validation (BEAN-274)
# ---------------------------------------------------------------------------


def validate_contract_graph(
    personas: list[PersonaInfo],
    registry: LibraryIndex,
) -> ValidationResult:
    """Validate the produces/consumes contract graph for a composed team.

    Per ADR-013, every persona declares ``produces`` and ``consumes`` lists
    of artifact-type names. This check verifies, for the given team:

    1. **Missing producer** (ERROR): every artifact type consumed by some
       team member is also produced by some team member. The error names
       the missing type, the team consumers, and any producer personas in
       the library so the user knows whom to add.

    2. **Orphan produces** (WARNING): an artifact type is produced by a
       team member but consumed by no team member. Emitted as a warning
       in both standard and overlay modes — it indicates a wasted output
       channel, not a broken pipeline. ``handoff-packet`` is excluded
       (universally produced; implicitly consumed by Team Lead).

    Args:
        personas: The selected team (members composing the project). May
            be empty — in which case the result is trivially valid.
        registry: The library index, used as the registry of all personas
            (and their declared produces) for "Producers in library"
            suggestions when an unsatisfied consume is found.

    Returns:
        A ``ValidationResult`` with ordered messages: missing-producer
        errors first (sorted by artifact type), then orphan-produces
        warnings (sorted by artifact type, then producer id).
    """
    messages: list[ValidationMessage] = []

    if not personas:
        return ValidationResult(messages=messages)

    # Build the produced/consumed maps for the team. Preserve the order of
    # first-appearance so the rendered persona lists are deterministic and
    # follow the team's persona order.
    team_producers: dict[str, list[str]] = {}
    team_consumers: dict[str, list[str]] = {}
    for persona in personas:
        for artifact in persona.produces:
            if artifact in _CONTRACT_GRAPH_IGNORED_TYPES:
                continue
            team_producers.setdefault(artifact, []).append(persona.id)
        for artifact in persona.consumes:
            if artifact in _CONTRACT_GRAPH_IGNORED_TYPES:
                continue
            team_consumers.setdefault(artifact, []).append(persona.id)

    # Library-wide producer index — used to suggest who to add when a
    # consume is unsatisfied by the current team.
    library_producers: dict[str, list[str]] = {}
    for persona in registry.personas:
        for artifact in persona.produces:
            if artifact in _CONTRACT_GRAPH_IGNORED_TYPES:
                continue
            library_producers.setdefault(artifact, []).append(persona.id)

    # Missing producers — consumed by the team, produced by nobody on the team.
    missing_types = sorted(
        artifact for artifact in team_consumers
        if artifact not in team_producers
    )
    for artifact in missing_types:
        consumers = team_consumers[artifact]
        lib_producers = sorted(set(library_producers.get(artifact, [])))
        producer_list = ", ".join(lib_producers) if lib_producers else "none"
        consumer_list = ", ".join(consumers)
        messages.append(ValidationMessage(
            severity=Severity.ERROR,
            code="missing-producer",
            message=(
                f"Missing producer for type '{artifact}'. "
                f"Consumed by: {consumer_list}. "
                f"Producers in library: {producer_list}. "
                f"Add one to your team."
            ),
        ))

    # Orphan produces — produced by the team, consumed by nobody on the team.
    orphan_pairs: list[tuple[str, str]] = []
    for artifact in sorted(team_producers):
        if artifact in team_consumers:
            continue
        for producer_id in team_producers[artifact]:
            orphan_pairs.append((artifact, producer_id))
    # Stable sort: by artifact (already sorted) then by producer id
    orphan_pairs.sort(key=lambda pair: (pair[0], pair[1]))
    for artifact, producer_id in orphan_pairs:
        messages.append(ValidationMessage(
            severity=Severity.WARNING,
            code="orphan-produces",
            message=(
                f"Persona '{producer_id}' produces type '{artifact}' but no "
                f"persona on the team consumes it."
            ),
        ))

    result = ValidationResult(messages=messages)

    logger.info(
        "Contract-graph validation: %d missing producers, %d orphan produces",
        len(result.errors),
        len(result.warnings),
    )

    return result
