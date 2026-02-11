# BEAN-059: Theme Wiring Fix

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-059 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The dark industrial theme (defined in `foundry_app/ui/theme.py`) is not rendering in the application. The screenshot shows a white/light sidebar and unstyled menu bar despite a comprehensive dark palette being defined in code. The root cause is that `apply_theme(app)` is never called in `foundry_app/main.py` after creating the QApplication. Additionally, the MainWindow's own stylesheet may have escaping issues with the f-string double-brace pattern (`{{{{`}`) that could prevent proper QSS rendering.

## Goal

The Foundry application renders with its intended dark industrial palette on startup — deep charcoal backgrounds, brass/gold accents, and properly styled sidebar, menu bar, and content areas. No light/white unstyled regions remain.

## Scope

### In Scope
- Add `theme.apply_theme(app)` call in `foundry_app/main.py` after QApplication creation
- Audit the MainWindow `STYLESHEET` f-string escaping to ensure QSS selectors render correctly
- Verify that sidebar, menu bar, content area, and placeholder screens all pick up the dark theme
- Test that the About dialog still works correctly (it has special light-background handling)
- Ensure no regressions in existing styled screens (Builder wizard, Library Manager, etc.)

### Out of Scope
- New icons or icon integration (that's BEAN-060)
- Removing the menu bar (that's BEAN-061)
- Changing the palette colors themselves (BEAN-045 palette is fine)

## Acceptance Criteria

- [x] `apply_theme(app)` is called in `main.py` before MainWindow is shown
- [x] Sidebar renders with dark background (`#141424` BG_INSET) on app startup
- [x] Navigation items show brass/gold accent on selection and hover
- [x] Menu bar renders dark, not light/white
- [x] Content area renders with dark background (`#1a1a2e` BG_BASE)
- [x] About dialog remains readable (dark text on light native background)
- [x] All tests pass (`uv run pytest`) — 1134 passed
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add `theme.apply_theme(app)` to main.py | team-lead | — | Done |
| 2 | Fix About dialog text contrast (dark text on light bg) | team-lead | — | Done |

## Notes

- Fix was adding `from foundry_app.ui import theme` and `theme.apply_theme(app)` in `main.py` after QApplication creation, before any widgets.
- About dialog was also fixed (separate from this bean) — text color changed from theme.TEXT_PRIMARY (light) to #2a2a2a (dark) since QMessageBox.about() uses a native light background.
- Index status discrepancy for BEAN-045/046/047 was reconciled by another agent.

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

> Duration backfilled from git timestamps (single commit, no merge).
