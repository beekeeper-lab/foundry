# Task 01: Implement Collapsible Expertise Groups

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Status** | Done |
| **Depends On** | — |
| **Started** | 2026-03-12 03:16 |
| **Completed** | 2026-03-12 03:16 |
| **Duration** | < 1m |

## Description

Add collapse/expand functionality to expertise group sections in the wizard's expertise selection page.

## Acceptance Criteria

- [ ] Create a `CollapsibleSection` widget with clickable header and chevron indicator
- [ ] Replace `QGroupBox` usage in `load_expertise()` with `CollapsibleSection`
- [ ] Chevron shows ▼ when expanded, ▶ when collapsed
- [ ] All sections default to expanded on page load
- [ ] Collapse state persists during wizard session

## Files Changed

- `foundry_app/ui/screens/builder/wizard_pages/expertise_page.py`