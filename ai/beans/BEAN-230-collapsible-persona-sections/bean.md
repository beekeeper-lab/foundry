# BEAN-230: Collapsible Persona Selection Sections

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-230 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-03-12 |
| **Started** | 2026-03-12 03:18 |
| **Completed** | 2026-03-12 03:18 |
| **Duration** | < 1h |
| **Owner** | Developer |
| **Category** | App |

## Problem Statement

In the wizard's persona selection page, all persona groups are always expanded, making it difficult to navigate when there are many personas. Users need the ability to collapse persona groups to reduce visual clutter and focus on the groups they care about.

## Goal

Make the persona selection sections (groups) collapsible so users can expand/collapse each group of personas independently.

## Scope

### In Scope
- Add collapse/expand functionality to persona group sections in the wizard
- Persist expand/collapse state during the wizard session
- Visual indicator (chevron/arrow) showing collapsed vs expanded state

### Out of Scope
- Persisting collapse state across application restarts
- Filtering or searching personas

## Acceptance Criteria

- [ ] Each persona group section has a clickable header that toggles collapse/expand
- [ ] Collapsed sections hide their persona items
- [ ] Visual indicator shows current state (expanded vs collapsed)
- [ ] All sections default to expanded on page load
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement collapsible persona groups | Developer | — | Done |
| 2 | Verify collapsible sections | Tech QA | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Trello card #100. Related to BEAN-231 (expertise sections) and BEAN-232 (architecture sections) — all three add collapsible behavior to different wizard pages.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 69a09e282de27adef0c1ca80 |
| **Card Name** | Make the sections where we select the persona collapsible.  So we can collapse the group of personas. |
| **Card URL** | https://trello.com/c/ZE2tQeCY |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Implement collapsible persona groups | Developer | — | — | — | — |
| 2 | Verify collapsible sections | Tech QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 344h 42m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |