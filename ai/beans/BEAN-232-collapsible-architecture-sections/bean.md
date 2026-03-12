# BEAN-232: Collapsible Architecture Selection Sections

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-232 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-03-12 |
| **Started** | 2026-03-12 03:16 |
| **Completed** | 2026-03-12 03:18 |
| **Duration** | 344h 42m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the wizard's architecture and cloud configuration page, all sections are always expanded. Users need the ability to collapse sections to reduce visual clutter and focus on the configuration areas they are actively working with.

## Goal

Make the architecture selection sections collapsible so users can expand/collapse each group independently.

## Scope

### In Scope
- Add collapse/expand functionality to architecture group sections in the wizard
- Persist expand/collapse state during the wizard session
- Visual indicator (chevron/arrow) showing collapsed vs expanded state

### Out of Scope
- Persisting collapse state across application restarts
- Filtering or searching architecture items

## Acceptance Criteria

- [ ] Each architecture group section has a clickable header that toggles collapse/expand
- [ ] Collapsed sections hide their architecture items
- [ ] Visual indicator shows current state (expanded vs collapsed)
- [ ] All sections default to expanded on page load
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement collapsible architecture groups | Developer | — | Done |
| 2 | Verify collapsible sections | Tech-QA | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| foundry_app/ui/screens/builder/wizard_pages/architecture_page.py | +97/-4 |

## Notes

Trello card #102. Related to BEAN-230 (persona sections) and BEAN-231 (expertise sections).

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 69a09e8db30b2622bb9488c7 |
| **Card Name** | Make the Architecture sections collapsible. |
| **Card URL** | https://trello.com/c/Kx9UddVY |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Implement collapsible architecture groups | Developer | — | — | — | — |
| 2 | Verify collapsible sections | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 344h 42m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |