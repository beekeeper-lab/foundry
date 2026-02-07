# Task 01: Implement Beans Seed Mode

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Add a `beans` seed mode to the seeder that generates `ai/beans/` directory structure with `_index.md` and `_bean-template.md`, matching the structure defined in `ai/context/bean-workflow.md`.

## Inputs

- `ai/beans/BEAN-001-backlog-seeding/bean.md` — acceptance criteria
- `ai/context/bean-workflow.md` — reference structure
- `ai/beans/_index.md` — reference index format
- `ai/beans/_bean-template.md` — reference template format
- `foundry_app/services/seeder.py` — existing seeder with `detailed` and `kickoff` modes
- `foundry_app/services/generator.py` — pipeline orchestrator that calls seeder
- `foundry_app/core/models.py` — `GenerationOptions.seed_mode`

## Implementation

1. **`foundry_app/core/models.py`**: Update `seed_mode` comment to include `beans`
2. **`foundry_app/services/seeder.py`**: Add `_seed_beans()` function that generates:
   - `_index.md` — backlog index with status key, empty backlog table, project name in header
   - `_bean-template.md` — bean template (matches the existing reference)
3. **`foundry_app/services/seeder.py`**: Add `beans` dispatch in `seed_tasks()` (before detailed fallback)
4. **`foundry_app/services/generator.py`**: When `seed_mode == "beans"`, pass `project_dir / "ai" / "beans"` instead of `project_dir / "ai" / "tasks"`
5. **`tests/test_seeder.py`**: Add tests for the new mode

## Tests to Add

- `test_beans_mode_creates_index_file` — `_index.md` exists
- `test_beans_mode_creates_template_file` — `_bean-template.md` exists
- `test_beans_mode_index_has_status_key` — index contains status table
- `test_beans_mode_index_has_backlog_table` — index contains backlog header
- `test_beans_mode_template_has_required_sections` — template has Problem Statement, Goal, Scope, AC, Tasks
- `test_beans_mode_returns_stage_result` — StageResult lists both files
- `test_beans_mode_does_not_create_seeded_tasks` — no `seeded-tasks.md`
- `test_detailed_mode_unaffected_by_beans` — existing detailed mode still works
- `test_kickoff_mode_unaffected_by_beans` — existing kickoff mode still works

## Acceptance Criteria

- [ ] `seed_mode: beans` dispatches to `_seed_beans()`
- [ ] Generated `_index.md` matches reference format
- [ ] Generated `_bean-template.md` matches reference format
- [ ] Generator passes correct directory for beans mode
- [ ] Existing `detailed` and `kickoff` modes unaffected
- [ ] All new tests pass
- [ ] `uv run pytest` — all tests pass
- [ ] `uv run ruff check foundry_app/` — lint clean

## Definition of Done

All acceptance criteria met. Implementation notes written to `ai/outputs/developer/bean-001-implementation-notes.md`.
