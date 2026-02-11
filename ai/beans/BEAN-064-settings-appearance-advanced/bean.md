# BEAN-064: Settings Screen — Appearance & Advanced

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-064 |
| **Status** | Done |
| **Priority** | Low |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Users have no control over the application's visual preferences or advanced behavior. The dark industrial theme is the only option, and there is no way to adjust font size for accessibility, reset all settings to defaults, or view application version and diagnostic info from within the Settings screen itself.

## Goal

Add an "Appearance" section and an "Advanced" section to the Settings screen, giving users control over visual preferences and providing a clean way to reset configuration or view app diagnostics.

## Scope

### In Scope
- Add an "Appearance" group to the Settings screen:
  - Font size preference (Small / Medium / Large) that scales the base font
  - Theme selection placeholder (Dark only for now, but wired for future Light mode)
- Add an "Advanced" group:
  - "Reset All Settings" button with confirmation dialog
  - Application version display
  - Configuration file location display (QSettings path)
  - Log file location with "Open Log" button
- Persist appearance values via FoundrySettings
- Apply font size preference on change (live preview)
- Add tests

### Out of Scope
- Implementing a full Light theme (just the dropdown placeholder)
- Custom color picker or palette editor
- Plugin or extension settings

## Acceptance Criteria

- [ ] Settings screen has an "Appearance" section with font size selector
- [ ] Font size change takes effect immediately in the running app
- [ ] Settings screen has an "Advanced" section with reset, version, and log path
- [ ] "Reset All Settings" clears QSettings and restores defaults after confirmation
- [ ] "Open Log" button opens the log file in the system's default text editor
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-057 (Settings Screen — Core Paths) so the settings_screen.py file exists.
- Font size scaling should multiply the theme's FONT_SIZE_* constants by a factor (0.85 / 1.0 / 1.15).
- The log file path is set in `foundry_app/core/logging_config.py` — currently `~/.local/share/logs/foundry.log`.
- Low priority because the app is fully functional without these features.

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
