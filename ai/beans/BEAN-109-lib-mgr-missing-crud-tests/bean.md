# BEAN-109: Library Manager — Missing CRUD Test Coverage

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-109 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-10 |
| **Started** | 2026-02-10 16:19 |
| **Completed** | 2026-02-10 16:24 |
| **Duration** | 5m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

An audit of Library Manager CRUD operations found that all 28 UI operations (7 entity types x 4 ops) are implemented and functional, but two operation/entity combinations lack dedicated test files: Skill Delete and Hook Create. This creates a gap in regression safety for these specific flows.

## Goal

Add test coverage for the two missing Library Manager CRUD combinations so that every entity type x operation pair has a dedicated test file following the established patterns.

## Scope

### In Scope
- Add `tests/test_skill_delete.py` — test skill deletion via the Library Manager (confirmation dialog, directory removal, tree refresh). Follow the pattern of `tests/test_hook_delete.py`.
- Add `tests/test_hook_create.py` — test hook creation via the Library Manager (new button, name input, starter content, tree selection). Follow the pattern of `tests/test_command_create.py`.

### Out of Scope
- Refactoring UI to use a service layer (current direct file I/O approach is fine)
- Expanding `library_indexer.py` to cover all 7 entity types
- Any UI changes — the UI already works correctly for both operations

## Acceptance Criteria

- [x] `tests/test_skill_delete.py` exists and tests skill deletion end-to-end (confirmation dialog, file/directory removal, tree update)
- [x] `tests/test_hook_create.py` exists and tests hook creation end-to-end (name input, starter content written, tree auto-select)
- [x] Both test files follow existing patterns from sibling test files
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create tests/test_skill_delete.py | Developer | — | Done |
| 2 | Create tests/test_hook_create.py | Developer | — | Done |
| 3 | Run all tests and lint | Tech-QA | 1, 2 | Done |

## Notes

- Identified during backlog refinement audit on 2026-02-10.
- All 28 UI operations confirmed working — this is test coverage only.
- `test_library_manager.py` (3,392 lines) has some integration-level coverage for these operations, but dedicated test files are the established pattern.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 5m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 80s).
