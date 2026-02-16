# Task 02: Verify Missing Stages Fix

| Field | Value |
|-------|-------|
| **Owner** | Tech QA |
| **Status** | Pending |
| **Depends On** | Task 01 |

## Goal

Verify that the PIPELINE_STAGES update is correct, tests pass, and lint is clean.

## Acceptance Criteria

- [ ] `PIPELINE_STAGES` lists all 8 stages in correct order
- [ ] Stage IDs match generator's `_run_stage()` keys exactly
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)
- [ ] Progress bar range matches stage count (verified by code inspection)

## Definition of Done

All tests pass, lint clean, stage list verified against generator.
