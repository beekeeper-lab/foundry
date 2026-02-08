# BEAN-052: Accessibility & Visual Polish

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-052 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The app currently has no explicit accessibility features. Focus states are minimal (only on some inputs via border color). Keyboard navigation hasn't been tested or optimized. Some information is conveyed by color alone (status indicators). After the style beans (BEAN-045 through BEAN-051) are applied, a final pass is needed to verify visual consistency, fix edge cases, and ensure the app is accessible.

## Goal

Add proper accessibility support and perform a final visual polish pass across the entire app. Every interactive element should have a visible focus state. The app should be fully keyboard-navigable. No information should be conveyed by color alone. Fix any visual inconsistencies introduced by the style updates.

## Scope

### In Scope
- Focus states (brass/gold focus ring) on all interactive elements:
  - QPushButton, QLineEdit, QComboBox, QCheckBox, QListWidget items
  - Card components (QFrame-based)
  - Navigation sidebar items
- Keyboard navigation:
  - Tab order verification across all wizard pages
  - Arrow key navigation in card lists
  - Enter/Space activation of buttons and checkboxes
  - Escape to cancel dialogs
- Color-only information:
  - Add text labels or icons alongside color-coded status indicators
  - Ensure selected/unselected states are distinguishable without color
- Contrast verification:
  - All text meets WCAG AA contrast ratio (4.5:1 for normal, 3:1 for large)
  - Verify against the industrial dark palette
- Visual consistency pass:
  - Check all screens for missed inline hex values
  - Verify spacing/padding consistency across pages
  - Fix any edge cases (long text overflow, narrow window, etc.)
- Tooltips on icon-only elements (if any exist after BEAN-047)

### Out of Scope
- Screen reader support (ARIA equivalents for Qt — complex, defer to future)
- High-contrast alternate theme
- RTL layout support
- Adding new features

## Acceptance Criteria

- [ ] Every interactive widget has a visible focus state (brass/gold ring or highlight)
- [ ] Tab key navigates through all interactive elements in logical order
- [ ] No information conveyed by color alone — text/icon backup for all status indicators
- [ ] All text passes WCAG AA contrast ratio against its background
- [ ] No inline hex color values remain in any UI file
- [ ] Spacing and padding are consistent across all wizard pages and screens
- [ ] App is usable entirely via keyboard (no mouse required for core workflows)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on ALL other style beans (BEAN-045 through BEAN-051) — this is the final pass
- This bean should be done LAST in the style work
- Style guide: "High contrast text, keyboard navigable, focus states clearly visible, no information conveyed by color alone"
- Run the app and tab through every screen to verify keyboard navigation
- Use a contrast checker tool to verify color ratios
