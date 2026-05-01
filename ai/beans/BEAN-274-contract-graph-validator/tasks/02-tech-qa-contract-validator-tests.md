# Task 02: Test Coverage — Contract Validator (All Paths)

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-05-01 00:35 |
| **Completed** | 2026-05-01 00:44 |
| **Duration** | 9m |

## Goal

Cover every path of the contract-graph validator: valid team, missing
producer (standard hard-fail), missing producer (overlay warn), orphan
producer warning, wizard indicator state transitions. Full pytest
suite must pass and lint must stay clean.

## Inputs

- `ai/beans/BEAN-274-contract-graph-validator/bean.md` — bean
  acceptance criteria.
- The implementation Task 01 produced (read what's actually there
  rather than assuming — the Developer may have placed the validator
  in `validator.py` or in a new `contract_validator.py`).
- `tests/` directory — existing test patterns. Look at:
  - `tests/test_validator.py` — for ValidationResult assertion idioms.
  - `tests/test_generator.py` — for end-to-end pipeline test idioms
    (esp. how to construct a CompositionSpec + minimal library).
  - `tests/test_persona_page.py` — for wizard test idioms (esp.
    BEAN-271's tier-group tests, freshly added).

## Acceptance Criteria

- [ ] `validate_contract_graph()` test: valid team (every consume has
      a producer) returns success.
- [ ] Test: missing producer in standard mode raises / produces a
      ValidationResult with severity ERROR, the missing type name in
      the message, and the consuming persona named.
- [ ] Test: missing producer in overlay mode produces a warning in
      `GenerationManifest` and the pipeline proceeds (returns a
      manifest, does not abort).
- [ ] Test: orphan producer (persona produces a type nobody on the
      team consumes) emits a warning in both modes.
- [ ] Test: integration through `generate_project` — standard mode
      with a known-broken team aborts; overlay mode with the same team
      proceeds and the manifest carries the warning.
- [ ] Wizard test: persona page indicator transitions through
      🟢/🟡/🔴 as personas are checked/unchecked. (If the indicator is
      not testable in isolation, settle for a unit test on the
      computation function the indicator depends on.)
- [ ] `uv run pytest` passes (full suite).
- [ ] `uv run ruff check foundry_app/` clean.

## Definition of Done

- All listed tests added (in `tests/test_contract_validator.py` if
  the Developer made a new module, otherwise extending
  `tests/test_validator.py`).
- Full pytest suite green.
- Status set to `Done`.

## Notes

**Verify, don't re-implement.** If you find a bug in the Developer's
implementation, stop and report it rather than patching the
implementation in this task. Examples:
- The error message doesn't match the format the bean specifies.
- Overlay mode aborts instead of warning.
- The wizard indicator never reaches 🔴.

**Coverage focus.** The contract this bean adds is: "compose-time
guarantee that every team is internally coherent (or, in overlay,
loudly noted when it isn't)." Tests should make that contract break
loudly if a future change weakens it.
