# BEAN-033: Generation Progress Screen

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-033 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

When the user clicks "Generate" on the Review page, there is no visual feedback showing generation progress through the 6-stage pipeline (Scaffold, Compile, Copy Assets, Seed, Safety, Diff Report). Users need real-time progress indication and a summary of results.

## Goal

Implement a `GenerationProgressScreen` PySide6 widget that displays real-time progress through the generation pipeline stages, with a final summary showing generated files and warnings.

## Scope

### In Scope
- Implement `foundry_app/ui/screens/generation_progress.py`
- Display current pipeline stage with progress indicator
- Show elapsed time per stage
- Display log messages from generator
- Final summary: total files written, warnings, errors
- "Open Project" button to open output directory
- Connect to Review page's `generate_requested` signal
- Catppuccin Mocha theme styling
- Comprehensive test suite

### Out of Scope
- Estimated time remaining
- Cancel/abort generation mid-flight
- Manifest viewer (separate feature)

## Acceptance Criteria

- [x] `GenerationProgressScreen` widget exists and renders
- [x] Shows stage-by-stage progress through pipeline
- [x] Displays elapsed time and file counts
- [x] Shows warnings and errors clearly
- [x] Integrates with main window navigation (via signals)
- [x] All tests pass (`uv run pytest`) — 25 PySide6 tests
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement progress screen | Developer | — | Done |
| 2 | Implement stage status widget | Developer | — | Done |
| 3 | Write tests (25 tests) | Tech-QA | 1,2 | Done |

## Notes

- Depends on BEAN-032 (generator orchestrator), BEAN-017 (main window), both Done
- Review page has `generate_requested` signal (BEAN-024, Done)
- Services BEAN-029/030/031 should ideally be done first for complete pipeline

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

> Duration backfilled from git timestamps (commit→merge, 6s).
