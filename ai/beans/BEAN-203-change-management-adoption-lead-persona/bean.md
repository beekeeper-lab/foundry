# BEAN-203: Change Management / Adoption Lead Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-203 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:47 |
| **Completed** | 2026-02-20 19:52 |
| **Duration** | < 1 day |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a change management / adoption lead persona. Add change-management persona to ai-team-library. Organizational change communication, training and skills development programs, change resistance mitigation, process adoption tracking, stakeholder alignment. Pairs with Change Management stack.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add change-management persona to ai-team-library. Organizational change communication, training and skills development programs, change resistance mitigation, process adoption tracking, stakeholder alignment. Pairs with Change Management stack.

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
| 1 | Create change-management persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | Done |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | 1 | Done |
| 3 | Verify tests pass and lint clean | Tech-QA | 2 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #78.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4b577257560cb3c5f6e |
| **Card Name** | Change Management / Adoption Lead Persona |
| **Card URL** | https://trello.com/c/GFHRcZQL |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create change-management persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | — | — | — |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | — | — | — | — |
| 3 | Verify tests pass and lint clean | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 5m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |