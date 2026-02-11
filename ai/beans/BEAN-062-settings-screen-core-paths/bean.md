# BEAN-062: Settings Screen — Core Paths

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-062 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

There is no Settings screen in the application. The sidebar shows a "Settings" placeholder but clicking it displays a static label instead of any functional UI. Without a Settings screen, users cannot configure the library root path — which means the Library Manager screen (already fully implemented) has no way to know where the library lives and always shows an empty state. The `FoundrySettings` class in `foundry_app/core/settings.py` already supports `library_root`, `workspace_root`, and `recent_libraries` via QSettings, but there is no UI to set these values.

## Goal

Create a functional `settings_screen.py` with the core path configuration needed to unblock the rest of the app. Users can set their library root and workspace root via browse dialogs, see a recent-libraries dropdown for quick switching, and have their choices persisted across sessions.

## Scope

### In Scope
- Create `foundry_app/ui/screens/settings_screen.py` as a QWidget
- Library root path field with a "Browse..." button (QFileDialog directory picker)
- Recent libraries dropdown (populated from `FoundrySettings.recent_libraries`)
- Workspace root path field with a "Browse..." button
- Persist all values via `FoundrySettings` on change
- Emit a signal (e.g. `settings_changed`) when library root changes so other screens can react
- Style the screen to match the existing dark theme constants from `foundry_app/ui/theme.py`
- Add tests for the new screen

### Out of Scope
- Generation defaults (overlay mode, strictness) — that is a separate bean
- Safety config defaults — separate bean
- Appearance settings (theme toggle, font size) — separate bean
- Wiring into main_window.py — that is the screen wiring bean

## Acceptance Criteria

- [ ] `settings_screen.py` exists and is importable
- [ ] Library root field with browse button opens a directory picker
- [ ] Selecting a directory updates `FoundrySettings.library_root` and adds to recent libraries
- [ ] Recent libraries dropdown shows previously-used library paths
- [ ] Workspace root field with browse button opens a directory picker
- [ ] Values persist across app restarts (QSettings)
- [ ] A signal is emitted when library_root changes
- [ ] Screen is styled with theme constants (dark background, brass accents)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- `FoundrySettings` already has `library_root`, `workspace_root`, `recent_libraries`, and `add_recent_library()` — the UI just needs to call these.
- This bean is a prerequisite for the screen wiring bean and for the Library Manager to function.
- The settings_changed signal should carry enough info for main_window to pass the new library_root to LibraryManagerScreen.set_library_root().

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

> Duration backfilled from git timestamps (commit→merge, 36s).
