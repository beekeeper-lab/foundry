# BEAN-287: Generation Failure Recovery — Sticky Banner + Auto-Scroll

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-287 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-05-01 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |
| **Depends On** | — |

## Problem Statement

When generation fails on the progress screen, the failure summary and the **Back to Builder** button appear at the bottom of the page, below the log box. On a smaller window the button is below the visible fold and the user cannot find a way back to the wizard.

The button **is wired correctly** — `generation_progress.py:331` connects `_back_btn` to `back_requested`, and `main_window.py:300` routes that to `_on_back_to_builder`, which preserves wizard state. The bug is purely visibility: the user doesn't see the recovery affordance.

Observed 2026-05-01: a real generation failure (BEAN-262 mutually-exclusive hook pack check) showed only the pipeline stages list and the log box on the progress screen; the Back to Builder button was off-screen below the log.

## Goal

When generation fails, the failure summary and the "Back to Builder" recovery affordance are **immediately visible** without scrolling, regardless of window size.

## Scope

### In Scope

- Move the failure summary + "Back to Builder" button into a **sticky banner at the top** of `GenerationProgressScreen`, rendered only when `finish_with_error()` fires.
- Keep the log box where it is — users still want to see the log, but they shouldn't have to scroll to see the recovery path.
- As a safety net (in case the layout is constrained), call `ensureWidgetVisible(self._back_btn)` (or equivalent) inside `finish_with_error()` so the button auto-scrolls into view even if the banner is preempted by a custom theme.
- Apply the same banner pattern when generation succeeds — the success summary and "Back to Builder" / "Open Project Folder" buttons should also be top-sticky for consistency.

### Out of Scope

- Re-running generation from the progress screen (a "Retry" button is a separate enhancement).
- Restructuring the pipeline-stages list.
- Adding a global toolbar (covered under BEAN-288 if relevant).
- Changing the failure messages themselves (BEAN-286 covers source-of-truth message improvements at the wizard level; this bean only handles the progress-screen presentation).

## Acceptance Criteria

- [ ] (test:tests/test_generation_progress.py) When `finish_with_error()` fires, the sticky banner is at the top of the visible scroll area and contains the failure summary plus the Back to Builder button.
- [ ] (test:tests/test_generation_progress.py) When `finish()` (success) fires, the sticky banner shows the success summary and recovery actions.
- [ ] Manual GUI verification: trigger a generation failure → failure banner is visible at the top of the screen without scrolling.
- [ ] Manual GUI verification: restore window to a smaller size (~600px tall); the Back to Builder button remains visible after `finish_with_error`.
- [ ] (test:tests/) All tests pass (`uv run pytest`).
- [ ] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks populated by Team-Lead. Likely wave: Developer (banner widget + layout reshuffle in `generation_progress.py`), Tech-QA (visibility tests + manual verification).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**The button works; it's just hidden.** This is purely a layout/visibility fix. The signal wiring is already correct — do not change it.

**Sticky-banner pattern reusable.** If a layout helper falls out of this bean (a generic "top-of-scroll status banner"), document it lightly in `foundry_app/ui/components/` so future screens with success/failure states can adopt it.

**Wizard state preserves on Back.** Verified `_on_back_to_builder` in `main_window.py:471` does not call `reset_wizard()`. Selections persist. No additional state-preservation work needed in this bean — pairs nicely with BEAN-288's broader sidebar-navigation preservation.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | — |
| **Bounces** | 0 (Tech-QA → Developer kicks) |
| **Scope changes** | 0 (in-flight scope edits) |
| **Contract violations** | 0 (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
| **Dispatch mode** | — |
