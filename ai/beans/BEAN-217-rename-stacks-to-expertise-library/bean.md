# BEAN-217: Rename stacks/ to expertise/ in Library

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-217 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | 2026-02-20 21:23 |
| **Completed** | 2026-02-20 21:23 |
| **Duration** | < 1m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

After the codebase rename (BEAN-216), the app expects an `expertise/` directory in the library, but the library still has `stacks/`. The directory needs to be renamed and all references in library documentation and example composition YAMLs updated.

## Goal

Rename the `ai-team-library/stacks/` directory to `ai-team-library/expertise/` and update all references in library docs, example YAMLs, and test assertions.

## Scope

### In Scope
- `git mv ai-team-library/stacks ai-team-library/expertise`
- Update `ai-team-library/README.md` references from "stacks" to "expertise"
- Update example composition YAMLs in `examples/` — change `stacks:` key to `expertise:`
- Update `tests/test_library_indexer.py` — rename `EXPECTED_STACKS` to `EXPECTED_EXPERTISE`, update `test_discovers_all_stacks` to `test_discovers_all_expertise`, etc.
- Update any references in `ai/context/project.md` or `CLAUDE.md` that mention the stacks directory

### Out of Scope
- Codebase rename (that's BEAN-216, must be done first)
- Category additions (BEAN-218-220)
- Renaming individual expertise file contents (they reference their own domain, not "stack")

## Acceptance Criteria

- [ ] `ai-team-library/stacks/` directory no longer exists
- [ ] `ai-team-library/expertise/` directory contains all 39 subdirectories
- [ ] Example YAML files use `expertise:` key instead of `stacks:`
- [ ] Library README updated to reference expertise instead of stacks
- [ ] `EXPECTED_STACKS` renamed to `EXPECTED_EXPERTISE` in test_library_indexer.py
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Depends on BEAN-216 (codebase rename). The app code must already expect `expertise/` before the library directory is renamed, otherwise the indexer will find nothing.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
