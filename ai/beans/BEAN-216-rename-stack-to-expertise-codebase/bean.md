# BEAN-216: Rename Stack to Expertise in Codebase

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-216 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | 2026-02-20 20:50 |
| **Completed** | 2026-02-20 21:07 |
| **Duration** | 17m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The library has grown from 11 technology-focused stacks to 39 items spanning languages, compliance frameworks, and business practices. The term "Technology Stack" no longer fits items like "change-management" or "sox-compliance." The concept is being renamed from "Stack" to "Expertise" across the entire codebase: models, services, UI, composition I/O, and tests.

## Goal

Perform a full mechanical rename of all Stack-related identifiers and UI text to use "Expertise" instead. After this bean, there should be zero references to "Stack" in the codebase (except in git history and this bean file).

## Scope

### In Scope
- **Models** (`foundry_app/core/models.py`): `StackInfo` → `ExpertiseInfo`, `StackSelection` → `ExpertiseSelection`, `stacks` field → `expertise` in `CompositionSpec` and `LibraryIndex`, `stack_by_id()` → `expertise_by_id()`
- **Services** (`foundry_app/services/`): `_scan_stacks()` → `_scan_expertise()` in library_indexer.py; update references in compiler.py, validator.py, generator.py, scaffold.py, seeder.py, asset_copier.py
- **I/O** (`foundry_app/io/composition_io.py`): Update YAML key parsing from `stacks` to `expertise`
- **UI** (`foundry_app/ui/`): Rename `stack_page.py` → `expertise_page.py`, `StackSelectionPage` → `ExpertiseSelectionPage`, `StackCard` → `ExpertiseCard`, `STACK_DESCRIPTIONS` → `EXPERTISE_DESCRIPTIONS`, heading "Select Technology Stacks" → "Select Expertise", update builder_screen.py and review_page.py references
- **Tests**: Update all test files to use new names
- **UI display text**: "Technology Stacks" → "Expertise" everywhere in user-facing strings

### Out of Scope
- Renaming the `ai-team-library/stacks/` directory (that's BEAN-217)
- Adding category fields or grouping (those are BEAN-218, 219, 220)
- Changing the composition YAML example files (BEAN-217 handles that)
- Backward compatibility shims or aliases

## Acceptance Criteria

- [ ] No Python identifier contains "Stack" or "stack" (except imports from external libraries)
- [ ] No user-facing UI string contains "Stack" or "Technology Stack"
- [ ] `StackInfo` renamed to `ExpertiseInfo` with identical fields
- [ ] `StackSelection` renamed to `ExpertiseSelection` with identical fields
- [ ] `CompositionSpec.stacks` renamed to `CompositionSpec.expertise`
- [ ] `LibraryIndex.stacks` renamed to `LibraryIndex.expertise`
- [ ] `stack_page.py` renamed to `expertise_page.py`
- [ ] YAML composition files still parse correctly (key changes from `stacks:` to `expertise:`)
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

This is a large mechanical rename that crosses all system boundaries (models, services, UI, I/O). It is kept as one bean because splitting it by layer would leave the codebase in a broken state between beans. Every change is a straightforward find-and-replace.

Must be completed before BEAN-217 (library directory rename), BEAN-218-220 (category work).

**Molecularity exception:** This bean touches more than 5 files because the rename must be atomic across the codebase. The alternative (partial renames with backward-compat aliases) adds complexity and goes against the project's "no backwards-compat hacks" rule.

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
| **Total Duration** | 17m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
