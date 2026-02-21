# BEAN-202: Financial Operations / Budget Officer Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-202 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:45 |
| **Completed** | 2026-02-20 19:50 |
| **Duration** | 5m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a financial operations / budget officer persona. Add finops persona to ai-team-library. Cost estimation and budgeting, licensing compliance and procurement, resource allocation decisions, ROI tracking, cloud spend optimization, showback/chargeback reporting. Pairs with FinOps stack.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add finops persona to ai-team-library. Cost estimation and budgeting, licensing compliance and procurement, resource allocation decisions, ROI tracking, cloud spend optimization, showback/chargeback reporting. Pairs with FinOps stack.

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
| 1 | Create persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | Done |
| 2 | Update EXPECTED_PERSONAS in test_library_indexer.py | Developer | 1 | Done |
| 3 | Run tests and lint | Tech-QA | 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #77.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4b4a2e8a1205d4dcdcb |
| **Card Name** | Financial Operations / Budget Officer Persona |
| **Card URL** | https://trello.com/c/MyWOHWA7 |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | — | — | — |
| 2 | Update EXPECTED_PERSONAS in test_library_indexer.py | Developer | — | — | — | — |
| 3 | Run tests and lint | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 5m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |