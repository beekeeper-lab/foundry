# Task 02: Tech-QA — Orphan-produces filter coverage + real-library regression

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-289 / 02 |
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-05-01 13:43 |
| **Completed** | 2026-05-01 13:45 |
| **Duration** | 2m |

## Goal

Bind the new validator behavior with tests, fix the existing tests
whose fixtures relied on the old "always warn" behavior, and add a
real-library regression test that proves the user-visible payoff:
zero `orphan-produces` warnings for the 5 core personas.

## Inputs

- `foundry_app/services/validator.py` — Developer task 01's
  implementation.
- `tests/test_validator.py` — existing BEAN-274 contract-graph test
  classes (`TestContractGraphValidatorOrphanProduces`,
  `TestContractGraphValidatorMixedResults`) whose fixtures need a
  library consumer added so the warning still fires.
- `tests/test_persona_page.py` — the `coherence_page` fixture's
  `orphan-producer` persona produces `orphan-thing` with no library
  consumer; the yellow indicator test relies on the warning firing.
- `ai-team-library/` — read-only library used for the real-library
  regression test.

## Acceptance Criteria

- [ ] **New positive test** in `tests/test_validator.py`:
      `validate_contract_graph` does NOT emit `orphan-produces` when
      the produced artifact has no library-wide consumer.
- [ ] **New regression test** in `tests/test_validator.py`:
      `validate_contract_graph` DOES emit `orphan-produces` when the
      produced artifact has at least one library-wide consumer (even
      if that consumer is not on the team). The
      `test_orphan_warning_fires_even_when_library_has_consumer` test
      already covers this case — verify it still passes (it should,
      unmodified).
- [ ] **Real-library regression** in `tests/test_validator.py`:
      indexes the real `ai-team-library/` (use `index_library` from
      `library_indexer`), composes the 5 core personas (`architect`,
      `ba`, `developer`, `team-lead`, `tech-qa`), and asserts
      `validate_contract_graph` returns zero `orphan-produces`
      warnings.
- [ ] **Persona-page test** in `tests/test_persona_page.py`: the 5
      core personas against the real library produce a 🟢
      ("satisfied") indicator (i.e., not 🟡, not hidden). This is the
      user-visible payoff.
- [ ] **Existing tests updated**: every test that previously asserted
      a warning fires must now ensure the produced artifact has a
      library-side consumer in its `_registry(...)` argument, or be
      moved to the new "no library consumer ⇒ no warning" assertion.
      Specifically expect updates to:
        - `test_orphan_produces_emits_warning`
        - `test_orphan_produces_severity_is_warning`
        - `test_mixed_missing_and_orphan`
        - `test_message_ordering_errors_before_warnings`
        - the `coherence_page` fixture's `orphan-producer` so the
          yellow indicator test stays meaningful.
- [ ] `uv run pytest` passes (full suite, no new failures).
- [ ] `uv run ruff check foundry_app/` is clean.

## Definition of Done

- [ ] All bean Acceptance Criteria are checked (see bean.md).
- [ ] `uv run pytest tests/test_validator.py tests/test_persona_page.py
      -v` passes locally.
- [ ] `uv run pytest` (full suite) passes locally.
- [ ] `uv run ruff check foundry_app/` is clean.
- [ ] No tests skip the real-library regression (it must run on the
      checked-in `ai-team-library/`).
