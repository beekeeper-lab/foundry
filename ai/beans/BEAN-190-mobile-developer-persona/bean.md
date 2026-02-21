# BEAN-190: Mobile Developer Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-190 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:27 |
| **Completed** | 2026-02-20 19:33 |
| **Duration** | 6m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a mobile developer persona. Add mobile-developer persona to ai-team-library. App store constraints, device testing, offline-first patterns. Drives react-native/Swift/Kotlin stacks.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add mobile-developer persona to ai-team-library. App store constraints, device testing, offline-first patterns. Drives react-native/Swift/Kotlin stacks.

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
| 1 | Create mobile-developer persona directory and persona.md | Developer | — | Done |
| 2 | Create outputs.md for mobile-developer | Developer | 1 | Done |
| 3 | Create prompts.md for mobile-developer | Developer | 1 | Done |
| 4 | Create templates/ with mobile-specific templates | Developer | 1 | Done |
| 5 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | 1 | Done |
| 6 | Verify all tests pass and lint clean | Tech-QA | 1-5 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #64.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f34727d9412661094d8c |
| **Card Name** | Mobile Developer Persona |
| **Card URL** | https://trello.com/c/IZRmq9lH |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create mobile-developer persona directory and persona.md | Developer | — | — | — | — |
| 2 | Create outputs.md for mobile-developer | Developer | — | — | — | — |
| 3 | Create prompts.md for mobile-developer | Developer | — | — | — | — |
| 4 | Create templates/ with mobile-specific templates | Developer | — | — | — | — |
| 5 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | — | — | — | — |
| 6 | Verify all tests pass and lint clean | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 6 |
| **Total Duration** | 6m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |