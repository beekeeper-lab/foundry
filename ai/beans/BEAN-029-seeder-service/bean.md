# BEAN-029: Seeder Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-029 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The generator orchestrator calls `_stub_seed_tasks()` as a placeholder. When `spec.generation.seed_tasks` is True, the system should generate an initial `ai/tasks/_index.md` file with starter tasks based on the composition spec's selected personas, stacks, and architecture patterns. Without this service, generated projects have no initial task seeding.

## Goal

Implement a `SeederService` that generates starter task files in generated projects based on the composition spec. Support two seed modes: DETAILED (full task descriptions) and KICKOFF (minimal bootstrap).

## Scope

### In Scope
- Implement `foundry_app/services/seeder.py`
- Function: `seed_tasks(spec: CompositionSpec, output_dir: Path) -> StageResult`
- Support `SeedMode.DETAILED` and `SeedMode.KICKOFF` modes
- Generate tasks based on selected personas and stacks
- Handle missing personas gracefully
- Return `StageResult` with `wrote` list and `warnings`
- Replace `_stub_seed_tasks()` in generator with real call
- Comprehensive test suite

### Out of Scope
- Template customization UI
- Per-persona task template library

## Acceptance Criteria

- [x] `foundry_app/services/seeder.py` exists with `seed_tasks()` function
- [x] Supports both DETAILED and KICKOFF seed modes
- [x] Generates deterministic, ordered task output
- [x] Gracefully handles specs with no personas selected
- [x] Generator stub replaced with real service call
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement seeder service | Developer | — | Done |
| 2 | Integrate with generator | Developer | 1 | Done |
| 3 | Write tests (23 tests) | Tech-QA | 1 | Done |

## Notes

- Models already exist: `SeedMode` enum in `core/models.py`
- Generator stub at `generator.py:49-52`
- Depends on BEAN-016 (models) and BEAN-032 (generator orchestrator), both Done

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

> Duration backfilled from git timestamps (commit→merge, 9s).
