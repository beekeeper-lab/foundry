# Task 02 — Tech-QA: Regression sweep + end-to-end developer+tech-qa generation

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-292 / 02 |
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Independently verify that the severity demotion preserves all
documented behavior:

1. Standard-mode generation succeeds for a `developer + tech-qa`-only
   team (the user-facing acceptance scenario).
2. STRICT-mode still gates on missing-producer (the safety lever the
   bean's Notes call out).
3. The persona-page indicator's tri-state precedence is intact: 🔴
   reachable for genuine ERROR codes, 🟡 for missing-producer or
   orphan-produces warnings, 🟢 for clean teams.
4. No collateral regressions in the validator surface, the wizard
   pages, or the generator pipeline.

Add an end-to-end regression test that runs the full generation
pipeline for `developer + tech-qa` only and asserts no
`is_valid` gate trip. Run the manual wizard verification listed in the
bean's Acceptance Criteria.

## Inputs

- `ai/beans/BEAN-292-relax-contract-graph-to-warning/bean.md` — full
  Acceptance Criteria list. The (test:tests/) E2E criterion and the
  two (manual) criteria are this task's responsibility.
- The Developer's Task 01 commits on
  `bean/BEAN-292-relax-contract-graph-to-warning` — the validator
  change, the `_run_contract_graph_check` strictness routing, the
  persona-page indicator update, and the test renames.
- `tests/test_generator.py` — `test_standard_mode_aborts_on_missing_producer`
  (line ~1557) and `test_overlay_mode_proceeds_on_missing_producer`
  (line ~1599). The standard-mode test name and assertions need to
  flip: with the demotion, standard mode no longer aborts on
  missing-producer alone.
- `foundry_app/services/generator.py` — `generate` entrypoint, used
  by the E2E test fixture.
- `ai-team-library/personas/core/developer/` and
  `.../tech-qa/` — the actual personas selected in the E2E test.

## Acceptance Criteria

- [ ] `tests/test_generator.py` — `test_standard_mode_aborts_on_missing_producer`
      is renamed and rewritten (or replaced with a new test) to assert
      that standard-mode generation **proceeds** for a team that has
      only missing-producer findings, and that the generation result
      records the warnings on the manifest or validation surface.
- [ ] `tests/test_generator.py` — a new test exercises the bean's
      headline scenario: a composition with only `developer` and
      `tech-qa` (resolved from the real library), `Strictness.STANDARD`,
      runs through `generate()` without tripping the `is_valid` gate
      and produces a non-None manifest. Use the existing test fixtures
      and helpers; do not invent a new test harness.
- [ ] `tests/test_generator.py` — a STRICT-mode test asserts that the
      same `developer + tech-qa` composition under
      `Strictness.STRICT` **does** trip the `is_valid` gate (the
      missing-producer warning is promoted back to ERROR).
- [ ] `tests/test_validator.py` — confirm that all pre-existing
      `TestContractGraphValidator*` tests still pass after the rename
      sweep. Specifically: orphan-produces tests (still WARNING),
      ignored-types tests, library-producer-suggestion tests, and the
      pluralization/sorting tests should be untouched in semantics.
- [ ] `tests/test_persona_page.py` — confirm the truncation cap (six
      findings collapse to "+1 more") still works in the yellow state
      after the move from red. The verbatim-message bullets format is
      unchanged.
- [ ] (manual) Launch the wizard with `uv run foundry`, select only
      `developer + tech-qa` on the persona page, walk through every
      wizard page accepting defaults, click Generate, and confirm: (a)
      generation completes without an "is_valid" block, (b) the
      persona page shows a yellow coherence indicator with the
      friendly missing-supplier bullets, (c) the Next button is
      enabled at every page. Capture a one-paragraph observation note
      in `ai/outputs/tech-qa/BEAN-292-manual-verification.md` (create
      the file).
- [ ] (manual) From the same wizard, switch strictness to STRICT
      (settings or composition.yml — whichever is exposed in the UI),
      keep the developer + tech-qa team, click Generate, and confirm
      generation now blocks with the friendly BEAN-290 message. Note
      the result in the same observation file.
- [ ] `uv run pytest` passes — full suite, no skips beyond pre-existing
      ones.
- [ ] `uv run ruff check foundry_app/` passes.
- [ ] If any acceptance criterion fails or any regression surfaces,
      file the finding back to the Developer via `/handoff` (Tech-QA →
      Developer kick) and leave the bean `In Progress` for a fix
      cycle.

## Definition of Done

- All acceptance criteria checked.
- Manual-verification observation file committed at
  `ai/outputs/tech-qa/BEAN-292-manual-verification.md`.
- Status set to `Done`; the PostToolUse telemetry hook auto-stamps
  `Completed` and `Duration`.
- Bean is ready for the orchestrator's verification + close phase
  (Phase 5 of `/long-run`).

## Notes

**STRICT-mode test placement.** The existing
`run_pre_generation_validation` + strictness tests live in
`tests/test_validator.py`; the new STRICT-mode contract-graph
integration test belongs in `tests/test_generator.py` (because the
contract-graph messages are merged into the validation result inside
`generate()`, not inside `validate_contract_graph` itself). Don't
duplicate the test in both files.

**No mocks for the E2E test.** The bean's headline scenario runs the
real `developer` and `tech-qa` personas from the library against the
real generator. Use the same fixture pattern as the existing
`test_standard_mode_aborts_on_missing_producer` test. If that test
uses synthetic personas, the new test should use real ones to catch
any drift between the synthetic shapes and what `developer.contracts.yml`
and `tech-qa.contracts.yml` actually declare.

**Manual-verification reproducibility.** Note the wizard build that
was tested (commit SHA), the wall-clock time, and any deviation from
the Acceptance Criteria's expected outcome. The observation file is
small but it's the only artifact that confirms the GUI-path
acceptance.
