# Task 02 — Developer: Rewrite Seeder to Emit Starter Bean

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 18:47 |
| **Completed** | 2026-04-17 18:48 |
| **Duration** | ~1m |

## Goal

Rewrite `seed_tasks()` in `foundry_app/services/seeder.py` so a freshly generated project enters the bean workflow through a starter bean, not through orphan `ai/tasks/` files.

## Inputs

- `foundry_app/services/seeder.py` (current implementation)
- `foundry_app/core/models.py` `CompositionSpec`, `StageResult`, `SeedMode`
- `ai/beans/_bean-template.md` (for bean.md structure)
- `ai/outputs/architect/BEAN-254-seeder-decision.md` (decision)

## Required Changes

1. **`foundry_app/services/seeder.py`**
   - Stop writing `ai/tasks/_index.md`.
   - Emit `ai/beans/BEAN-001-bootstrap/bean.md` with `Status: Approved`, `Priority: Medium`, `Category: App`, `Owner: (unassigned)`.
   - The bean's Problem Statement references `ai/context/project-charter.md` when that file exists in the generated project tree, otherwise uses a generic bootstrap placeholder.
   - Emit one task file per seeded task at `ai/beans/BEAN-001-bootstrap/tasks/NN-<owner>-<slug>.md`. The content mirrors the description string the seeder produces today. Task numbers are zero-padded and contiguous across personas.
   - Append (or create) `ai/beans/_index.md` with a row listing BEAN-001. Existing rows are preserved if the file already exists; the BEAN-001 row is not duplicated on re-run.
   - Empty-team case: if no personas are selected, still emit bean.md with an empty `tasks/` directory and a warning — preserves the existing no-personas warning shape.
   - All files written are returned in `StageResult.wrote`.

## Acceptance Criteria

- [ ] `ai/beans/BEAN-001-bootstrap/bean.md` exists with `Status: Approved`.
- [ ] Number of task files under `ai/beans/BEAN-001-bootstrap/tasks/` equals the number of tasks the old seeder would have written to the index table, for both `DETAILED` and `KICKOFF` modes.
- [ ] `ai/beans/_index.md` contains a BEAN-001 Backlog row.
- [ ] No write to `ai/tasks/_index.md`.
- [ ] When `ai/context/project-charter.md` is present, the bean's Problem Statement references it by path.
