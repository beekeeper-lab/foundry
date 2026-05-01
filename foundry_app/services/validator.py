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
from foundry_app.services.artifact_labels import (
    artifact_label,
    join_personas,
    persona_name,
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
                message=(
                    f"The {persona_name(ps.id)} persona is in the library but its "
                    f"profile file (persona.md) is missing — this is a library-data "
                    f"issue, not your composition. Generation will continue but the "
                    f"agent file will be sparse."
                ),
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
                message=(
                    f"The '{ss.id}' expertise pack isn't in the library — check the "
                    f"spelling, or remove it from your selection."
                ),
            ))
        elif not expertise.files:
            messages.append(ValidationMessage(
                severity=Severity.WARNING,
                code="expertise-no-files",
                message=(
                    f"The '{ss.id}' expertise pack is in the library but has no "
                    f"convention files — this is a library-data issue, not your "
                    f"composition. Generation will continue but the expertise will "
                    f"contribute nothing."
                ),
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
                message=(
                    f"The '{hp.id}' hook pack isn't in the library — check the "
                    f"spelling, or remove it from your selection."
                ),
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
                        f"The '{pair[0]}' and '{pair[1]}' hook packs can't be used "
                        f"together — pick one and remove the other."
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
            logger.info(
                "hook-pack-posture-incompatible: pack=%s posture=%s "
                "(Posture Compatibility table says Included: No)",
                hp.id, posture_key,
            )
            messages.append(ValidationMessage(
                severity=Severity.ERROR,
                code="hook-pack-posture-incompatible",
                message=(
                    f"The '{hp.id}' hook pack isn't available at the "
                    f"'{posture_key}' safety posture. Either remove the pack, or "
                    f"raise your composition's posture so it's allowed."
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
            message=(
                "You haven't selected any team members yet. Pick at least one "
                "persona on the Persona Selection page so the generated project "
                "has a team."
            ),
        ))

    if not composition.expertise:
        messages.append(ValidationMessage(
            severity=Severity.INFO,
            code="no-expertise",
            message=(
                "You haven't selected any expertise packs. The generated project "
                "will work, but it won't carry any technology-specific "
                "conventions. If that's intentional, you can ignore this."
            ),
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
                message=(
                    f"You've added the {persona_name(pid)} more than once — "
                    f"extra copies have no effect, you can remove the "
                    f"duplicates."
                ),
            ))
        seen_personas.add(pid)

    expertise_ids = [ss.id for ss in composition.expertise]
    seen_expertise: set[str] = set()
    for sid in expertise_ids:
        if sid in seen_expertise:
            messages.append(ValidationMessage(
                severity=Severity.WARNING,
                code="duplicate-expertise",
                message=(
                    f"You've added the '{sid}' expertise pack more than once — "
                    f"extra copies have no effect, you can remove the "
                    f"duplicates."
                ),
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

    1. **Missing producer** (WARNING): every artifact type consumed by some
       team member is also produced by some team member. When a producer
       is absent from the team, the validator emits a friendly *advisory*
       naming the missing artifact, the team consumers, and any producer
       personas in the library so the user knows whom they could add.

    2. **Orphan produces** (WARNING): an artifact type is produced by a
       team member but consumed by no team member. Indicates a wasted
       output channel, not a broken pipeline. ``handoff-packet`` is
       excluded (universally produced; implicitly consumed by Team Lead).

    **Why warning, not error (BEAN-292).** ``consumes`` describes how a
    persona *collaborates* when teammates that produce the artifact are
    present — not a hard prerequisite for the persona to function. A
    generalist team (e.g. ``developer + tech-qa`` only) is a valid
    composition: those personas absorb the BA / Architect responsibilities
    informally rather than failing because no one supplies user-stories or
    ADRs. Treating ``missing-producer`` as ERROR forced every team to
    include the full core tier any time ``developer`` or ``tech-qa`` was
    selected, which broke the small-startup / generalist-team pattern.
    Users who *do* want the hard gate can opt in via the strictness lever
    (``Strictness.STRICT``), which promotes WARNING back to ERROR through
    :func:`_apply_strictness` and restores the blocking behaviour.

    Args:
        personas: The selected team (members composing the project). May
            be empty — in which case the result is trivially valid.
        registry: The library index, used as the registry of all personas
            (and their declared produces) for "Producers in library"
            suggestions when an unsatisfied consume is found.

    Returns:
        A ``ValidationResult`` with ordered messages: missing-producer
        warnings first (sorted by artifact type), then orphan-produces
        warnings (sorted by artifact type, then producer id). Both are
        WARNING severity by default; STRICT-mode strictness promotes them
        to ERROR.
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

    # Library-wide producer and consumer indexes. ``library_producers``
    # is used to suggest who to add when a consume is unsatisfied;
    # ``library_consumers`` is used to filter orphan-produces warnings
    # for artifacts no library persona consumes (the user can't fix
    # those — see BEAN-289).
    library_producers: dict[str, list[str]] = {}
    library_consumers: dict[str, list[str]] = {}
    for persona in registry.personas:
        for artifact in persona.produces:
            if artifact in _CONTRACT_GRAPH_IGNORED_TYPES:
                continue
            library_producers.setdefault(artifact, []).append(persona.id)
        for artifact in persona.consumes:
            if artifact in _CONTRACT_GRAPH_IGNORED_TYPES:
                continue
            library_consumers.setdefault(artifact, []).append(persona.id)

    # Missing producers — consumed by the team, produced by nobody on the team.
    missing_types = sorted(
        artifact for artifact in team_consumers
        if artifact not in team_producers
    )
    for artifact in missing_types:
        consumers = team_consumers[artifact]
        lib_producers = sorted(set(library_producers.get(artifact, [])))
        consumers_label = join_personas(consumers, prefix="")
        type_label = artifact_label(artifact)
        verb = "needs" if len(consumers) == 1 else "need"
        if lib_producers:
            producer_options_label = join_personas(lib_producers)
            text = (
                f"Your {consumers_label} {verb} {type_label}, but no one on "
                f"your team can supply it. Add {producer_options_label} to "
                f"your team."
            )
        else:
            text = (
                f"Your {consumers_label} {verb} {type_label}, but no persona "
                f"in the library can supply it — this is a library gap, not a "
                f"team-composition issue."
            )
        messages.append(ValidationMessage(
            severity=Severity.WARNING,
            code="missing-producer",
            message=text,
        ))

    # Orphan produces — produced by the team, consumed by nobody on the
    # team. BEAN-289: only warn when at least one library persona
    # declares ``consumes`` on the artifact. If no library persona
    # consumes it, the warning is unactionable (the user has no team
    # composition that closes the graph) and is suppressed.
    orphan_pairs: list[tuple[str, str]] = []
    for artifact in sorted(team_producers):
        if artifact in team_consumers:
            continue
        if not library_consumers.get(artifact):
            continue
        for producer_id in team_producers[artifact]:
            orphan_pairs.append((artifact, producer_id))
    # Stable sort: by artifact (already sorted) then by producer id
    orphan_pairs.sort(key=lambda pair: (pair[0], pair[1]))
    for artifact, producer_id in orphan_pairs:
        producer_label = persona_name(producer_id)
        type_label = artifact_label(artifact)
        consumer_options = sorted(set(library_consumers.get(artifact, [])))
        if consumer_options:
            consumer_options_label = join_personas(consumer_options)
            fix_clause = (
                f"Either add {consumer_options_label} so someone reads it, or "
                f"remove the {producer_label} if you don't need this output."
            )
        else:
            fix_clause = (
                f"Remove the {producer_label} if you don't need this output."
            )
        messages.append(ValidationMessage(
            severity=Severity.WARNING,
            code="orphan-produces",
            message=(
                f"The {producer_label} produces {type_label} that no one else "
                f"on your team uses. {fix_clause}"
            ),
        ))

    result = ValidationResult(messages=messages)

    missing_producer_count = sum(
        1 for m in result.messages if m.code == "missing-producer"
    )
    orphan_produces_count = sum(
        1 for m in result.messages if m.code == "orphan-produces"
    )
    logger.info(
        "Contract-graph validation: %d missing producers, %d orphan produces",
        missing_producer_count,
        orphan_produces_count,
    )

    return result
