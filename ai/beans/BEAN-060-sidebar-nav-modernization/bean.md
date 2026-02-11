# BEAN-060: Sidebar Navigation Modernization

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-060 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The current sidebar is a plain QListWidget with text-only items ("Foundry", "Builder", "Library", "History", "Settings"). It has no icons, no visual hierarchy, and looks dated. Users have described it as "1990s looking." Modern desktop apps use icon + text navigation with active state indicators, hover transitions, and clear visual grouping.

## Goal

A polished, modern sidebar navigation with icon + text items, a left-edge active indicator bar, smooth hover transitions, and a version/info footer. The sidebar should feel like a contemporary desktop app (VS Code, Figma, Slack style) while maintaining the industrial dark theme aesthetic.

## Scope

### In Scope
- Replace QListWidget with custom icon + text navigation items
- Integrate SVG icons from BEAN-047's icon set (or create minimal placeholder icons if the set isn't available): hammer/wrench for Builder, books/folder for Library, clock for History, gear for Settings
- Add a 3px brass/gold left-edge indicator bar on the active item
- Implement hover transitions (background color fade, subtle text color shift)
- Add proper vertical spacing between nav items (not cramped list)
- Add a sidebar footer with a small info "i" icon and version number ("v1.0.0") that opens the About dialog on click
- Remove the "Foundry" text label at the top of the sidebar — the brand is in the window title and will be in the logo (BEAN-043)
- Ensure keyboard navigation still works (up/down arrows, Enter to select)

### Out of Scope
- Collapsible/expandable sidebar (keep fixed width for now)
- Drag-to-reorder navigation items
- Badge/notification counts on nav items
- The theme wiring itself (that's BEAN-054)
- Menu bar removal (that's BEAN-056)

## Acceptance Criteria

- [ ] Each sidebar item has an icon (SVG or fallback) and text label
- [ ] Active item shows a 3px left-edge brass/gold indicator bar
- [ ] Hover state shows a subtle background color change
- [ ] Sidebar footer displays version and info icon that opens the About dialog
- [ ] "Foundry" brand text label is removed from sidebar top
- [ ] Keyboard navigation (arrow keys, Tab) works correctly
- [ ] Sidebar width is appropriate for icon + text (180-220px)
- [ ] Visual style matches the industrial dark theme (deep charcoal bg, brass accents)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-054 (Theme Wiring Fix) being done first so the dark theme actually renders.
- BEAN-047 (Icon Set) may provide the icons needed. If not available, create minimal inline SVG placeholders.
- The current sidebar code is in `foundry_app/ui/main_window.py` lines 190-207. The nav list is exposed via `MainWindow.nav_list` property (line 239) — other code may depend on this API.
- The About dialog trigger currently lives in the Help menu (line 180). It needs to be rewired to the sidebar footer info icon.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 5s).
