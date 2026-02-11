# BEAN-017: App Shell & Main Window

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-017 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

There is no PySide6 application skeleton — no main window, no navigation, no entry point. The wizard pages and screens have nowhere to live until the app shell is built.

## Goal

Build the PySide6 application skeleton: main window with navigation, stacked widget for screens, settings infrastructure, logging setup, and both GUI and module entry points.

## Scope

### In Scope
- `foundry_app/main.py` — QApplication setup, MainWindow creation, app launch
- `foundry_app/__main__.py` — module entry point
- `foundry_app/ui/main_window.py` — MainWindow with navigation and stacked widget for screens
- `foundry_app/core/settings.py` — QSettings-backed persistent user preferences
- `foundry_app/core/logging.py` — structured logging with rotation
- Navigation structure that can host wizard pages and other screens
- Professional look and feel (stylesheet, spacing, typography)
- pyproject.toml entry points for `foundry` GUI command

### Out of Scope
- Individual wizard pages (separate beans)
- Library browser screens (deferred)
- Service implementations

## Acceptance Criteria

- [x] `uv run foundry` launches a PySide6 window
- [x] Main window has a navigation mechanism to switch between screens
- [x] Stacked widget can host placeholder screens
- [x] Settings persist across app restarts (library_root, workspace_root, etc.)
- [x] Logging writes to rotating log file
- [x] App has a polished, professional appearance
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Build main window and navigation | developer | — | Done |
| 2 | Implement settings and logging | developer | — | Done |
| 3 | Set up entry points and verify launch | tech-qa | 1, 2 | Done |

## Notes

Depends on BEAN-016 (Core Data Models). The main window should be designed to accommodate the 6-page wizard flow defined in BEAN-019 through BEAN-024.

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

> Duration backfilled from git timestamps (commit→merge, 21s).
