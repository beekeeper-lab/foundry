# Task 01 — BA: label wording + indicator style decisions

| Field | Value |
|-------|-------|
| **Owner** | BA |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 11:50 |
| **Completed** | 2026-05-01 11:50 |
| **Duration** | < 1m |

## Goal

Lock the user-language and visual decisions before Developer touches code. Two open questions in BEAN-288:

1. Sidebar label wording when wizard has in-progress state.
2. Visual-indicator style (dot vs asterisk vs accent).

## Decisions

### Label wording: **"Resume Project"**

- Considered: "Continue Project", "Resume Project", "Builder (in progress)".
- Pick **"Resume Project"** because:
  - It is the inverse pair of "New Project" — same nominal phrase, reads as "go back to the one in progress."
  - "Continue" is ambiguous in builder UIs (continue stepping forward inside the wizard vs come back to it from elsewhere).
  - Parenthetical state ("Builder (in progress)") is fragile under width constraints and reads as a status badge, not an action.
- The current default ("New Project") stays as-is when there is no in-progress state.

### Indicator style: **small accent-colored dot, top-right of the icon**

- Considered: dot, asterisk, swapped accent color, animated badge.
- Pick **a small filled dot in `ACCENT_PRIMARY`** rendered as a Qt-painted overlay on top of the icon's top-right corner because:
  - It is the most universally-recognized "unsaved/in-progress" affordance (matches macOS/IDE conventions).
  - It does not require a second SVG asset — keeps the implementation cheap.
  - Asterisks read as "required field" or "footnote" in form contexts; we don't want that ambiguity.
  - Recoloring the whole icon would conflict with the theme's stated "checked / hover" treatments and would surprise users.
- Size: ~6-8 px. Position: top-right corner with ~4 px inset.

### "Start Over" affordance

- Place a small ghost button labeled **"Start Over"** in the wizard's header / nav row (next to Back).
- Tooltip: "Reset wizard — clear all selections."
- Behavior: clears all wizard-page state and returns to step 0 (calls `BuilderScreen.start_over()`).
- Visible only when `has_in_progress_state()` is True (no point cluttering the UI when there is nothing to reset).

## Acceptance Criteria

- [x] Wording fixed: "Resume Project".
- [x] Indicator fixed: small accent-colored dot, top-right inset.
- [x] Start Over affordance fixed: ghost button in wizard header, visible only when state exists.

## Definition of Done

- [x] Decisions documented here for the developer task to consume.
- [x] No further BA back-and-forth required to start implementation.
