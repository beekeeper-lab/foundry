# BEAN-167: ISO 9000 Certification Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-167 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 22:20 |
| **Completed** | 2026-02-20 22:26 |
| **Duration** | 6m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The Foundry library lacks an ISO 9000 certification and compliance officer tech stack option. Users who need quality management system compliance cannot generate projects with ISO 9000 guidance.

## Goal

Add a new tech stack option in the ai-team-library for ISO 9000 Certification and Compliance Officer. Include detailed skill descriptions and third-party references that agents can read.

## Scope

### In Scope
- Create ISO 9000 tech stack YAML in the library
- Include certification-specific skills and knowledge areas
- Add references to ISO standards, ANSI resources, and compliance guides
- Ensure the stack integrates with the existing library indexer

### Out of Scope
- Modifying the library indexer service itself
- Creating a new persona (uses existing personas)

## Acceptance Criteria

- [x] ISO 9000 tech stack YAML exists in the library
- [x] Stack includes relevant skills (QMS, audit, document control, CAPA, etc.)
- [x] References to third-party sources are included
- [x] Library indexer can discover and index the new stack
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create ISO 9000 Tech Stack | Developer | — | Done |
| 2 | Verify ISO 9000 Tech Stack | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default — straightforward library addition)

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

(None)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 699849f3f68f1e9987582092 |
| **Card Name** | ISO 9000 Tech Stack |
| **Card URL** | https://trello.com/c/Xqngnooa/40-iso-9000-tech-stack |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create ISO 9000 Tech Stack | Developer | 4m | 3,022,218 | 3,830 | $5.39 |
| 2 | Verify ISO 9000 Tech Stack | Tech-QA | 1m | 307,214 | 831 | $0.54 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 5m |
| **Total Tokens In** | 3,329,432 |
| **Total Tokens Out** | 4,661 |
| **Total Cost** | $5.93 |