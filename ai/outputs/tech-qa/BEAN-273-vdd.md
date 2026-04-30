# BEAN-273 — Verification & Defect Disposition Report

**Owner:** Tech-QA
**Bean:** BEAN-273 — Persona `produces:` / `consumes:` Contracts
**Task:** 04 — Verify Contracts (tests, lint, AC sweep)
**Date:** 2026-04-30
**Branch:** `bean/BEAN-273-persona-produces-consumes-contracts`

## Recommendation

**PASS — bean is ready for Team-Lead to mark Done.**

All 8 BEAN-273 acceptance criteria are met with concrete evidence. The full
test suite (2217 tests) is green; lint is clean. No regressions detected.

## Gaps

_None._ Every AC has a Pass row with reproducible evidence below.

## Test execution summary

| Command | Result |
|---|---|
| `uv run pytest` | `2217 passed, 4 warnings in 12.02s` |
| `uv run ruff check foundry_app/` | `All checks passed!` |
| `uv run pytest tests/test_persona_contracts.py -v` | `20 passed in 0.28s` |

The 4 warnings are pre-existing PySide6 `QMouseEvent` deprecation notices
unrelated to BEAN-273.

## New test coverage

File: `tests/test_persona_contracts.py` (20 new tests in 6 classes,
mapping to the six coverage points enumerated in the task spec).

| Class | Tests | Maps to coverage point |
|---|---|---|
| `TestArtifactTypeRegistryParses` | 5 | (1) Registry parses |
| `TestArtifactTypeRegistryRejectsMalformed` | 4 | (2) Registry rejects malformed |
| `TestPersonaContractsParse` | 2 | (3) Persona contracts parse |
| `TestTypeResolution` | 2 | (4) Type resolution |
| `TestCrossPersonaPairing` | 3 | (5) Cross-persona pairing + regression guard |
| `TestComposeRoundTrip` | 4 | (6) Compiler round-trip |

## BEAN-273 Acceptance Criteria Sweep

| # | Acceptance Criterion | Status | Evidence |
|---|---|---|---|
| 1 | `ai-team-library/contracts/artifact-types.yml` exists with the initial registry. | **Pass** | File present (15 entries, 230 lines). `TestArtifactTypeRegistryParses::test_registry_returns_non_empty_list`, `::test_registry_count_in_expected_range`, `::test_registry_contains_named_core_types` |
| 2 | All 5 core persona files declare `produces:` and `consumes:` lists. | **Pass** | `TestPersonaContractsParse::test_contracts_yml_files_present_for_core_personas` (sibling `contracts.yml` per ADR-013 — supersedes "frontmatter" wording in the bean Notes); `::test_each_core_persona_has_non_empty_produces_and_consumes` |
| 3 | Every type referenced by a persona exists in the registry (validated by tests). | **Pass** | `TestTypeResolution::test_every_referenced_type_resolves_in_registry`; negative-path coverage in `::test_unknown_type_in_synthetic_persona_is_dropped_with_warning` |
| 4 | Compiled `composition.yml` in generated projects contains a `contracts:` block summarizing the team's graph. | **Pass** | `TestComposeRoundTrip::test_composition_yml_contains_contracts_block`, `::test_contracts_block_has_per_persona_lists`, `::test_contracts_block_has_flat_artifact_types_reference`, `::test_no_contracts_block_when_team_empty` |
| 5 | At least one core persona pair has matching `produces` → `consumes`. | **Pass** | `TestCrossPersonaPairing::test_ba_produced_type_is_consumed_by_developer` (asserts `user-story` overlap); `::test_developer_produced_type_is_consumed_by_tech_qa` (asserts `code-change` overlap) |
| 6 | No core persona has `produces:` or `consumes:` empty. | **Pass** | `TestPersonaContractsParse::test_each_core_persona_has_non_empty_produces_and_consumes` — loops all five core personas, asserts both lists non-empty |
| 7 | All tests pass (`uv run pytest`). | **Pass** | `2217 passed, 4 warnings in 12.02s` (no regressions in the prior baseline; new file adds 20 tests) |
| 8 | Lint clean (`uv run ruff check foundry_app/`). | **Pass** | `All checks passed!` |

## Task-04 Acceptance Criteria Sweep

| # | Task AC | Status | Evidence |
|---|---|---|---|
| T1 | All six new tests added under `tests/` and pass. | **Pass** | `tests/test_persona_contracts.py` adds 20 tests across the six required coverage points; `pytest tests/test_persona_contracts.py -v` → `20 passed` |
| T2 | `uv run pytest` is green (no regressions in the existing baseline). | **Pass** | `2217 passed, 4 warnings in 12.02s` — only pre-existing PySide6 QMouseEvent deprecations |
| T3 | `uv run ruff check foundry_app/` is clean. | **Pass** | `All checks passed!` |
| T4 | `ai/outputs/tech-qa/BEAN-273-vdd.md` exists with a row per BEAN-273 AC. | **Pass** | This file. |
| T5 | Cross-persona assertion fails on a synthetic persona that drops the `user-story` consume edge (regression guard). | **Pass** | `TestCrossPersonaPairing::test_synthetic_break_of_user_story_chain_is_caught` constructs a tmp_path library where Developer drops `user-story`, then asserts the BA→Developer overlap goes away — a future edit that breaks the chain in the real library will fail `test_ba_produced_type_is_consumed_by_developer` |

## Notes for Team-Lead

- The bean Notes recommend "YAML frontmatter at the top of `persona.md`,
  fenced with `---`," but Architect's ADR-013 chose **sibling
  `contracts.yml` next to `persona.md`** instead. The structural intent
  ("declare produces and consumes per persona") is fully satisfied; only
  the storage mechanism differs. AC #2 evidence reflects ADR-013.
- The compiler emits the `contracts:` block from the **scaffold** stage
  (where `composition.yml` is written), not the `compile` stage — see
  `foundry_app/services/scaffold.py:_build_contracts_yaml_block`. The AC
  text says "compiled `composition.yml`" which matches the resulting
  artifact regardless of the stage that writes it.
- Total registry entries: 15 (top of the bean's "12-15 types" range).
- Cross-persona pairs explicitly tested: BA→Developer (`user-story`),
  Developer→Tech-QA (`code-change`). Both have spec-level assertions, not
  just intersection tests, so a future rename also fails fast.

## Files touched by Task 04

- **New:** `tests/test_persona_contracts.py` (20 tests).
- **New:** `ai/outputs/tech-qa/BEAN-273-vdd.md` (this report).
- No production code changed in this task.
