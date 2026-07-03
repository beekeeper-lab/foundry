# BEAN-254: Bootstrap Bean for Seeded Tasks

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-254 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 18:45 |
| **Completed** | 2026-04-17 18:51 |
| **Duration** | 6m (corrected 2026-07) |
| **Owner** | worker-bean-254 |
| **Category** | App |

## Problem Statement

External audit (2026-04-17): "Seeded tasks are orphaned. `ai/tasks/_index.md` has 27 tasks assigned to roles, but `ai/beans/_index.md` is empty and tasks aren't linked to beans. The bean workflow is the unit of work, so these tasks live outside the system that tracks them."

Today the Seeder produces per-persona tasks directly into `ai/tasks/<persona>/` and writes `_index.md`. The bean workflow is the declared unit of work (per `ai/context/bean-workflow.md`), but seeded tasks skip it entirely. A Team Lead's first action when opening a generated project is meant to be *picking a bean* — but there is no starter bean, and the 27 orphan tasks have no home in the bean-tracking system.

## Goal

Seeded work enters the project through the bean workflow, not around it. A freshly generated project contains **one starter bean** (e.g., `BEAN-001-bootstrap`) that owns whatever tasks the Seeder produces. `ai/tasks/` exists but is empty, or is removed entirely in favor of `ai/beans/BEAN-001-bootstrap/tasks/`.

## Scope

### In Scope
- Decide: does the Seeder still produce `ai/tasks/<persona>/` files, or are those tasks created inside a starter bean's `tasks/` directory instead?
- Implement the chosen direction in `foundry_app/services/seeder.py` and the pipeline.
- If a starter bean is emitted: it should be `Approved` (so the Team Lead can pick it immediately), reference the project charter (BEAN-252), and have a bean.md stub that names the bootstrap goals.
- Tests asserting a starter bean exists when seeding is enabled, and that its task count equals what the Seeder would have produced.
- Update `ai/context/bean-workflow.md` if the seeding semantics change.

### Out of Scope
- Redesigning the Seeder's task-mapping rules (that's upstream content).
- Creating starter beans for every stack/expertise combination (one generic starter is sufficient).
- Changing seed mode taxonomy (`SeedMode.DETAILED` etc.).

## Acceptance Criteria

- [x] When `spec.generation.seed_tasks` is true, the generator emits `ai/beans/BEAN-001-bootstrap/bean.md` with status `Approved` and its `tasks/` directory populated with the same set of tasks the Seeder produces today.
- [x] `ai/tasks/` is either empty (no orphan tasks) or removed entirely — the audit's complaint is resolved.
- [x] `ai/beans/_index.md` lists BEAN-001.
- [x] The starter bean's `Problem Statement` references `ai/context/project-charter.md` (BEAN-252) if that bean is Done, or falls back to a generic "bootstrap" placeholder.
- [x] Existing seeder tests updated; new test asserts the starter bean exists and contains the expected task files.
- [x] All tests pass (`uv run pytest`).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

> Skipped: BA (default — goal is clear from audit).

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Decide seeder-to-bean task location (ADR) | architect | — | Done |
| 2 | Rewrite seeder to emit starter bean + tasks | developer | 1 | Done |
| 3 | Update/add seeder and generator tests | tech-qa | 2 | Done |

## Changes

| File | Lines |
|------|-------|
| `foundry_app/services/seeder.py` | full rewrite: emit BEAN-001-bootstrap bean + tasks + backlog index |
| `tests/test_seeder.py` | full rewrite: 40 tests against new starter-bean output shape |
| `tests/test_generator.py` | `test_seed_tasks_created` now asserts starter-bean shape |
| `ai/context/decisions.md` | +ADR-004 |
| `ai/outputs/architect/BEAN-254-seeder-decision.md` | new |
| `ai/outputs/tech-qa/BEAN-254-verification.md` | new |

## Notes

**Depends on.** BEAN-252 (charter) is softly related — the starter bean's stated goals should reference the charter if it exists. Not a hard dependency.

**Architect participation.** The pipeline change touches the seeder/scaffolder boundary. Architect may be warranted for the task-location decision.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Decide seeder-to-bean task location (ADR) | architect | — | — | — | — |
| 2 | Rewrite seeder to emit starter bean + tasks | developer | — | — | — | — |
| 3 | Update/add seeder and generator tests | tech-qa | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 1269h 43m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |