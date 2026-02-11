# BEAN-032: Generator Orchestrator & Overlay

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-032 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The Foundry application has individual service modules (scaffold, validator, library indexer) but no orchestrator to coordinate them into a complete generation pipeline. Without an orchestrator, the UI and CLI have no single entry point for generating a Claude Code project. Additionally, the overlay mode (re-generation over an existing project) requires a two-phase approach that individual services don't manage.

## Goal

Implement a `generate_project()` function that orchestrates the full generation pipeline: validation, scaffolding, compilation, asset copying, seeding, safety writing, and manifest creation. Support both standard and overlay modes. This is the central service that ties all other services together.

## Scope

### In Scope
- Generator orchestrator function (`foundry_app/services/generator.py`)
- Pipeline stage execution in correct order
- Standard generation mode (write directly to output)
- Overlay mode (two-phase: generate to temp, then compare and apply)
- Dry-run support (plan overlay but don't apply)
- GenerationManifest assembly from per-stage results
- Stub callouts for not-yet-implemented services (compiler, asset_copier, seeder, safety_writer, diff_reporter)
- Library version detection (git short-hash)
- Comprehensive test suite

### Out of Scope
- Implementation of individual pipeline stages beyond scaffold/validator (those are separate beans)
- UI integration (BEAN-033 handles the progress screen)
- CLI wiring (BEAN-034)
- Actual compilation, asset copying, seeding, safety writing logic

## Acceptance Criteria

- [x] `generate_project()` function exists in `foundry_app/services/generator.py`
- [x] Runs validation and stops on errors (returns ValidationResult)
- [x] Calls scaffold_project to create directory skeleton
- [x] Calls stub functions for compiler, asset_copier, seeder, safety_writer, diff_reporter
- [x] Assembles and returns a GenerationManifest with all stage results
- [x] Overlay mode: generates to temp dir, compares with target, returns OverlayPlan
- [x] Overlay mode with apply: applies the plan to target directory
- [x] Dry-run mode: returns OverlayPlan without applying
- [x] Force mode: skips validation errors
- [x] Library version detection via git hash
- [x] All tests pass (`uv run pytest`) — 451 tests, 59 new
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement generator orchestrator service | developer | — | Done |
| 2 | Implement overlay compare and apply logic | developer | 1 | Done |
| 3 | Write comprehensive test suite | tech-qa | 1, 2 | Done |
| 4 | Lint check and final verification | developer | 3 | Done |

## Notes

- Stub functions for unimplemented services should return empty StageResult objects
- The orchestrator follows the same functional, stateless pattern as other services
- Pipeline order: validate → scaffold → compile → copy assets → seed → safety → diff report → manifest

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

> Duration backfilled from git timestamps (commit→merge, 19s).
