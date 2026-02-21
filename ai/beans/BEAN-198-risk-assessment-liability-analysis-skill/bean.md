# BEAN-198: Risk Assessment & Liability Analysis Skill

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-198 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:39 |
| **Completed** | 2026-02-20 19:42 |
| **Duration** | 3m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a risk assessment & liability analysis skill. Add risk-liability skill to ai-team-library. Evaluating legal exposure in software projects, indemnification clauses, limitation of liability, insurance requirements, incident response legal obligations, breach notification duties.

## Goal

Add the content to the ai-team-library with comprehensive, actionable guidance.

## Scope

### In Scope
- Add risk-liability skill to ai-team-library. Evaluating legal exposure in software projects, indemnification clauses, limitation of liability, insurance requirements, incident response legal obligations, breach notification duties.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Skill documentation created following library conventions
- [x] Covers all key topics described in the card description
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create risk-liability SKILL.md | Developer | — | Done |
| 2 | Create risk-liability command doc | Developer | — | Done |
| 3 | Verify skill and run tests/lint | Tech-QA | 1, 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #73.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f3dbcb0f0bde3d7d1a76 |
| **Card Name** | Risk Assessment & Liability Analysis Skill |
| **Card URL** | https://trello.com/c/P98FByFL |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create risk-liability SKILL.md | Developer | — | — | — | — |
| 2 | Create risk-liability command doc | Developer | — | — | — | — |
| 3 | Verify skill and run tests/lint | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 3m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |