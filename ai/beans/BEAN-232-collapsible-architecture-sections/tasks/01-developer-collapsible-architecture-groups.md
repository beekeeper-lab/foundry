# Task 01: Implement Collapsible Architecture Groups

| Field | Value |
|-------|-------|
| **Task** | 01-developer-collapsible-architecture-groups |
| **Owner** | Developer |
| **Status** | Done |
| **Depends On** | — |
| **Started** | 2026-03-12 03:16 |
| **Completed** | 2026-03-12 03:16 |
| **Duration** | < 1m |

## Objective

Add collapse/expand functionality to the Architecture Patterns and Cloud Providers sections in the wizard's architecture page.

## Approach

- Create a `CollapsibleSection` widget with clickable header and chevron indicator
- Replace the static QLabel section headers with CollapsibleSection instances
- Default all sections to expanded on page load
- Persist state during wizard session (in-memory)

## Files Modified

- `foundry_app/ui/screens/builder/wizard_pages/architecture_page.py`