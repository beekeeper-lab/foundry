# BEAN-028: Asset Copier Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-028 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The generation pipeline needs a service to copy reusable library assets (persona templates, commands, hooks) into generated projects. This is stage 4 of the 6-stage pipeline: Validate → Scaffold → Compile → **Copy Assets** → Seed → Write Manifest.

## Goal

Implement `foundry_app/services/asset_copier.py` that copies library assets into the scaffolded project directory, returning a `StageResult` with all copied file paths.

## Scope

### In Scope
- Copy persona templates when `include_templates=True`
- Copy Claude commands from library to `.claude/commands/`
- Copy Claude hooks from library to `.claude/hooks/`
- Overlay-safe behavior: skip existing identical files, warn on conflicts
- Return `StageResult` with `wrote` and `warnings` lists
- Comprehensive test suite

### Out of Scope
- Skills copying (deferred to BEAN-027 Compiler coordination)
- Generator orchestrator integration (BEAN-032)
- CLI invocation (BEAN-034)

## Acceptance Criteria

- [x] `asset_copier.py` exists at `foundry_app/services/asset_copier.py`
- [x] Copies persona templates from `library/personas/<id>/templates/` when `include_templates=True`
- [x] Skips template copying when `include_templates=False`
- [x] Copies all commands from `library/claude/commands/` to `.claude/commands/`
- [x] Copies all hooks from `library/claude/hooks/` to `.claude/hooks/`
- [x] Returns `StageResult` with `wrote` listing all copied files as relative paths
- [x] Handles missing/empty template directories gracefully with warnings
- [x] Overlay-safe: skips existing identical files, warns on conflicts
- [x] Unit tests cover happy path, edge cases, and overlay behavior (27 tests)
- [x] All tests pass (`uv run pytest` — 419 total)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design asset copier interface and review models | architect | | Done |
| 2 | Implement asset_copier.py service | developer | 1 | Done |
| 3 | Write comprehensive test suite | tech-qa | 2 | Done |
| 4 | Integration verification and lint check | tech-qa | 3 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on: BEAN-016 (models), BEAN-018 (library indexer), BEAN-026 (scaffold)
- Used by: BEAN-032 (Generator Orchestrator)
- Must follow overlay-safe pattern from ADR-001

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 24s).
