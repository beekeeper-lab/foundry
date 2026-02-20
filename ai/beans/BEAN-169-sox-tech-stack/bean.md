# BEAN-169: SOX Compliance Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-169 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The Foundry library lacks a SOX (Sarbanes-Oxley) compliance tech stack option. Organizations subject to SOX requirements cannot generate projects with SOX-specific compliance guidance.

## Goal

Add a new tech stack option in the ai-team-library for SOX compliance. Include detailed skill items that a sub-agent should know and references where it can find more information to build this skill.

## Scope

### In Scope
- Create SOX compliance tech stack YAML in the library
- Include SOX-specific skills (internal controls, financial reporting, IT general controls, audit trails, etc.)
- Add references to PCAOB standards, SEC guidance, and compliance resources
- Ensure the stack integrates with the existing library indexer

### Out of Scope
- Modifying the library indexer service itself
- Creating a new persona

## Acceptance Criteria

- [ ] SOX compliance tech stack YAML exists in the library
- [ ] Stack includes relevant skills (internal controls, ITGC, segregation of duties, audit trail, etc.)
- [ ] References to authoritative sources are included (PCAOB, SEC, COSO framework)
- [ ] Library indexer can discover and index the new stack
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

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
| **Card ID** | 6998499af76185ce5271df17 |
| **Card Name** | SOX Tech Stack |
| **Card URL** | https://trello.com/c/3isAPLjb/39-sox-tech-stack |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
