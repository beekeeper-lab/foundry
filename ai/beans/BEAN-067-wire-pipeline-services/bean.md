# BEAN-067: Wire Compiler & Asset Copier into Pipeline

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-067 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The compiler service (`compiler.py`) and asset copier service (`asset_copier.py`) are fully implemented but never called. In `generator.py`, the pipeline calls `_stub_compile()` and `_stub_copy_assets()` which return empty `StageResult` objects. This means generated projects get:

- An empty `CLAUDE.md` (no compiled persona+stack content)
- Empty `.claude/commands/` directory (commands never copied from library)
- Empty `.claude/hooks/` directory (hooks never copied from library)
- No persona templates copied to `ai/outputs/`

The services exist and are tested — they just need to be imported and called with the correct signatures.

## Goal

Replace the two stub functions in `generator.py` with calls to the real `compile_project()` and `copy_assets()` functions. After this bean, the generation pipeline produces a fully populated project with compiled CLAUDE.md, copied commands, copied hooks, and persona templates.

## Scope

### In Scope
- Import `compile_project` from `foundry_app.services.compiler` in `generator.py`
- Import `copy_assets` from `foundry_app.services.asset_copier` in `generator.py`
- Replace `_stub_compile()` call with `compile_project(spec, library, library_root, output_dir)`
- Replace `_stub_copy_assets()` call with `copy_assets(spec, library, library_root, output_dir)`
- Pass `library_root` path through to `_run_pipeline()` (currently only receives `library: LibraryIndex`)
- Update tests to verify real services are called
- Verify generated project has populated CLAUDE.md, commands, hooks

### Out of Scope
- Changes to compiler.py or asset_copier.py logic
- New asset types (skills, MCP — those are separate beans)
- Agent file format changes

## Acceptance Criteria

- [ ] `generator.py` imports and calls `compile_project()` instead of `_stub_compile()`
- [ ] `generator.py` imports and calls `copy_assets()` instead of `_stub_copy_assets()`
- [ ] `_run_pipeline()` signature updated to accept `library_root: Path`
- [ ] Generated project has populated `CLAUDE.md` with persona and stack sections
- [ ] Generated project has `.claude/commands/` populated with library commands
- [ ] Generated project has `.claude/hooks/` populated with library hook files
- [ ] Persona templates copied to `ai/outputs/<persona>/` when `include_templates=True`
- [ ] Existing tests still pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- `compile_project()` signature: `(spec, library_index, library_root, output_dir) -> StageResult`
- `copy_assets()` signature: `(spec, library_index, library_root, output_dir) -> StageResult`
- Both need `library_root` as a `Path`, which `_run_pipeline()` doesn't currently receive — need to thread it through from `generate_project()`
- The stub functions `_stub_compile` and `_stub_copy_assets` can be deleted after wiring
- This is a quick win that unblocks BEAN-068 (Agent Writer) and BEAN-071 (Skills Copier)
