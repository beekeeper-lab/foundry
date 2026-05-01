# Task 02 — Tech-QA: sticky banner visibility tests

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-05-01 11:47 |
| **Completed** | 2026-05-01 11:47 |
| **Duration** | < 1m |

## Goal

Lock the new sticky-banner behavior with tests. Cover both `finish` (success) and `finish_with_error` paths, the start-resets-banner path, and the auto-scroll safety net.

## Inputs

- `ai/beans/BEAN-287-generation-failure-recovery-banner/bean.md` — acceptance criteria
- `ai/beans/BEAN-287-generation-failure-recovery-banner/tasks/01-developer-sticky-banner.md` — implementation contract
- `tests/test_generation_progress.py` — existing test scaffolding (qapp fixture, screen construction)

## Acceptance Criteria

- [ ] (test:tests/test_generation_progress.py) New test class `TestOutcomeBanner` exposes:
  - banner hidden after construction
  - banner hidden after `start()` (even after a prior outcome was shown)
  - banner visible after `finish()` and contains Back + Open buttons
  - banner visible after `finish_with_error()` and contains the failure message + Back button (no Open)
- [ ] (test:tests/test_generation_progress.py) Assert that `_outcome_banner` is a sibling of `_scroll` in the outer layout (i.e., not nested inside the scroll viewport) — this is what makes it "sticky" at small window sizes.
- [ ] All existing tests in the file continue to pass without modification (verify the `_back_btn`, `_open_btn`, `_summary_label` properties still resolve and behave as before).
- [ ] Suite-wide: `uv run pytest`.
- [ ] Lint: `uv run ruff check foundry_app/`.

## Definition of Done

- [ ] Tests added under existing structure.
- [ ] No flakiness — deterministic, no GUI display required.
- [ ] Status set to `Done`.
