# BEAN-199: Product Owner / Product Manager Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-199 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:48 |
| **Completed** | 2026-02-20 19:53 |
| **Duration** | 5m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a product owner / product manager persona. Add product-manager persona to ai-team-library. Product vision, roadmap ownership, prioritization (RICE/MoSCoW), stakeholder communication, go-to-market strategy, feature scoping. Works upstream from BA persona. Pairs with Product Strategy stack.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add product-manager persona to ai-team-library. Product vision, roadmap ownership, prioritization (RICE/MoSCoW), stakeholder communication, go-to-market strategy, feature scoping. Works upstream from BA persona. Pairs with Product Strategy stack.

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
| 1 | Create product-owner persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | Done |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | 1 | Done |
| 3 | Run tests and lint verification | Tech-QA | 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #74.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4b0bdba36cb7b43feaf |
| **Card Name** | Product Owner / Product Manager Persona |
| **Card URL** | https://trello.com/c/RwCmLhSI |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create product-owner persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | — | — | — |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | — | — | — | — |
| 3 | Run tests and lint verification | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 5m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |