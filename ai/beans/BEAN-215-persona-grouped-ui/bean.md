# BEAN-215: Group Personas by Category in Wizard UI

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-215 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | 2026-02-20 20:59 |
| **Completed** | 2026-02-20 21:03 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The persona selection page in the Foundry wizard displays all 24 personas as a flat list of cards. With the library growing from 13 to 24 personas across very different domains (software development, data, compliance, business operations), users have to scroll through the entire list to find relevant personas. There is no visual grouping or filtering.

## Goal

Update the persona selection page to group PersonaCards under collapsible category sections. Each section shows a category header (e.g., "Software Development") that can be expanded/collapsed. All sections start expanded. Also update the `PERSONA_DESCRIPTIONS` dictionary with display names and role descriptions for the 11 new personas added recently.

## Scope

### In Scope
- Group PersonaCards by category using the `PersonaInfo.category` field
- Render each category as a collapsible `QGroupBox` (or equivalent) with a header label and card count
- All categories expanded by default
- Personas with empty/unknown category go in an "Other" group at the bottom
- Add display names and role descriptions for the 11 new personas to `PERSONA_DESCRIPTIONS`
- Update test_persona_page.py for the grouped layout

### Out of Scope
- Category filtering (show/hide entire categories) — future enhancement
- Search/filter within personas
- Drag-and-drop reordering
- Changes to PersonaInfo model or library indexer (those are BEAN-213 and BEAN-214)

## Acceptance Criteria

- [x] Persona cards are visually grouped under category headers
- [x] Category headers show the category name and count (e.g., "Software Development (13)")
- [x] Each category section is collapsible (click header to toggle)
- [x] All categories are expanded by default
- [x] Personas with no category appear in an "Other" group
- [x] All 24 personas have entries in `PERSONA_DESCRIPTIONS`
- [x] Selecting/deselecting personas still works correctly within groups
- [x] `get_team_config()` returns all selected personas regardless of group
- [x] `set_team_config()` correctly restores selections across groups
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add PERSONA_DESCRIPTIONS for 11 new personas and implement grouped layout | Developer | — | Done |
| 2 | Update tests for grouped layout | Tech-QA | 1 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Depends on BEAN-213 (category field in PersonaInfo) and BEAN-214 (category metadata in persona files). Both must be merged before this bean can be fully tested.

The 11 new personas needing PERSONA_DESCRIPTIONS entries: change-management, customer-success, data-analyst, data-engineer, database-administrator, financial-operations, legal-counsel, mobile-developer, platform-sre-engineer, product-owner, sales-engineer.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add PERSONA_DESCRIPTIONS for 11 new personas and implement grouped layout | Developer | — | — | — | — |
| 2 | Update tests for grouped layout | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |