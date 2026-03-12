# BEAN-231: Collapsible Expertise Selection Sections

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-231 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-03-12 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the wizard's expertise (technology stack) selection page, all expertise groups are always expanded. With the growing number of expertise options, this creates a long scrollable list that is hard to navigate. Users need collapsible sections to manage the visual complexity.

## Goal

Make the expertise selection sections (groups) collapsible so users can expand/collapse each group independently.

## Scope

### In Scope
- Add collapse/expand functionality to expertise group sections in the wizard
- Persist expand/collapse state during the wizard session
- Visual indicator (chevron/arrow) showing collapsed vs expanded state

### Out of Scope
- Persisting collapse state across application restarts
- Filtering or searching expertise items

## Acceptance Criteria

- [ ] Each expertise group section has a clickable header that toggles collapse/expand
- [ ] Collapsed sections hide their expertise items
- [ ] Visual indicator shows current state (expanded vs collapsed)
- [ ] All sections default to expanded on page load
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

Trello card #101. Related to BEAN-230 (persona sections) and BEAN-232 (architecture sections).

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 69a09e6dd1f20a7cc6d3ff0a |
| **Card Name** | make the expertise sections collapsible. |
| **Card URL** | https://trello.com/c/3BlgHC7i |

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
