# Task 01 — Developer: Demote missing-producer to WARNING and update persona-page indicator

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-292 / 01 |
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Demote the contract-graph `missing-producer` finding from `Severity.ERROR`
to `Severity.WARNING` so a `developer + tech-qa`-only team passes
standard-mode validation and proceeds to generation. Preserve the
strictness lever — `Strictness.STRICT` must continue to promote the
warning back to ERROR for users who opt in. Update the persona-page
team-coherence indicator so a missing-producer-only finding renders as
🟡 (advisory), with the headline copy clarified to cover both
missing-supplier and unused-output messages. Update existing tests in
`tests/test_validator.py` and `tests/test_persona_page.py` that assert
the old ERROR / 🔴 expectations to assert the new WARNING / 🟡
expectations. Document the rationale in the validator docstring so
future refactors don't regress.

## Inputs

- `ai/beans/BEAN-292-relax-contract-graph-to-warning/bean.md` — Problem
  Statement, Goal, Scope, Acceptance Criteria, and the
  coherence-indicator state model (table in Notes).
- `foundry_app/services/validator.py` — `validate_contract_graph`
  (line ~336), the `Severity.ERROR` emission for `missing-producer`
  (line ~430), and `_apply_strictness` (line ~261).
- `foundry_app/services/generator.py` — `_run_contract_graph_check`
  (line ~125) and the merge into the pre-generation `ValidationResult`
  (line ~420). The contract-graph messages are appended *after*
  `run_pre_generation_validation` applies `_apply_strictness`, so this
  task must route contract messages through the same strictness pass to
  preserve STRICT-mode promotion.
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` —
  `_update_coherence_indicator` (line ~610). The state machine
  currently splits on error count vs warning count; after this change,
  missing-producer warnings join the yellow branch.
- `tests/test_validator.py` — existing tests that assert ERROR severity
  and `not result.is_valid`: `test_missing_producer_is_error`
  (line ~679), `test_missing_producer_severity_is_error` (line ~754),
  and any related assertions in the `TestContractGraphValidator*`
  classes.
- `tests/test_persona_page.py` — `TestCoherenceIndicatorRed` (line
  ~833): tests asserting 🔴 emoji and "missing role(s)" headline for
  consumer-without-producer; these must move to a yellow-state class.
  `test_red_includes_verbatim_missing_producer_message` (line ~1015)
  and `test_red_findings_capped_at_five_with_overflow_line` (line
  ~1044) similarly need to move from red to yellow expectations.

## Acceptance Criteria

- [ ] `validate_contract_graph` in `foundry_app/services/validator.py`
      emits `missing-producer` messages with `severity =
      Severity.WARNING` (not `Severity.ERROR`).
- [ ] The function's docstring documents the rationale: a one-paragraph
      "Why warning, not error" note explaining that `consumes` describes
      collaboration when teammates are present, not a hard prerequisite,
      so a generalist team (e.g., developer + tech-qa) still validates.
      The note mentions the strictness lever as the opt-in for the hard
      gate.
- [ ] `_run_contract_graph_check` in `foundry_app/services/generator.py`
      applies `_apply_strictness` to the contract-graph messages before
      returning them, so STRICT-mode users still get the hard gate. (The
      function currently bypasses strictness; route contract messages
      through the same policy pass.)
- [ ] `tests/test_validator.py` — `test_missing_producer_is_error` is
      renamed to `test_missing_producer_is_warning` (or analogous) and
      asserts `result.is_valid` is **True**, `len(result.warnings) ==
      1`, and `msg.severity == Severity.WARNING`.
- [ ] `tests/test_validator.py` — `test_missing_producer_severity_is_error`
      is renamed to `_is_warning` and asserts WARNING severity.
- [ ] `tests/test_validator.py` — a new test asserts that
      `_apply_strictness([missing-producer WARNING], Strictness.STRICT)`
      returns the message with `Severity.ERROR`.
- [ ] `tests/test_validator.py` — a new test asserts that the
      `developer + tech-qa`-only team (or any team with only
      missing-producer findings) yields `result.is_valid == True`.
- [ ] `foundry_app/ui/screens/builder/wizard_pages/persona_page.py`
      `_update_coherence_indicator` renders 🟡 when only
      missing-producer warnings are present (no other errors). The
      headline copy works for both missing-supplier and unused-output
      messages — choose one of:
      - a unified "Team check" headline that lists the count of
        warnings without naming the cause, or
      - a dispatch on warning code so missing-producer renders one
        headline and orphan-produces renders another.
      Either approach is fine; the bean's Notes table is the source of
      truth for which states are red vs yellow vs green.
- [ ] 🔴 remains reachable for the genuine ERROR codes:
      `hook-pack-conflict`, `hook-pack-posture-incompatible`,
      `missing-persona`, `missing-expertise`, `missing-hook-pack`,
      `duplicate-persona`, `duplicate-expertise`. (These are not
      surfaced by `validate_contract_graph` itself, but the
      indicator's tri-state precedence must still gate on them when
      they appear via the broader pre-generation result. If the
      indicator only sees contract-graph messages today, document that
      and leave the broader integration for a later bean.)
- [ ] `tests/test_persona_page.py` — `TestCoherenceIndicatorRed` tests
      that exercised consumer-without-producer move to a yellow-state
      class; the asserted emoji is `\U0001f7e1` (yellow). The
      `test_red_includes_verbatim_missing_producer_message` and
      `test_red_findings_capped_at_five_with_overflow_line` tests
      similarly move to yellow expectations (verbatim messages and
      truncation cap behavior are unchanged; only the emoji and any
      red-specific copy change).
- [ ] If any test name in `test_persona_page.py` currently asserts a
      "🔴 only" precedence behavior that no longer holds for
      missing-producer, the test is either kept under a different
      class name (with updated assertions) or replaced with an
      equivalent test for a still-red-state code. Do not delete
      coverage.
- [ ] `uv run pytest` passes locally for the developer at completion.
- [ ] `uv run ruff check foundry_app/` passes locally for the
      developer at completion.

## Definition of Done

- All acceptance criteria checked.
- Code committed on branch `bean/BEAN-292-relax-contract-graph-to-warning`.
- Status set to `Done`; the PostToolUse telemetry hook auto-stamps
  `Completed` and `Duration`.
- Hand off to Tech-QA via `/handoff` (or by setting Task 02 to ready).

## Notes

**Why the strictness routing matters.** `_run_contract_graph_check`
currently appends contract messages to the validation result *after*
`_apply_strictness` has run on the rest of the messages. If we leave
that path alone, a STRICT-mode user will still see WARNING severity
for missing-producer (since strictness never sees the contract
messages), and the bean's "STRICT promotes to ERROR" guarantee breaks.
The fix is small: in `_run_contract_graph_check`, accept the
`strictness` parameter and call `_apply_strictness(messages,
strictness)` on the demoted-or-not list before returning, OR have the
generator apply strictness uniformly across the merged result before
the `is_valid` check. Either is correct; the second is structurally
cleaner. Pick one and document the choice in the commit message.

**Coherence-indicator headline copy.** The current yellow headline
talks about "unused outputs" — that's specific to orphan-produces. With
missing-producer joining yellow, you have a few options:
1. Keep two warning subheadlines and dispatch on code.
2. Adopt a unified "Team check: N team note(s)" headline and let the
   bullets carry the specifics.
3. Treat missing-producer count and orphan-produces count as separate
   sub-counts in one headline ("2 missing roles, 1 unused output").
Whichever you pick, ensure the existing yellow-state tests still pass
or are updated together. The verbatim per-message bullets (BEAN-286)
do not change.
