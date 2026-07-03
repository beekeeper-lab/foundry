# BEAN-207: FinOps / Cloud Cost Management Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-207 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:55 |
| **Completed** | 2026-02-20 20:02 |
| **Duration** | 7m (corrected 2026-07) |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a finops / cloud cost management stack. Add finops stack to ai-team-library. Cloud spend optimization, tagging strategies, reserved instance planning, cost allocation models, budget alerts, showback/chargeback reporting, waste identification, right-sizing recommendations.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add finops stack to ai-team-library. Cloud spend optimization, tagging strategies, reserved instance planning, cost allocation models, budget alerts, showback/chargeback reporting, waste identification, right-sizing recommendations.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Stack file created in `ai-team-library/stacks/` following standardized template
- [x] Includes: Defaults table with alternatives, Do/Don't lists, Common Pitfalls, Checklist, code examples
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create FinOps stack files | Developer | — | Done |
| 2 | Verify quality and run tests | Tech-QA | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #82.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4bba3aceff8738b682f |
| **Card Name** | FinOps / Cloud Cost Management Stack |
| **Card URL** | https://trello.com/c/C9uD0l1e |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create FinOps stack files | Developer | — | — | — | — |
| 2 | Verify quality and run tests | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 7m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |