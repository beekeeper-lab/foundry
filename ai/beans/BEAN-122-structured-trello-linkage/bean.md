# BEAN-122: Structured Trello Linkage in Bean Template

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-122 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-14 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

When `/trello-load` creates beans from Trello cards, the linkage is stored as a free-text note ("Source: Trello card '[Card Name]'") in the Notes section. When `/long-run` completes a bean and needs to move the Trello card to Completed, it must parse this note, then do fuzzy name matching across the In_Progress list to find the card. This is fragile — card names can change, multiple cards may have similar names, and the match can fail silently. There is no structured data to directly locate the card via API. Non-Trello beans have no indicator at all, so the code must check for the absence of a note pattern.

## Goal

Every bean has a dedicated `## Trello` section with structured fields (workspace, board, list, card ID, card URL). Trello-sourced beans have all fields populated. Non-Trello beans have a clear "N/A" marker. `/long-run` uses the card ID directly instead of fuzzy matching.

## Scope

### In Scope
- Add a `## Trello` section to the bean template (`_bean-template.md`) between Notes and Telemetry
- Fields: Workspace (name), Board (name + ID), Source List (name), Card ID, Card Name, Card URL
- Non-Trello beans show `Source: Manual` (no Trello fields)
- Update `/trello-load` skill to populate the Trello section with full metadata when creating beans from cards
- Update `/long-run` skill to read the structured Trello section (Card ID + Board ID) for direct API calls instead of fuzzy matching from Notes
- Update `/backlog-refinement` skill to set `Source: Manual` when creating non-Trello beans
- Update `/new-bean` skill to set `Source: Manual` in the Trello section
- Update the library copy of the bean template (`ai-team-library/process/beans/_bean-template.md`)
- Remove the "Source: Trello card" convention from Notes (no longer needed)

### Out of Scope
- Changing how Trello boards/lists are discovered (already works via `/trello-load`)
- Adding Trello fields to the `_index.md` table (the index stays lean — Trello data lives in bean.md)
- Bi-directional sync (updating Trello card description from bean changes)
- Trello webhook integration

## Acceptance Criteria

- [ ] Bean template has a `## Trello` section between Notes and Telemetry
- [ ] Trello section for Trello-sourced beans contains: Workspace, Board Name, Board ID, Source List, Card ID, Card Name, Card URL
- [ ] Trello section for non-Trello beans shows `Source: Manual`
- [ ] `/trello-load` populates all Trello fields when creating beans from cards
- [ ] `/long-run` uses Card ID from the Trello section (not fuzzy name matching from Notes) to move cards to Completed
- [ ] `/backlog-refinement` sets `Source: Manual` when creating beans
- [ ] `/new-bean` sets `Source: Manual` in the Trello section
- [ ] Library bean template (`ai-team-library/process/beans/_bean-template.md`) is updated
- [ ] All existing tests pass
- [ ] Lint clean

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- The Trello section format for Trello-sourced beans:
  ```
  ## Trello

  | Field | Value |
  |-------|-------|
  | **Source** | Trello |
  | **Workspace** | Beekeeper Lab |
  | **Board** | Foundry (ID: abc123) |
  | **Source List** | Sprint_Backlog |
  | **Card ID** | def456 |
  | **Card Name** | Add user authentication |
  | **Card URL** | https://trello.com/c/def456 |
  ```
- The Trello section format for non-Trello beans:
  ```
  ## Trello

  | Field | Value |
  |-------|-------|
  | **Source** | Manual |
  ```
- `/long-run` step 17b currently: "Check the bean's Notes section for a 'Source: Trello card' reference" → change to: "Read the Trello section; if Source is 'Trello', use Card ID and Board ID to call `mcp__trello__move_card` directly"
- This eliminates the fragile fuzzy matching step entirely
- Card ID is stable (unlike card names which can be edited)

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
