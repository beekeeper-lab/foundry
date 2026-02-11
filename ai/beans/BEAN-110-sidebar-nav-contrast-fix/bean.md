# BEAN-110: Sidebar Nav Button Contrast Fix

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-110 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-10 |
| **Started** | 2026-02-10 20:09 |
| **Completed** | 2026-02-10 20:11 |
| **Duration** | 2m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The sidebar navigation buttons (Builder, Library, History, Settings) display with a light/white background that clashes with the dark theme. The text labels have poor contrast — light gray on near-white — making them hard to read. Previous attempts (BEAN-046, BEAN-060, BEAN-076) addressed sidebar styling but the `.nav-button` property-class selector does not fully override `QToolButton`'s default platform styling, leaving the buttons looking out of place.

## Goal

Sidebar nav buttons should have a dark background that blends seamlessly with the sidebar panel, with light text that has strong contrast. The active/selected button should have a bold, clearly distinct highlight (accent background fill + left border indicator). The sidebar should feel cohesive with the rest of the dark industrial theme.

## Scope

### In Scope
- Fix QToolButton stylesheet selectors in `main_window.py` so the dark theme actually applies (may need `QToolButton` type selector instead of or in addition to `.nav-button` class selector)
- Dark background for unselected buttons matching `BG_INSET` (`#141424`) sidebar
- Light text (`TEXT_PRIMARY` / `TEXT_SECONDARY`) with good contrast on dark background
- Bold highlight for active/selected button: accent-colored background fill (e.g., `BG_SURFACE` or slightly brighter) plus left border indicator
- Hover state with visible feedback on the dark background
- Ensure icons remain visible (may need to re-tint for contrast)

### Out of Scope
- Changing the sidebar width or layout structure
- Adding new navigation items
- Changing the icon set
- Theme color palette changes (use existing `theme.py` constants)

## Acceptance Criteria

- [x] Unselected nav buttons have a dark background (no light/white bleed-through)
- [x] Button text labels are clearly readable with strong contrast against the dark background
- [x] Selected/active button has a visually distinct bold highlight (accent fill + left border)
- [x] Hover state provides visible feedback without clashing with the dark palette
- [x] Icons are visible and properly tinted on the dark background
- [x] Sidebar looks cohesive — no visual seam between buttons and sidebar background
- [x] All existing tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Fix nav button stylesheet selectors | Developer | — | Done |
| 2 | Run tests and lint | Tech-QA | 1 | Done |

## Notes

- Root cause is likely that `QToolButton` has platform-specific default styling that the property-based `.nav-button` class selector cannot fully override. Fix may require using `QToolButton` as the type selector (e.g., `QToolButton#sidebar QToolButton` or `#sidebar QToolButton`) for full specificity.
- Previous related beans: BEAN-046 (Main Window & Sidebar Restyle), BEAN-060 (Sidebar Navigation Modernization), BEAN-076 (Sidebar Nav Button Restyle)
- Key files: `foundry_app/ui/main_window.py` (lines 36-111 stylesheet, lines 208-226 button construction), `foundry_app/ui/theme.py`

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 2m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 4s).
