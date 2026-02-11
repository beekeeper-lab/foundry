# BEAN-065: Wire Screens into Main Window

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-065 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The main window currently displays placeholder widgets for all 4 sidebar tabs (Builder, Library, History, Settings). The actual screen implementations exist — LibraryManagerScreen, HistoryScreen, ExportScreen, and GenerationProgressScreen are fully coded — but none are instantiated or added to the QStackedWidget. Users click sidebar tabs and see static labels instead of functional screens. This makes the entire application appear unfinished despite the screens being complete.

## Goal

Replace all placeholder widgets in `main_window.py` with the real, implemented screen classes. When users click a sidebar tab, they see the actual functional screen. The Library Manager receives the library root from Settings. The History screen shows past generation runs. The Settings screen allows configuration. The app feels like a complete, working application.

## Scope

### In Scope
- Replace the Library tab placeholder with `LibraryManagerScreen`
- Replace the History tab placeholder with `HistoryScreen`
- Replace the Settings tab placeholder with `SettingsScreen` (from BEAN-057)
- Connect `SettingsScreen.settings_changed` signal to update LibraryManagerScreen's library root
- On startup, read `FoundrySettings.library_root` and pass it to LibraryManagerScreen
- Remove the `_placeholder()` helper function (no longer needed)
- Ensure screen switching works correctly (QStackedWidget index mapping)
- Add/update tests for screen instantiation and navigation

### Out of Scope
- Builder wizard wiring — that is BEAN-061 (separate, more complex)
- Theme wiring — that is BEAN-054
- Sidebar modernization — that is BEAN-055
- Export screen wiring (triggered from History/Generation, not a sidebar tab)

## Acceptance Criteria

- [ ] Clicking "Library" shows the real LibraryManagerScreen with tree browser
- [ ] Clicking "History" shows the real HistoryScreen with generation run list
- [ ] Clicking "Settings" shows the real SettingsScreen with path configuration
- [ ] Changing library root in Settings immediately updates the Library Manager tree
- [ ] Library root persists across app restarts (set in Settings, visible in Library on relaunch)
- [ ] No placeholder widgets remain for Library, History, or Settings tabs
- [ ] Builder tab still works (placeholder or wizard, depending on BEAN-061 status)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-057 (Settings Screen — Core Paths) for SettingsScreen to exist.
- Depends on BEAN-054 (Theme Wiring Fix) so the dark theme renders when screens are shown.
- The Builder tab can remain as a BrandedEmptyState placeholder until BEAN-061 wires the wizard.
- The `_placeholder()` function is defined around line 160 of main_window.py and used in `_init_screens()` around line 210.
- LibraryManagerScreen exposes `set_library_root(path)` and auto-refreshes on `showEvent`.
- HistoryScreen and ExportScreen may need a workspace_root to locate manifest files — check their constructors.

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

> Duration backfilled from git timestamps (commit→merge, 7s).
