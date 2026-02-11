# BEAN-048: Wizard Card Components Restyle

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-048 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard's card-based selection pages (persona, stack, architecture, hooks) use inline Catppuccin styling with purple selection borders. Each page defines its own card stylesheet independently, leading to subtle inconsistencies. The cards need to shift to brass/gold selection accents and a more industrial feel — sharper edges, better visual hierarchy between selected and unselected states.

## Goal

Restyle all card components across the 4 card-based wizard pages using the centralized theme. Cards should feel like precision components in a control panel: clear selected/unselected distinction with brass/gold highlights, clean hover states, and consistent styling across all card types.

## Scope

### In Scope
- Replace inline stylesheets in:
  - `persona_page.py` — PersonaCard
  - `stack_page.py` — StackCard
  - `architecture_page.py` — ArchitectureCard
  - `hook_safety_page.py` — HookPackCard, SafetyPolicySection, preset buttons
- Use theme constants for all colors, spacing, border-radius
- Card states:
  - Default: dark surface, subtle border
  - Hover: slightly lighter border, subtle lift
  - Selected: brass/gold left-border accent or full border highlight
  - Disabled: muted, reduced opacity feel
- Badge styling (file counts, template counts) using theme secondary accent
- Checkbox and combo box styling within cards
- Section headers (architecture categories, safety policy groups) using steel blue
- Move Up / Move Down buttons in stack page using theme button styles
- Update tests if structural changes affect them

### Out of Scope
- Project page form inputs (BEAN-049)
- Review page (BEAN-051)
- Adding new card features or changing card behavior
- Icon integration in cards (can be done as follow-up after BEAN-047)

## Acceptance Criteria

- [ ] All 4 card-based pages use `theme.py` constants — no inline hex values
- [ ] Cards have brass/gold selection accent (consistent across all card types)
- [ ] Hover states provide clear feedback without being distracting
- [ ] Section headers use steel blue accent consistently
- [ ] Badge styling is uniform across persona, stack, and hook cards
- [ ] Visual hierarchy is clear: selected cards are immediately distinguishable
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-045 (theme foundation)
- This is the highest-touch bean — 4 files, many card variants
- Consider a shared card base style from theme.py that each page extends
- The hook/safety page is the most complex (615 lines) — handle with care
- Test visually by running wizard: `uv run foundry`

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 6m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 6m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 391s).
