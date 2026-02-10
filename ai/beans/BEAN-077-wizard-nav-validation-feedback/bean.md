# BEAN-077: Wizard Navigation Validation Feedback

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-077 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-09 |
| **Completed** | 2026-02-09 |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard's Next button silently does nothing when the current page fails validation. In `_go_next()` (builder_screen.py:208-209), if `_is_current_page_valid()` returns `False`, the method simply returns with no visual feedback. Users click Next repeatedly with no idea why it's not working. This affects all wizard pages that have validation (Project, Personas, Stacks).

## Goal

The Next button is disabled (grayed out) whenever the current wizard page is not valid. It re-enables dynamically as the user makes selections. Users always have clear visual feedback about whether they can proceed.

## Scope

### In Scope
- Disable the Next button when the current page's `is_valid()` / `is_complete()` returns `False`
- Connect page change signals to re-evaluate button state:
  - `ProjectPage.completeness_changed` signal
  - `PersonaSelectionPage.selection_changed` signal
  - `StackSelectionPage.selection_changed` signal
- Re-evaluate button state on page transitions (`_update_nav_state`)
- Add a disabled style for the Next button (muted/grayed appearance)
- Architecture and Safety pages always return `True` — no change needed for those

### Out of Scope
- Tooltip or status bar text explaining *why* Next is disabled
- Validation error highlighting on individual fields
- Empty-state messaging (covered by BEAN-078)

## Acceptance Criteria

- [x] Next button is disabled on wizard page 0 (Project) when the project name field is empty
- [x] Next button enables on page 0 when a project name is entered
- [x] Next button is disabled on page 1 (Personas) when no persona is selected
- [x] Next button enables on page 1 when at least one persona is selected
- [x] Next button is disabled on page 2 (Stacks) when no stack is selected
- [x] Next button enables on page 2 when at least one stack is selected
- [x] Next button is always enabled on pages 3 (Architecture) and 4 (Safety) since those are optional
- [x] Button state updates reactively (not just on click) — toggling a checkbox immediately updates the button
- [x] Disabled button has a visually distinct style (grayed/muted)
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add `_update_next_enabled()` method to BuilderScreen | | | Pending |
| 2 | Connect page signals to `_update_next_enabled()` | | 1 | Pending |
| 3 | Call `_update_next_enabled()` from `_update_nav_state()` | | 1 | Pending |
| 4 | Add disabled QPushButton style to `_primary_button_style()` | | | Pending |
| 5 | Add/update tests for button state behavior | | 1-4 | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- **Key file:** `foundry_app/ui/screens/builder_screen.py` — `_go_next()` (line 206), `_update_nav_state()` (line 227)
- Signal connections needed in `_build_ui()` after page creation (around line 120)
- The `_go_next` validation check (line 208) should remain as a safety net, but the button being disabled makes it a secondary guard
- Depends on BEAN-075 only loosely — this fix is valuable even without auto-detection, because it covers all validation pages

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
