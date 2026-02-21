# BEAN-184: API Design Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-184 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:18 |
| **Completed** | 2026-02-20 19:24 |
| **Duration** | 6m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a api design tech stack. Add API design stack to ai-team-library. REST + GraphQL conventions, versioning, pagination, error contracts, rate limiting, OpenAPI specs.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add API design stack to ai-team-library. REST + GraphQL conventions, versioning, pagination, error contracts, rate limiting, OpenAPI specs.

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
| 1 | Create API design conventions stack file | Developer | — | Done |
| 2 | Create error contracts guide | Developer | — | Done |
| 3 | Create pagination patterns guide | Developer | — | Done |
| 4 | Create rate limiting guide | Developer | — | Done |
| 5 | Create OpenAPI specification guide | Developer | — | Done |
| 6 | Verify tests and lint | Tech-QA | 1–5 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #57.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f33dd7700454ad5fee76 |
| **Card Name** | API Design Tech Stack |
| **Card URL** | https://trello.com/c/p9dTCmzH |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create API design conventions stack file | Developer | — | — | — | — |
| 2 | Create error contracts guide | Developer | — | — | — | — |
| 3 | Create pagination patterns guide | Developer | — | — | — | — |
| 4 | Create rate limiting guide | Developer | — | — | — | — |
| 5 | Create OpenAPI specification guide | Developer | — | — | — | — |
| 6 | Verify tests and lint | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 6 |
| **Total Duration** | 6m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |