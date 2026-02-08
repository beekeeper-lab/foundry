# BEAN-047: Icon Set for Industrial Theme

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-047 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The app currently uses Unicode text symbols for all visual indicators (◆ ▲ ▼ ✓ ✗ • –). These look inconsistent across platforms, can't be colored independently, and don't contribute to the industrial-modern aesthetic. Buttons are text-only with no visual affordance beyond the label.

## Goal

Create a small, focused SVG icon set for Foundry and integrate it into the app's resource system. Icons should match the industrial-modern aesthetic — clean, geometric, no-nonsense. Provide a helper in the theme module to load and tint icons at runtime.

## Scope

### In Scope
- SVG icon files in `foundry_app/ui/icons/` (or Qt resource system)
- Core icon set (~15-20 icons):
  - Navigation: builder, history, settings, library
  - Actions: generate, export, add, remove, move-up, move-down, refresh
  - Status: success (check), error (x), warning (alert), pending (circle), running (gear/spinner)
  - UI: expand, collapse, search, folder
- Icon loader utility in `theme.py` or `foundry_app/ui/icons.py`:
  - Load SVG by name
  - Tint to match theme colors (gold for active, gray for inactive, etc.)
  - Return QIcon or QPixmap
- Qt resource file (`.qrc`) if needed, or direct file loading
- Unit tests for icon loading

### Out of Scope
- Actually replacing Unicode symbols in existing UI files (other style beans handle that)
- Animated icons or complex illustrations
- Multiple icon variants (outline/filled/etc.) — one style only
- Custom-drawn icons from scratch — use an open-source icon set as a base (e.g., Lucide, Tabler, Feather) and customize

## Acceptance Criteria

- [ ] SVG icon files exist in a dedicated directory under `foundry_app/ui/`
- [ ] At least 15 icons covering navigation, actions, and status indicators
- [ ] Icons are monochrome SVG, tintable at runtime
- [ ] Icon loader function returns QIcon from icon name
- [ ] Icons are visually consistent — same stroke weight, same grid size
- [ ] Style matches industrial-modern: geometric, clean, not playful
- [ ] Unit tests verify icon loading and tinting
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-045 (theme foundation — for color constants used in tinting)
- Open-source icon sets to consider: Lucide (MIT), Tabler Icons (MIT), Feather (MIT)
- Keep the set small — only icons we actually use. Can expand later.
- Icons should work at 16px and 24px sizes
- Consider using Qt's SVG support (`QSvgRenderer` or `QIcon.addFile`) for crisp rendering at any DPI
