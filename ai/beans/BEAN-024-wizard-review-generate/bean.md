# BEAN-024: Wizard — Review & Generate Page

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-024 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard needs a final review page where users can see a complete summary of all their configuration choices before triggering generation. Without this, users would generate projects blind — unable to verify their selections or catch mistakes before output is produced.

## Goal

Build the final wizard page: a read-only summary screen that displays all composition spec data (project identity, selected personas, selected stacks, hooks/safety config, generation options) and provides a "Generate" action to proceed.

## Scope

### In Scope
- `foundry_app/ui/screens/builder/wizard_pages/review_page.py`
- Read-only summary sections for each CompositionSpec area:
  - Project identity (name, slug, output path)
  - Team composition (selected personas with config)
  - Technology stacks (selected stacks in order)
  - Hooks & safety configuration
  - Generation options
- `set_composition_spec(spec)` method to populate from full spec
- `generate_requested` signal for triggering generation
- Collapsible/grouped sections for organized display
- Visual consistency with existing wizard pages (Catppuccin Mocha theme)

### Out of Scope
- Actual generation logic (BEAN-032)
- Progress bar/generation screen (BEAN-033)
- Inline editing from the review page
- Export functionality (BEAN-035)

## Acceptance Criteria

- [x] Page displays project identity summary (name, slug, output path)
- [x] Page displays selected personas with per-persona config
- [x] Page displays selected stacks in compilation order
- [x] Page displays hooks posture and enabled packs
- [x] Page displays generation options (seed tasks, manifest, diff report)
- [x] Page displays safety config summary when present
- [x] `set_composition_spec()` populates all sections correctly
- [x] `generate_requested` signal emits when generate button clicked
- [x] Empty/default sections handled gracefully (no crash on empty lists)
- [x] All tests pass (`uv run pytest`) — 364 tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design and implement review page | developer | — | Done |
| 2 | Write comprehensive tests (68 tests) | tech-qa | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-016 (data models), BEAN-017 (app shell). This is wizard page 6 of 6 — the final page before generation. Pages 4 and 5 (Architecture & Cloud, Hook & Safety) are separate beans; this page should display whatever data is present in the CompositionSpec regardless.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 2m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 2m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 179s).
