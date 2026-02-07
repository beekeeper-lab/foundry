# BEAN-001: Beans Seed Mode — Implementation Notes

**Author:** Developer | **Date:** 2026-02-07 | **Bean:** BEAN-001

## Changes

### `foundry_app/core/models.py`
- Updated `GenerationOptions.seed_mode` comment: `detailed | kickoff | beans`

### `foundry_app/services/seeder.py`
- Added `beans` dispatch in `seed_tasks()` before the detailed fallback
- Added `_seed_beans()` function that generates:
  - `_index.md` — backlog index with project name, status key, empty backlog table
  - `_bean-template.md` — complete bean template with all required sections

### `foundry_app/services/generator.py`
- When `seed_mode == "beans"`, passes `project_dir / "ai" / "beans"` instead of `project_dir / "ai" / "tasks"` to the seeder

### `tests/test_seeder.py`
- 10 new tests (tests 11-20):
  - `test_beans_mode_creates_index_file`
  - `test_beans_mode_creates_template_file`
  - `test_beans_mode_index_has_status_key`
  - `test_beans_mode_index_has_backlog_table`
  - `test_beans_mode_index_includes_project_name`
  - `test_beans_mode_template_has_required_sections`
  - `test_beans_mode_returns_stage_result_with_both_files`
  - `test_beans_mode_does_not_create_seeded_tasks`
  - `test_detailed_mode_still_works`
  - `test_kickoff_mode_still_works`

## Design Decisions

- The `_seed_beans()` function follows the same pattern as `_seed_kickoff()` — receives the output directory and StageResult, writes files, returns result
- The generator determines the output directory (`ai/beans/` vs `ai/tasks/`) based on seed mode — keeps the seeder directory-agnostic
- The generated index and template match the reference files in Foundry's own `ai/beans/` directory
- No initial bean population — the template and commands (`/new-bean`) handle bean creation

## Test Results

- **Total tests:** 333 (323 + 10 new)
- **Pass:** 333
- **Fail:** 0
- **Lint:** 21 pre-existing E501, 0 new issues
