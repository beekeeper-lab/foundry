# BEAN-210: Sales Engineering Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-210 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:01 |
| **Completed** | 2026-02-20 20:08 |
| **Duration** | 7m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a sales engineering stack. Add sales-engineering stack to ai-team-library. Demo environment management, RFP/RFI response templates, POC scoping and success criteria, competitive battle cards, technical win documentation, customer architecture review patterns.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add sales-engineering stack to ai-team-library. Demo environment management, RFP/RFI response templates, POC scoping and success criteria, competitive battle cards, technical win documentation, customer architecture review patterns.

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
| 1 | Create sales-engineering stack (6 topic files) | Developer | — | Done |
| 2 | Update test_library_indexer EXPECTED_STACKS | Developer | 1 | Done |
| 3 | Verify tests pass and lint clean | Tech-QA | 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #85.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4bf732d46ca5d2231c4 |
| **Card Name** | Sales Engineering Stack |
| **Card URL** | https://trello.com/c/fDzVUImb |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create sales-engineering stack (6 topic files) | Developer | — | — | — | — |
| 2 | Update test_library_indexer EXPECTED_STACKS | Developer | — | — | — | — |
| 3 | Verify tests pass and lint clean | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 7m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |