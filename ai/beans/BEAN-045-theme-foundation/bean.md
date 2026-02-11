# BEAN-045: Theme Foundation & Style Constants

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-045 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

All styling in the Foundry app is done via inline `setStyleSheet()` calls with hardcoded hex color values scattered across 10+ UI files. The current Catppuccin Mocha palette uses purple as its primary accent, which doesn't match the industrial-modern brand identity. There is no centralized style system — changing a single color means editing every file.

## Goal

Create a centralized theme module (`foundry_app/ui/theme.py`) that defines the complete visual identity for Foundry: color palette, typography scale, spacing constants, and reusable QSS template strings. The palette shifts from Catppuccin purple to an industrial dark theme with muted brass/warm gold accents and steel blue secondary. All other style beans build on this foundation.

## Scope

### In Scope
- New module `foundry_app/ui/theme.py` with:
  - Color constants (background, surface, border, text, accent-gold, accent-blue, success, error, warning)
  - Typography scale (heading sizes, body, caption, monospace family)
  - Spacing constants (padding, margins, border-radius, border-width)
  - Reusable QSS template strings for common patterns (cards, inputs, buttons, scrollbars, lists)
  - Helper function to apply the global stylesheet to QApplication
- Industrial dark color palette:
  - Background: deep charcoal (#1a1a2e or similar dark navy)
  - Surface: slightly lighter charcoal (#252540 range)
  - Accent primary: muted brass/warm gold (#c9a84c / #d4a843 range)
  - Accent secondary: steel blue/blueprint blue (#5b8fb9 / #4a7fa5 range)
  - Text: high-contrast light (#e0e0e8 range)
  - Success: restrained green, Error: muted red, Warning: amber
- Unit tests for the theme module (constants exist, QSS templates are valid strings, helper applies stylesheet)

### Out of Scope
- Actually restyling any existing UI files (that's BEAN-046 through BEAN-052)
- Icon system (BEAN-047)
- Light theme or theme switching
- Custom fonts (use system sans-serif + system monospace)

## Acceptance Criteria

- [x] `foundry_app/ui/theme.py` exists with all color, typography, and spacing constants
- [x] Color palette is industrial dark with brass/gold primary accent and steel blue secondary
- [x] QSS template strings exist for: card, input, button-primary, button-secondary, scrollbar, list-item, section-header
- [x] `apply_theme(app)` function applies the base stylesheet to a QApplication instance
- [x] All constants are documented with their intended usage
- [x] Unit tests verify constants and QSS templates
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create theme module with constants and QSS | developer | - | Done |
| 2 | Write unit tests | tech-qa | 1 | Done |
| 3 | Run tests and lint | tech-qa | 2 | Done |
| 4 | Commit and merge | team-lead | 3 | Done |

## Notes

- This bean is the foundation for all other style beans (BEAN-046 through BEAN-052)
- The palette should feel like a "precision workshop" or "modern forge" — confident, stable, not playful
- Gold/brass accents are for focus and active states, not decoration — use sparingly
- Existing modules should NOT be modified in this bean — only create the new theme module

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
