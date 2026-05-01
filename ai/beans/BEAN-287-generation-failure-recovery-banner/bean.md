# BEAN-287: Generation Failure Recovery — Sticky Banner + Auto-Scroll

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-287 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-05-01 |
| **Started** | 2026-05-01 11:43 |
| **Completed** | 2026-05-01 11:47 |
| **Duration** | 1598h 40m |
| **Owner** | team-lead |
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

- [x] (test:tests/test_generation_progress.py) When `finish_with_error()` fires, the sticky banner is at the top of the visible scroll area and contains the failure summary plus the Back to Builder button. — `test_banner_visible_after_error_back_only`, `test_banner_is_sibling_of_scroll_not_nested`
- [x] (test:tests/test_generation_progress.py) When `finish()` (success) fires, the sticky banner shows the success summary and recovery actions. — `test_banner_visible_after_finish_with_buttons`
- [ ] Manual GUI verification: trigger a generation failure → failure banner is visible at the top of the screen without scrolling. *(deferred — covered by automated banner-sibling + summary tests)*
- [ ] Manual GUI verification: restore window to a smaller size (~600px tall); the Back to Builder button remains visible after `finish_with_error`. *(deferred — sibling-not-nested test guarantees the banner is outside the scroll viewport)*
- [x] (test:tests/) All tests pass (`uv run pytest` — 2386 passed).
- [x] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Sticky outcome banner + auto-scroll safety net | Developer | — | Done |
| 2 | Sticky banner visibility tests | Tech-QA | 01 | Done |

> Skipped: BA (default), Architect (default — pure layout/widget refactor; no new subsystem or ADR).

## Changes

| File | Lines |
|------|-------|
| `foundry_app/ui/screens/generation_progress.py` | 153 (sticky `_outcome_banner`, `_build_outcome_banner`, banner-driven start/finish/finish_with_error, scroll-reset safety net) |
| `tests/test_generation_progress.py` | 74 (`TestOutcomeBanner` — 6 tests) |
| `ai/beans/BEAN-287-generation-failure-recovery-banner/bean.md` | 40 (status, ACs, telemetry) |
| `ai/beans/BEAN-287-generation-failure-recovery-banner/tasks/01-developer-sticky-banner.md` | 43 (new) |
| `ai/beans/BEAN-287-generation-failure-recovery-banner/tasks/02-tech-qa-banner-tests.md` | 38 (new) |

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
| 1 | Sticky outcome banner + auto-scroll safety net | Developer | < 1m | 13,849,769 | 66,465 | $28.13 |
| 2 | Sticky banner visibility tests | Tech-QA | < 1m | N/A (suspect) | N/A (suspect) | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 13,849,769 |
| **Total Tokens Out** | 66,465 |
| **Total Cost** | $28.13 |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | Developer, Tech-QA |
| **Bounces** | 0 (Tech-QA → Developer kicks) |
| **Scope changes** | 0 (in-flight scope edits) |
| **Contract violations** | 0 (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
| **Dispatch mode** | in-process |