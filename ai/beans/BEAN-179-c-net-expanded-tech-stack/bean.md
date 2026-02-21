# BEAN-179: C#/.NET Expanded Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-179 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:08 |
| **Completed** | 2026-02-20 19:13 |
| **Duration** | 5m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a c#/.net expanded tech stack. Expand dotnet stack with Blazor, MAUI, Unity-specific patterns. Current stack covers basics; needs deeper framework coverage.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Expand dotnet stack with Blazor, MAUI, Unity-specific patterns. Current stack covers basics; needs deeper framework coverage.

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
| 1 | Create Blazor framework stack file | Developer | — | Done |
| 2 | Create MAUI framework stack file | Developer | — | Done |
| 3 | Create Unity framework stack file | Developer | — | Done |
| 4 | Verify tests and lint pass | Tech-QA | 1,2,3 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #52.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f336015dafc4f3c3d543 |
| **Card Name** | C#/.NET Expanded Tech Stack |
| **Card URL** | https://trello.com/c/qwy4lGh4 |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create Blazor framework stack file | Developer | — | — | — | — |
| 2 | Create MAUI framework stack file | Developer | — | — | — | — |
| 3 | Create Unity framework stack file | Developer | — | — | — | — |
| 4 | Verify tests and lint pass | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 5m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |