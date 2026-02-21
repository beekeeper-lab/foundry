# BEAN-220: Group Expertise by Category in Wizard UI

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-220 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | 2026-02-20 21:42 |
| **Completed** | 2026-02-20 21:46 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The expertise selection page in the Foundry wizard displays all 39 items as a flat list of cards. With items spanning languages, compliance frameworks, infrastructure platforms, and business practices, users must scroll through the entire list to find relevant items. There is no visual grouping or filtering.

## Goal

Update the expertise selection page to group ExpertiseCards under collapsible category sections. Each section shows a category header with item count. Also add `EXPERTISE_DESCRIPTIONS` entries for the 28 expertise items currently missing display names and descriptions.

## Scope

### In Scope
- Group ExpertiseCards by category using the `ExpertiseInfo.category` field
- Render each category as a collapsible section with a header label and item count
- All categories expanded by default
- Items with empty/unknown category go in an "Other" group
- Add display names and descriptions for all 28 expertise items missing from `EXPERTISE_DESCRIPTIONS`
- Preserve the Move Up/Move Down reordering functionality within groups
- Update test_expertise_page.py (formerly test_stack_page.py) for grouped layout

### Out of Scope
- Category filtering (show/hide entire categories)
- Search/filter within expertise items
- Changes to ExpertiseInfo model or library indexer (those are BEAN-218 and BEAN-219)
- Cross-category drag-and-drop reordering

## Acceptance Criteria

- [ ] Expertise cards are visually grouped under category headers
- [ ] Category headers show name and count (e.g., "Languages (12)")
- [ ] Each category section is collapsible (click header to toggle)
- [ ] All categories expanded by default
- [ ] Items with no category appear in an "Other" group
- [ ] All 39 expertise items have entries in `EXPERTISE_DESCRIPTIONS`
- [ ] Selecting/deselecting items still works correctly within groups
- [ ] Move Up/Move Down reordering still works within groups
- [ ] `get_expertise_selections()` returns all selected items regardless of group
- [ ] `set_expertise_selections()` correctly restores selections across groups
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

Depends on BEAN-218 (category field in ExpertiseInfo) and BEAN-219 (category metadata in expertise files). Both must be merged before this bean can be fully tested.

The 28 expertise items needing EXPERTISE_DESCRIPTIONS entries (currently only 11 have descriptions): accessibility-compliance, api-design, aws-cloud-platform, azure-cloud-platform, business-intelligence, change-management, customer-enablement, data-engineering, event-driven-messaging, finops, frontend-build-tooling, gcp-cloud-platform, gdpr-data-privacy, go, hipaa-compliance, iso-9000, kotlin, kubernetes, microservices, mlops, pci-dss-compliance, product-strategy, react-native, rust, sales-engineering, sox-compliance, swift, terraform.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
