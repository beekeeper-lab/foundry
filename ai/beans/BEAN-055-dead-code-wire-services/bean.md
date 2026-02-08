# BEAN-055: Wire Real Services & Clean Up Dead Code

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-055 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-08 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The generator pipeline (`generator.py`) still routes through five `_stub_*` wrapper functions from the early scaffolding phase. Two of these (`_stub_compile` and `_stub_copy_assets`) are genuine stubs that log "not yet implemented" even though the real services (`compiler.py`, `asset_copier.py`) exist and are fully implemented. Three others call real implementations but retain misleading `_stub_` names. Additionally, the `StackOverrides` model is defined but never used, and `PersonaInfo.id` is missing the `min_length=1` constraint that all other ID fields have.

## Goal

Wire the pipeline to call real services directly, remove misleading stub wrappers, and clean up unused/inconsistent model definitions.

## Scope

### In Scope
- Replace `_stub_compile()` call in `_run_pipeline()` with direct call to `compile_project()`
- Replace `_stub_copy_assets()` call with direct call to `copy_assets()`
- Remove or rename `_stub_seed_tasks`, `_stub_write_safety`, `_stub_diff_report` — either inline or rename to drop `_stub_` prefix
- Remove or annotate `StackOverrides` model
- Add `min_length=1` to `PersonaInfo.id`

### Out of Scope
- Refactoring the pipeline architecture itself
- Adding new pipeline stages
- Changes to the real service implementations

## Acceptance Criteria

- [ ] `_run_pipeline()` calls `compile_project()` from `compiler.py` directly (not a stub)
- [ ] `_run_pipeline()` calls `copy_assets()` from `asset_copier.py` directly (not a stub)
- [ ] No functions named `_stub_*` remain in `generator.py`
- [ ] No log messages say "not yet implemented" for implemented services
- [ ] `StackOverrides` is either removed or marked with a comment explaining it's reserved
- [ ] `PersonaInfo.id` has `Field(..., min_length=1)`
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Wire compile_project() into _run_pipeline() | | | Pending |
| 2 | Wire copy_assets() into _run_pipeline() | | | Pending |
| 3 | Remove _stub_ wrappers, inline or rename remaining helpers | | 1, 2 | Pending |
| 4 | Remove or annotate StackOverrides | | | Pending |
| 5 | Add min_length=1 to PersonaInfo.id | | | Pending |
| 6 | Update generator tests for new direct calls | | 1, 2, 3 | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

### Current pipeline (generator.py _run_pipeline):
```python
stages["compile"] = _stub_compile(spec, library, output_dir)      # Logs "not yet implemented"
stages["copy_assets"] = _stub_copy_assets(spec, library, output_dir)  # Logs "not yet implemented"
stages["seed_tasks"] = _stub_seed_tasks(spec, output_dir)          # Calls real seed_tasks()
stages["safety"] = _stub_write_safety(spec, output_dir)            # Calls real write_safety()
stages["diff_report"] = _stub_diff_report(spec, output_dir, plan)  # Calls real write_diff_report()
```

### Target pipeline:
```python
from foundry_app.services.compiler import compile_project
from foundry_app.services.asset_copier import copy_assets

stages["compile"] = compile_project(spec, library, output_dir)
stages["copy_assets"] = copy_assets(spec, library, library_path, output_dir)
stages["seed_tasks"] = seed_tasks(spec, output_dir)
stages["safety"] = write_safety(spec, output_dir)
if spec.generation.write_diff_report:
    plan = plan or OverlayPlan()
    stages["diff_report"] = write_diff_report(plan, output_dir)
```

Note: `compile_project()` and `copy_assets()` have different signatures than the stubs — verify the actual function signatures before wiring.
