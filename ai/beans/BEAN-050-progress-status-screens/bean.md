# BEAN-050: Progress & Status Screens Restyle

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-050 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | Developer |
| **Category** | App |

## Problem Statement

The generation progress screen, export screen, and history screen use inline Catppuccin styling with purple progress bars and purple button accents. The progress indicators use Unicode bullets for status. These screens should convey "deterministic, calm" progress and feel like monitoring a build pipeline in a control room.

## Goal

Restyle the three operational screens (generation progress, export, history) to match the industrial theme. Progress bars should use brass/gold fill. Status indicators should be clear and calm. The history split-pane should feel like a log viewer. The export screen should feel like a precise export control panel.

## Scope

### In Scope
- Replace inline stylesheets in:
  - `generation_progress.py` — progress bar, stage status widgets, log area, completion summary
  - `export_screen.py` — project list, format selector, export button, status
  - `history_screen.py` — run list, manifest detail viewer, regenerate button
- Progress bar: brass/gold fill on dark surface, clean radius
- Stage status indicators: replace Unicode bullets with themed indicators (or prep for BEAN-047 icons)
- Log area: monospace font, dark surface, blueprint-blue feel
- QListWidget items: consistent dark styling with brass/gold selection
- Buttons: primary (brass/gold) and secondary (steel blue) using theme styles
- Split-pane styling in history screen: clean separator, proper proportions
- Status messages: success=restrained green, error=muted red, using theme constants

### Out of Scope
- Changing screen behavior or adding features
- Icon integration (BEAN-047 follow-up)
- Wizard pages (BEAN-048, BEAN-049, BEAN-051)

## Acceptance Criteria

- [x] All 3 screens use `theme.py` constants — no inline hex values
- [x] Progress bar uses brass/gold fill color
- [x] Stage status indicators are clear and calm (no flashy animations)
- [x] Log area uses monospace font with dark industrial styling
- [x] List selections use brass/gold highlight consistently
- [x] Buttons match theme primary/secondary styles
- [x] History split-pane has clean visual separation
- [x] Overall feel is "monitoring a build pipeline" — deterministic, trustworthy
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-045 (theme foundation)
- The generation progress screen is where users spend time waiting — it should feel calm and informative
- Style guide: "Long-running operations should show clear status and deterministic progress"
- The history screen's manifest JSON viewer could benefit from basic syntax highlighting matching the theme
