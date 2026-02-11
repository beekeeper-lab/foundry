# BEAN-046: Main Window & Sidebar Restyle

**Priority:** High | **Category:** App | **Status:** Done | **Owner:** team-lead
**Depends on:** BEAN-045 (Done)

## Goal

Restyle the main window shell — sidebar navigation, brand header, menu bar, and
overall chrome — using the centralized theme from BEAN-045.

## Acceptance Criteria

- [x] main_window.py uses theme.py constants instead of inline hex values
- [x] Sidebar has distinct visual identity: darker background, clear brand header, brass/gold active state
- [x] Navigation items have hover and selected states using theme colors
- [x] Menu bar and About dialog match the industrial dark theme
- [x] No inline hex color values remain in main_window.py
- [x] Visual result feels like a control room
- [x] All tests pass
- [x] Lint clean

## Changes Made

- Replaced inline STYLESHEET with f-string referencing theme.* constants
- Sidebar: BG_INSET background, ACCENT_PRIMARY (brass/gold) selected state with left border accent
- Brand label: ACCENT_PRIMARY color, BORDER_SUBTLE separator
- Hover states: ACCENT_PRIMARY_HOVER text
- Menu bar: BG_INSET background, BG_SURFACE/BG_OVERLAY for menus
- About dialog: themed with ACCENT_PRIMARY heading
- Zero inline hex color values remain

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 74s).
