# BEAN-201: Customer Success / Solutions Engineer Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-201 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:43 |
| **Completed** | 2026-02-20 19:48 |
| **Duration** | <1 hr |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a customer success / solutions engineer persona. Add customer-success persona to ai-team-library. Customer onboarding and enablement, implementation support and consulting, feedback collection for product iteration, case study development, post-launch support. Pairs with Customer Enablement stack.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add customer-success persona to ai-team-library. Customer onboarding and enablement, implementation support and consulting, feedback collection for product iteration, case study development, post-launch support. Pairs with Customer Enablement stack.

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
| 1 | Create persona directory and persona.md | Developer | — | Done |
| 2 | Create outputs.md with deliverable definitions | Developer | 1 | Done |
| 3 | Create prompts.md with prompt fragments | Developer | 1 | Done |
| 4 | Create templates/ with reusable templates | Developer | 1 | Done |
| 5 | Update EXPECTED_PERSONAS in test_library_indexer.py | Developer | 1 | Done |
| 6 | Run tests and lint verification | Tech-QA | 1–5 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #76.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4b39c62145e99c9c5c3 |
| **Card Name** | Customer Success / Solutions Engineer Persona |
| **Card URL** | https://trello.com/c/Xsc1yAag |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create persona directory and persona.md | Developer | — | — | — | — |
| 2 | Create outputs.md with deliverable definitions | Developer | — | — | — | — |
| 3 | Create prompts.md with prompt fragments | Developer | — | — | — | — |
| 4 | Create templates/ with reusable templates | Developer | — | — | — | — |
| 5 | Update EXPECTED_PERSONAS in test_library_indexer.py | Developer | — | — | — | — |
| 6 | Run tests and lint verification | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 6 |
| **Total Duration** | 5m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |