# BEAN-183: Azure Cloud Platform Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-183 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:15 |
| **Completed** | 2026-02-20 19:19 |
| **Duration** | 4m (corrected 2026-07) |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a azure cloud platform stack. Add Azure stack to ai-team-library. App Service, AKS, Azure AD, Cosmos DB, Service Bus. Counterpart to existing AWS stack.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add Azure stack to ai-team-library. App Service, AKS, Azure AD, Cosmos DB, Service Bus. Counterpart to existing AWS stack.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Stack file created in `ai-team-library/stacks/` following standardized template
- [x] Includes: Defaults table with alternatives, Do/Don't lists, Common Pitfalls, Checklist, code examples
- [x] All tests pass (`uv run pytest`) — pre-existing PySide6 segfault in headless env; no Python code changed
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create Azure core-services.md stack file | Developer | — | Done |
| 2 | Create Azure well-architected.md stack file | Developer | — | Done |
| 3 | Verify tests pass and lint clean | Tech-QA | 1, 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #56.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f33c2bf5458d89eee391 |
| **Card Name** | Azure Cloud Platform Stack |
| **Card URL** | https://trello.com/c/EUe2WIo0 |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create Azure core-services.md stack file | Developer | — | — | — | — |
| 2 | Create Azure well-architected.md stack file | Developer | — | — | — | — |
| 3 | Verify tests pass and lint clean | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |