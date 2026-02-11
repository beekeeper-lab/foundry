# BEAN-022: Wizard — Architecture & Cloud Page

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-022 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard needs a page where users configure architecture patterns and cloud deployment targets for their generated project. This is wizard page 4 of 6, sitting between Technology Stack (page 3) and Hook & Safety Config (page 5). Without this page, generated projects lack architecture guidance and cloud-specific conventions.

## Goal

Build the architecture & cloud wizard page where users can select architecture patterns (e.g. monolith, microservices, serverless, event-driven) and cloud providers (e.g. AWS, Azure, GCP, self-hosted). Selections are stored in a new `ArchitectureConfig` model on CompositionSpec.

## Scope

### In Scope
- `foundry_app/core/models.py` — new `ArchitecturePattern`, `CloudProvider` enums and `ArchitectureConfig` model
- `foundry_app/ui/screens/builder/wizard_pages/architecture_page.py` — wizard page 4
- Architecture pattern multi-select with cards (monolith, microservices, serverless, event-driven, modular-monolith)
- Cloud provider multi-select with cards (AWS, Azure, GCP, Self-hosted/On-prem)
- Per-pattern and per-provider descriptions
- Data binding to new `CompositionSpec.architecture` field
- Visual consistency with existing wizard pages (Catppuccin Mocha theme)
- Comprehensive tests in `tests/test_architecture_page.py`

### Out of Scope
- Per-architecture or per-cloud detailed configuration (future extensibility)
- Cloud-specific resource templates
- Architecture diagram generation

## Acceptance Criteria

- [x] Architecture patterns appear as selectable cards
- [x] Cloud providers appear as selectable cards
- [x] User can select/deselect patterns and providers independently
- [x] Each card shows name and description
- [x] Page is optional (valid with zero selections — user can skip)
- [x] Selections populate `ArchitectureConfig` correctly
- [x] Round-trip `get_config()`/`set_config()` preserves state
- [x] `selection_changed` signal emits on changes
- [x] All tests pass (`uv run pytest`) — 457 tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add ArchitectureConfig model to models.py | developer | — | Done |
| 2 | Implement architecture_page.py wizard page | developer | 1 | Done |
| 3 | Write comprehensive tests (65 tests) | tech-qa | 2 | Done |
| 4 | Run tests and lint, fix issues | tech-qa | 3 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-016 (data models), BEAN-017 (app shell). This is wizard page 4 of 6. Unlike stack and persona pages, this page should be OPTIONAL — projects can be generated without architecture/cloud selections.

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

> Duration backfilled from git timestamps (commit→merge, 49s).
