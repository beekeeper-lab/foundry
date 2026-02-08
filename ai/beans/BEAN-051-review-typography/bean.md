# BEAN-051: Review Page & Typography System

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-051 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The review page displays a read-only summary of the full composition spec before generation. Currently it uses color alone for hierarchy (blue headers, white text, gray labels). The style guide calls for "use weight and spacing for hierarchy instead of color alone." The Generate button is the most important action in the entire app — it should be visually prominent but not flashy. Typography across the app lacks a systematic approach.

## Goal

Restyle the review page with proper typography hierarchy using font weight, size, and spacing. Apply the industrial theme with brass/gold accents for the Generate action. Establish typography patterns that reinforce the "precision workshop" feel: dense information, clean layout, clear hierarchy.

## Scope

### In Scope
- Replace inline stylesheets in `review_page.py`
- Typography hierarchy for review sections:
  - Section headers: bold, steel blue accent, slightly larger, letter-spaced
  - Field labels: semi-bold, muted tone, uppercase or small-caps
  - Field values: normal weight, primary text color
  - Bullet items: clean list formatting with proper indentation
- Generate button: brass/gold, prominent but restrained, clear hover/disabled states
- Section separators: subtle horizontal rules or spacing between review sections
- Apply typography scale from theme.py consistently
- Ensure monospace is used for any generated file paths or code-like content in the review

### Out of Scope
- Changing what data is shown in the review
- Card components (BEAN-048)
- Form inputs (BEAN-049)
- Adding features to the review page

## Acceptance Criteria

- [ ] `review_page.py` uses `theme.py` constants — no inline hex values
- [ ] Typography hierarchy uses weight and spacing, not just color
- [ ] Section headers are visually distinct from field labels and values
- [ ] Generate button uses brass/gold accent and is the clear primary action
- [ ] Monospace font used for code-like content (paths, file names)
- [ ] Dense information display with clean layout — no wasted space
- [ ] The page feels like a "pre-flight checklist" — structured, precise, confident
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
- The review page is the last step before generation — it's the "launch sequence confirmation"
- Style guide: "Clarity over decoration — dense information, but clean layout"
- The Generate button is the single most important action in the app — give it appropriate weight
