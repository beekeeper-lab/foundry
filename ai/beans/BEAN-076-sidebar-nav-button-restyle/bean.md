# BEAN-076: Sidebar Nav Button Restyle

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-076 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-09 |
| **Completed** | 2026-02-09 |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The current sidebar navigation uses a `QListWidget` with small 20x20 icons and plain text labels. The inactive items render in a faded color against the sidebar background, making them nearly unreadable. The items look like a plain text list rather than interactive navigation controls — there is no visual affordance that they are clickable. Users report the nav is "not really readable" and lacks graphical presence.

## Goal

Replace the sidebar navigation with icon-over-text button controls that are visually distinct, clearly readable, and feel like a modern app navigation panel. Each nav item should be a large icon centered above a short label, rendered against a dark background that matches the overall theme.

## Scope

### In Scope
- Replace `QListWidget` nav with `QPushButton` or `QToolButton`-based nav items
- Icon-over-text layout: large icon (32-40px) centered above text label
- Dark sidebar background matching the app theme (`BG_INSET` or `BG_BASE`)
- Gold accent indicator on the selected/active button (left border, background tint, or underline)
- Hover state with visual feedback (subtle color shift)
- Proper spacing between nav items
- Keyboard navigation support (Tab/arrow keys)
- Wire all 4 screens (Builder, Library, History, Settings) correctly
- Update sidebar stylesheet in `main_window.py`
- Update existing tests in `test_main_window.py`

### Out of Scope
- Adding new screens or nav items
- Changing the icon SVG artwork itself (reuse existing icons at larger size)
- Changing the content area or any screen implementations
- Responsive/collapsible sidebar behavior

## Acceptance Criteria

- [x] Nav items are rendered as icon-over-text buttons (icon centered above label)
- [x] Icons are 32-40px, clearly visible against the dark background
- [x] Sidebar background is dark, matching the app theme palette
- [x] Selected item has a clear gold/brass accent indicator
- [x] Hover state provides visual feedback on non-selected items
- [x] All 4 screens switch correctly when clicking nav items
- [x] Keyboard navigation works (arrow keys to move, Enter/Space to select)
- [x] Version footer remains functional at the bottom of the sidebar
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Builds on completed BEAN-046 (Main Window & Sidebar Restyle) and BEAN-060 (Sidebar Navigation Modernization) — this is a further iteration based on user feedback after seeing the current result
- Key files: `foundry_app/ui/main_window.py` (sidebar construction + stylesheet), `foundry_app/ui/theme.py` (constants), `foundry_app/ui/icons.py` (icon loader with tinting support)
- Existing SVG icons at `foundry_app/ui/icons/` include builder.svg, library.svg, history.svg, settings.svg
- The `load_icon()` function already supports color tinting and custom size — leverage this for larger colored icons
- Consider using `QToolButton` with `Qt.ToolButtonStyle.ToolButtonTextUnderIcon` for built-in icon-over-text layout

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | Replace QListWidget with QToolButton nav | team-lead | 2m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 (single commit) |
| **Total Duration** | 2m |
| **Total Tokens In** | — (not tracked) |
| **Total Tokens Out** | — (not tracked) |

> Backfilled from git reflog: branch 20:00:54 → merge 20:02:59. Token data unavailable (pre-telemetry-automation).
