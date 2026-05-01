# Task 03: Test Sweep — Fixtures, Indexer Tier Coverage, Compiler Defaults, Error Paths

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 02 |
| **Status** | Done |
| **Started** | 2026-04-30 23:58 |
| **Completed** | 2026-05-01 00:22 |
| **Duration** | 24m |

## Goal

Update existing test fixtures to the new `core/` and `extended/`
layout, then add new tests for the tiering behavior. The full test
suite (`uv run pytest`) must pass and the bean's acceptance criteria
must be verifiable from the test suite.

## Inputs

- `ai/beans/BEAN-271-library-persona-tiering/bean.md` — bean
  acceptance criteria.
- `ai/context/decisions.md` — **ADR-014** (the syntax + error-message
  decision). Tests for the error path must assert against the message
  ADR-014 specifies.
- Tests with hardcoded `personas/<id>` paths that will break after
  Task 02:
  - `tests/test_validator.py` (lines 32, 35, 37, 161, 351, 415, 470, 562)
  - `tests/test_agent_writer.py` (lines 82, 358)
  - `tests/test_persona_contracts.py` (line 222)
- `tests/` — for placement of new tier-coverage tests. Use
  `test_library_indexer.py` if it exists, otherwise create
  `test_persona_tiering.py`.

## Acceptance Criteria

- [ ] All existing tests updated for the new persona paths
      (`personas/core/<id>` or `personas/extended/<id>` as appropriate).
- [ ] New test: `_scan_personas` returns `tier="core"` for the 5 core
      personas and `tier="extended"` for the 19 extended personas
      (covers the indexer behavior end-to-end on the real library).
- [ ] New test: default composition (no `personas:` block) compiles
      to exactly the 5 core personas (covers compiler default behavior).
- [ ] New test: composition referencing an extended persona in
      ADR-014 syntax compiles successfully and the persona appears in
      the output.
- [ ] New test: composition referencing an unknown or wrong-tier
      persona raises with the exact error message ADR-014 specifies.
- [ ] New test: indexer warns (does not crash) if `personas/core/`
      or `personas/extended/` is missing — graceful degradation matches
      the existing `_scan_personas` "directory not found" behavior.
- [ ] Wizard test (if a smoke test exists for `persona_page.py`):
      both tier groups render. If no such test exists, skip — do not
      invent UI tests for this bean.
- [ ] `uv run pytest` passes (full suite).
- [ ] `uv run ruff check foundry_app/` clean.

## Definition of Done

- All listed tests added or updated.
- Full pytest suite green.
- Status set to `Done`.

## Notes

**Verify, don't re-implement.** If something in Task 02 looks wrong
(e.g., a default-composition behavior), open a follow-up rather than
fixing it silently. The Developer owns the implementation; Tech-QA
verifies and surfaces gaps.

**Coverage focus.** This bean's value is the contract: "default = core
only; extended = explicit opt-in." Tests should make that contract
break loudly if a future change weakens it.
