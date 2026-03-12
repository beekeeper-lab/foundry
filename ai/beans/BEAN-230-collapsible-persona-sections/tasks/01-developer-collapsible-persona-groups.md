# Task 01: Implement Collapsible Persona Groups

| Field | Value |
|-------|-------|
| **Task** | 01-developer-collapsible-persona-groups |
| **Owner** | Developer |
| **Status** | Done |
| **Depends On** | — |
| **Started** | 2026-03-12 03:16 |
| **Completed** | 2026-03-12 03:16 |
| **Duration** | < 1m |

## Description

Add collapse/expand functionality to persona group sections in the wizard's persona selection page.

## Acceptance Criteria

- [ ] Each persona group has a clickable header with chevron indicator
- [ ] Clicking the header toggles visibility of persona cards within the group
- [ ] All sections default to expanded on page load
- [ ] Collapse/expand state persists during wizard session
- [ ] Visual indicator (▶/▼) shows current state

## Implementation Notes

- Add `CollapsibleGroupHeader` widget with chevron + category label
- Replace `QGroupBox` with custom collapsible container in `load_personas()`
- Use `QWidget.setVisible()` for content toggling