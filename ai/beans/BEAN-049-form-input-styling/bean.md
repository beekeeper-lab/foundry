# BEAN-049: Form & Input Styling

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-049 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | Developer |
| **Category** | App |

## Problem Statement

Form elements (text inputs, combo boxes, labels, validation messages) across the app use inline Catppuccin styling. The project identity page has a QFormLayout with inline labels, but the style guide calls for labels above inputs with grouped separators. Validation feedback uses simple color changes without clear visual structure. Combo boxes and dropdowns need consistent industrial styling.

## Goal

Restyle all form and input elements to match the industrial theme: labels above inputs, subtle group separators, brass/gold focus borders, calm validation feedback. Forms should feel precise and structured, like entering parameters in a control system.

## Scope

### In Scope
- Replace inline stylesheets in `project_page.py` for all form elements
- Style QLineEdit: dark surface, subtle border, brass/gold focus ring
- Style QComboBox: matching dark theme, clean dropdown, brass/gold focus
- Style QCheckBox: custom appearance matching industrial theme
- Style labels: clear hierarchy (field labels vs hints vs validation messages)
- Validation messages: calm feedback with muted red for errors, amber for warnings
- Style read-only inputs (slug field): visually distinct from editable inputs
- Group related inputs with subtle horizontal separators or section spacing
- Apply consistent form styling to combo boxes in hook_safety_page.py (posture selector, mode selectors)
- Update tests if structural changes affect them

### Out of Scope
- Card components (BEAN-048)
- Button styling (handled in respective page beans)
- Adding new form fields or changing form behavior
- Complex form layout restructuring (keep existing QFormLayout if it works)

## Acceptance Criteria

- [x] All form elements use `theme.py` constants — no inline hex values
- [x] QLineEdit has clear unfocused/focused/error/read-only states
- [x] QComboBox matches the industrial dark theme with clean dropdowns
- [x] QCheckBox has custom styling consistent with the theme
- [x] Validation messages use muted red with clear but calm presentation
- [x] Labels have proper typography hierarchy (weight/size, not just color)
- [x] Forms feel structured and precise — "entering parameters in a control system"
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-045 (theme foundation)
- The project page is the first thing users see in the wizard — it sets the tone
- Style guide says "label above input (not inline)" — may need layout change from QFormLayout to QVBoxLayout with manual label/input pairs
- Validation should be "calm and informative" — no aggressive red borders or error icons
