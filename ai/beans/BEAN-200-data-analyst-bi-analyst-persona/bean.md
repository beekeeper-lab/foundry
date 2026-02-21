# BEAN-200: Data Analyst / BI Analyst Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-200 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:41 |
| **Completed** | 2026-02-20 19:45 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a data analyst / bi analyst persona. Add data-analyst persona to ai-team-library. KPI definition and dashboarding, user behavior analytics, A/B testing design, data-driven decision support, metrics tracking and reporting. Pairs with Business Intelligence stack.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add data-analyst persona to ai-team-library. KPI definition and dashboarding, user behavior analytics, A/B testing design, data-driven decision support, metrics tracking and reporting. Pairs with Business Intelligence stack.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Persona directory created in `ai-team-library/personas/` with persona.md, outputs.md, prompts.md, templates/
- [x] persona.md follows standardized format with mission, capabilities, boundaries
- [x] outputs.md defines deliverable types and formats
- [x] prompts.md provides reusable prompt templates
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create data-analyst persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | Done |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | 1 | Done |
| 3 | Run tests and lint, verify acceptance criteria | Tech-QA | 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #75.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4b2439b1432b4cb98ef |
| **Card Name** | Data Analyst / BI Analyst Persona |
| **Card URL** | https://trello.com/c/QWSUp3zb |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create data-analyst persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | — | — | — |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | — | — | — | — |
| 3 | Run tests and lint, verify acceptance criteria | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |