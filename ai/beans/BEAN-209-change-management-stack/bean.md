# BEAN-209: Change Management Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-209 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:56 |
| **Completed** | 2026-02-20 20:04 |
| **Duration** | 8m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a change management stack. Add change-management stack to ai-team-library. ADKAR framework, stakeholder mapping templates, communication plans, training curricula design, adoption KPI tracking, rollback triggers, organizational readiness assessments.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add change-management stack to ai-team-library. ADKAR framework, stakeholder mapping templates, communication plans, training curricula design, adoption KPI tracking, rollback triggers, organizational readiness assessments.

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
| 1 | Create change management stack files | Developer | — | Done |
| 2 | Tech QA — verify stack and run tests | Tech-QA | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #84.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4bd6f1bfd5ad6912c8e |
| **Card Name** | Change Management Stack |
| **Card URL** | https://trello.com/c/aDMa8bXc |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create change management stack files | Developer | — | — | — | — |
| 2 | Tech QA — verify stack and run tests | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 8m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |