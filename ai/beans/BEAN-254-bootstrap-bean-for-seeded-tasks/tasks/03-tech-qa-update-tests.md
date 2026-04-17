# Task 03 — Tech-QA: Update and Add Seeder Tests

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 02 |
| **Status** | Done |
| **Started** | 2026-04-17 18:48 |
| **Completed** | 2026-04-17 18:50 |
| **Duration** | ~2m |

## Goal

Update existing seeder/generator tests for the new starter-bean output shape and add a test asserting the starter bean exists with the expected task files. Verify the full suite passes and lint is clean.

## Inputs

- `tests/test_seeder.py`
- `tests/test_generator.py`
- `foundry_app/services/seeder.py` (post task 02)

## Required Changes

- **`tests/test_seeder.py`** — rewrite the assertions so they read `ai/beans/BEAN-001-bootstrap/bean.md` and its `tasks/` directory instead of `ai/tasks/_index.md`. Preserve the coverage surface (per-persona task content spot checks; detailed vs kickoff counts; empty/unknown persona warning paths).
- **`tests/test_generator.py::test_seed_tasks_created`** — assert that the starter bean exists and its tasks directory is populated when `seed_tasks` is enabled.
- **New test** — assert the bean.md contains `Status: Approved`, references `ai/context/project-charter.md` when that file is scaffolded, and falls back to a generic placeholder when the charter file is absent.
- Run `uv run pytest` and `uv run ruff check foundry_app/` — both must be clean.

## Acceptance Criteria

- [ ] All tests pass.
- [ ] Ruff is clean on `foundry_app/`.
- [ ] Starter-bean shape is covered by a test that would fail if the seeder regressed to writing `ai/tasks/_index.md`.
