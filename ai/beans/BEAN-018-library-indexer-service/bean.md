# BEAN-018: Library Indexer Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-018 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard pages need to present available personas, stacks, hooks, and templates from the library. Without a service that scans the library directory and builds a structured index, each UI screen would need its own ad-hoc file scanning logic.

## Goal

Rebuild the library indexer service that scans `ai-team-library/` and produces a LibraryIndex with all available personas, stacks, templates, hook packs, and workflows.

## Scope

### In Scope
- `foundry_app/services/library_indexer.py`
- `build_library_index(library_root)` function
- Scan personas directory: extract persona ID, name, available files (persona.md, outputs.md, prompts.md, templates/)
- Scan stacks directory: extract stack ID, name, available convention files
- Scan hooks directory: extract hook pack ID, name, description
- Scan templates across all personas
- Return structured LibraryIndex model (from BEAN-016)
- Unit tests

### Out of Scope
- UI for displaying the index (that's BEAN-020, BEAN-021, etc.)
- Modifying library content
- Stack combo configuration (that's part of BEAN-021)

## Acceptance Criteria

- [x] `build_library_index()` returns a LibraryIndex with all 13 personas
- [x] All 11 stacks are indexed with their convention files
- [x] Hook packs are indexed with IDs and descriptions
- [x] Templates are indexed per-persona
- [x] Function handles missing directories gracefully (warnings, not crashes)
- [x] Unit tests verify indexing against the real `ai-team-library/`
- [x] All tests pass (`uv run pytest`) — 134 pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement library_indexer.py | developer | — | Done |
| 2 | Write unit tests | tech-qa | 1 | Done |

## Notes

Depends on BEAN-016 (LibraryIndex model). Used by BEAN-020 (Persona Selection), BEAN-021 (Tech Stack), and multiple pipeline services.
