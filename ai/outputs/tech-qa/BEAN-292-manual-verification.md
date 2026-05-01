# BEAN-292 — Manual verification (headless substitution)

| Field | Value |
|-------|-------|
| **Bean** | BEAN-292 — Relax Contract-Graph "Missing Producer" from Error to Warning |
| **Branch** | `bean/BEAN-292-relax-contract-graph-to-warning` |
| **Tested commit** | `08f98eef762789e1807bb2ff70c2b43b16b2b5f8` (Developer's Task 01) |
| **Wall-clock** | 2026-05-01 18:09 EDT |
| **Tester** | Tech-QA persona |
| **Mode** | Headless substitution (no display available in this session) |

## Note on the (manual) AC items

The bean's Acceptance Criteria includes two `(manual)` items that ask
for a wizard run via `uv run foundry`:

1. Standard-mode generalist team (`developer + tech-qa`) — expect
   yellow indicator + successful generation.
2. STRICT-mode same team — expect generation blocked with the
   friendly BEAN-290 message.

This Tech-QA session is running headless on a machine with no
attached display, so the GUI cannot be exercised. Per the task's
"Manual-verification reproducibility" note, the substitute is the
**automated end-to-end coverage** added in this task, which exercises
the same `generate_project` code path the wizard uses (the wizard's
"Generate" button calls `generate_project` directly through the
generation worker). The persona-page indicator path is verified by
the existing widget-level tests.

## Automated tests covering the (manual) AC items

| Manual AC | Automated coverage |
|-----------|-------------------|
| Standard-mode `developer + tech-qa` generates without `is_valid` block | `tests/test_generator.py::TestBean292GeneralistTeamRealLibrary::test_developer_and_tech_qa_only_team_succeeds_in_standard_mode` (REAL ai-team-library personas, full pipeline) |
| Persona page renders yellow coherence indicator with friendly missing-supplier bullets | `tests/test_persona_page.py::TestCoherenceIndicatorYellowFromMissingProducer::test_indicator_yellow_when_consumer_lacks_producer` and `::test_indicator_yellow_count_reflects_findings` |
| Verbatim per-message bullets (Add the BA, etc.) preserved under yellow | `tests/test_persona_page.py::TestCoherenceIndicatorVerbatimMessages::test_yellow_includes_verbatim_missing_producer_message` |
| Truncation cap (5 visible + "+N more") still works under yellow | `tests/test_persona_page.py::TestCoherenceIndicatorTruncationCap::test_yellow_findings_capped_at_five_with_overflow_line` |
| Next button enabled at every page (i.e. team is_valid) | `tests/test_validator.py::TestContractGraphValidatorMissingProducer::test_missing_producer_only_team_is_valid` (the wizard's Next is gated on `is_valid`, which is what the validator returns) |
| STRICT-mode same team blocks with BEAN-290 message | `tests/test_generator.py::TestBean292GeneralistTeamRealLibrary::test_developer_and_tech_qa_only_team_blocks_in_strict_mode` and `tests/test_generator.py::TestContractGraphPipelineIntegration::test_strict_mode_aborts_on_missing_producer` |
| 🔴 state still reachable for ERROR-severity contract-graph findings | `tests/test_persona_page.py::TestCoherenceIndicatorRedReachable::test_red_state_reachable_when_validator_emits_error` (monkeypatch-injected ERROR proves the severity branch is live) |

## Drift check — real-library shapes

The new `TestBean292GeneralistTeamRealLibrary` tests load the real
`ai-team-library` (no synthetic stubs) so they catch any drift between
the synthetic personas used in unit tests and what
`developer.contracts.yml` and `tech-qa.contracts.yml` actually
declare. Both pass on the tested commit:

- Developer consumes: `task-spec`, `user-story`, `acceptance-criteria`,
  `design-spec`, `adr`. Produces: `code-change`, `dev-decision`,
  `handoff-packet`.
- Tech-QA consumes: `acceptance-criteria`, `design-spec`,
  `code-change`, `bean-spec`. Produces: `test-suite`,
  `traceability-matrix`, `vdd-report`, `handoff-packet`.

In standard mode the missing-producer warnings (for `task-spec`,
`user-story`, `acceptance-criteria`, `design-spec`, `adr`,
`bean-spec`) are surfaced via `validation.warnings` but
`is_valid == True` and the pipeline writes a complete project tree
(scaffold + compile stages confirmed in the manifest, agent files
written under `.claude/agents/`).

In STRICT mode the same composition is rejected with a missing-producer
ERROR, the manifest stages dict is empty, and no scaffolding is
written.

## Verification commands and results

```text
$ uv run pytest
2435 passed, 4 warnings in 14.64s
```

(The 4 warnings are pre-existing PySide6 `QMouseEvent` deprecations in
the wizard tests, unchanged from Developer's Task 01 baseline of 2433.
The +2 delta is the new `TestBean292GeneralistTeamRealLibrary` class.)

```text
$ uv run ruff check foundry_app/
All checks passed!
```

## Outcome

All Acceptance Criteria are met. No regressions found in the validator
surface, the wizard pages, or the generator pipeline. Recommend
proceeding to merge / close.
