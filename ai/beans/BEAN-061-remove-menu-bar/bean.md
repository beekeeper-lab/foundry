# BEAN-061: Remove Menu Bar

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-061 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The traditional File/Help horizontal menu bar at the top of the window looks dated and out of place in a modern desktop application. It contains only two items (File > Quit, Help > About Foundry) which don't justify a full menu bar. The "Quit" action is already available via Ctrl+Q, and the "About" dialog is being relocated to the sidebar footer in BEAN-055. The menu bar wastes vertical screen space and contributes to the "1990s" look.

## Goal

The traditional QMenuBar is completely removed. All its functionality is preserved through keyboard shortcuts and the sidebar footer. The application window has a clean top edge with no menu strip, giving a modern, chrome-less appearance.

## Scope

### In Scope
- Remove the `_build_menu_bar()` method and its call from `MainWindow.__init__()`
- Remove the QMenuBar-related stylesheet rules from both `main_window.py` STYLESHEET and `theme.py` `_BASE_STYLESHEET`
- Verify Ctrl+Q still quits the application (may need to re-add as a global shortcut on the QMainWindow if it was only attached to the menu action)
- Verify the About dialog is accessible via the sidebar footer (BEAN-055 dependency)
- Remove unused QMenuBar/QAction imports if no longer needed
- Update any tests that reference the menu bar

### Out of Scope
- Adding a replacement toolbar or hamburger menu
- Adding new keyboard shortcuts beyond Ctrl+Q
- Changing the window title bar or frame decorations

## Acceptance Criteria

- [ ] No QMenuBar is visible in the application window
- [ ] Ctrl+Q still closes the application
- [ ] About dialog is still accessible (via sidebar footer from BEAN-055)
- [ ] No dead code: `_build_menu_bar`, menu bar stylesheet rules, and unused imports are removed
- [ ] Window has a clean top edge — content starts immediately below the title bar
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-055 (Sidebar Navigation Modernization) which adds the sidebar footer with the About dialog trigger. Without BEAN-055, removing the menu bar would leave the About dialog inaccessible.
- Depends on BEAN-054 (Theme Wiring Fix) for baseline theme rendering.
- Execution order: BEAN-054 first, then BEAN-055, then BEAN-061.
- The `_build_menu_bar` method is at `foundry_app/ui/main_window.py:168-181`.
- Ctrl+Q shortcut is currently wired via `QAction.setShortcut("Ctrl+Q")` on the menu action (line 174). After removing the menu, this needs to be re-attached as a `QShortcut` on the main window directly.
- BEAN-036 (Update About Dialog Text) should be done before or alongside this bean, since the About dialog location is changing.

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

> Duration backfilled from git timestamps (commit→merge, 6s).
