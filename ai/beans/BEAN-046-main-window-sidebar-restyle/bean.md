# BEAN-046: Main Window & Sidebar Restyle

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-046 |
| **Status** | New |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The main window and sidebar currently use inline Catppuccin Mocha styling with purple accents. The sidebar feels like a generic dark theme rather than a "control room" for building software systems. The brand header is a plain text label. Navigation items lack visual weight and don't convey the industrial-modern aesthetic.

## Goal

Restyle the main window shell — sidebar navigation, brand header, menu bar, and overall chrome — using the centralized theme from BEAN-045. The sidebar should feel like a control panel: dense, precise, with brass/gold accents for the active navigation state. The brand "Foundry" header should feel crafted and confident.

## Scope

### In Scope
- Replace all inline stylesheet in `main_window.py` with theme constants from `theme.py`
- Restyle sidebar:
  - Darker background than main content (visual separation)
  - Brand header with stronger typography (bold, slightly larger, possibly letter-spaced)
  - Navigation items with brass/gold selected state, subtle hover
  - Clean border or accent line between sidebar and content
- Restyle menu bar to match dark theme
- Restyle the About dialog
- Update minimum window size if needed for the new proportions
- Update `test_main_window.py` if any structural changes affect tests

### Out of Scope
- Wizard page content (BEAN-048, BEAN-049, BEAN-051)
- Progress/export/history screens (BEAN-050)
- Adding new navigation items or changing navigation structure
- Icon system (BEAN-047 — but this bean may use icons once BEAN-047 is done)

## Acceptance Criteria

- [ ] `main_window.py` uses `theme.py` constants instead of inline hex values
- [ ] Sidebar has distinct visual identity: darker background, clear brand header, brass/gold active state
- [ ] Navigation items have hover and selected states using theme colors
- [ ] Menu bar and About dialog match the industrial dark theme
- [ ] No inline hex color values remain in `main_window.py`
- [ ] Visual result feels like a "control room" — stable, trustworthy, professional
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-045 (theme foundation)
- The sidebar is the user's persistent navigation — it should feel solid and permanent
- Consider subtle texture or gradient on sidebar (blueprint-grid feel?) but keep it restrained
- Test by running the app: `uv run foundry`
