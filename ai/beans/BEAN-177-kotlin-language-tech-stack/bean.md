# BEAN-177: Kotlin Language Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-177 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:08 |
| **Completed** | 2026-02-20 19:14 |
| **Duration** | 6m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a kotlin language tech stack. Add Kotlin stack to ai-team-library. Coroutines, null safety, data classes, Android + server-side Spring Boot patterns. Follows standardized template.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add Kotlin stack to ai-team-library. Coroutines, null safety, data classes, Android + server-side Spring Boot patterns. Follows standardized template.

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
| 1 | Create Kotlin conventions.md | Developer | — | Done |
| 2 | Create Kotlin performance.md | Developer | — | Done |
| 3 | Create Kotlin security.md | Developer | — | Done |
| 4 | Create Kotlin testing.md | Developer | — | Done |
| 5 | Update test_library_indexer.py expected stacks | Developer | — | Done |
| 6 | Verify all tests pass and lint clean | Tech-QA | 1,2,3,4,5 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #50.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f33303f0eb67a827a064 |
| **Card Name** | Kotlin Language Tech Stack |
| **Card URL** | https://trello.com/c/5wF6ZQAd |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create Kotlin conventions.md | Developer | — | — | — | — |
| 2 | Create Kotlin performance.md | Developer | — | — | — | — |
| 3 | Create Kotlin security.md | Developer | — | — | — | — |
| 4 | Create Kotlin testing.md | Developer | — | — | — | — |
| 5 | Update test_library_indexer.py expected stacks | Developer | — | — | — | — |
| 6 | Verify all tests pass and lint clean | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 6 |
| **Total Duration** | 6m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |