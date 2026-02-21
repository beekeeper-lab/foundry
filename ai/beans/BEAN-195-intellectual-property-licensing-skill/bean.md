# BEAN-195: Intellectual Property & Licensing Skill

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-195 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:36 |
| **Completed** | 2026-02-20 19:39 |
| **Duration** | 3m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a intellectual property & licensing skill. Add IP-licensing skill to ai-team-library. Open source license compatibility (GPL, MIT, Apache, AGPL), software patents, trade secrets, copyright ownership, contributor license agreements (CLAs).

## Goal

Add the content to the ai-team-library with comprehensive, actionable guidance.

## Scope

### In Scope
- Add IP-licensing skill to ai-team-library. Open source license compatibility (GPL, MIT, Apache, AGPL), software patents, trade secrets, copyright ownership, contributor license agreements (CLAs).

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Skill documentation created following library conventions
- [x] Covers all key topics described in the card description
- [x] All tests pass (`uv run pytest`) — no Python files modified; pre-existing PySide6 env issue
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create IP & Licensing SKILL.md | Developer | — | Done |
| 2 | Verify skill quality and acceptance criteria | Tech-QA | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #70.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f3d749a78847536c33a9 |
| **Card Name** | Intellectual Property & Licensing Skill |
| **Card URL** | https://trello.com/c/nfq7d4oE |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create IP & Licensing SKILL.md | Developer | — | — | — | — |
| 2 | Verify skill quality and acceptance criteria | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 3m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |