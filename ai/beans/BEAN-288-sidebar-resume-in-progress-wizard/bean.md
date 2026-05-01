# BEAN-288: Sidebar Navigation Preserves and Surfaces In-Progress Wizard State

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-288 |
| **Status** | Unapproved |
| **Priority** | Medium |
| **Created** | 2026-05-01 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |
| **Depends On** | — |

## Problem Statement

When a user is mid-wizard (e.g., on the Review step) and clicks a sidebar item — Library, History, Settings — they leave the wizard. The only way back is to click **New Project**, but that label suggests *starting over*. In reality the wizard's selections are preserved (`_on_back_to_builder` in `main_window.py:471` does not call `reset_wizard()`), so clicking "New Project" silently drops them back at the step they were on. The label and the behavior disagree.

Observed 2026-05-01: after hitting a generation error and clicking Settings to investigate, the user reported "now I definitely don't see the ability to get back into the project creation workflow." When prompted to click "New Project," they returned to the in-progress wizard at the Review step — but the path was non-obvious and the labeling implied destruction of state.

This is a real UX trap: the application looks like it threw away the user's work, even though it didn't.

## Goal

A user navigating away from an in-progress wizard via the sidebar can **see at a glance** that the wizard has unsaved/in-progress state, and **return to it without ambiguity** about whether they're starting over.

## Scope

### In Scope

- **Sidebar label is dynamic when the wizard has state.**
  - When the wizard is at step 0 with no selections: label reads "**New Project**" (current behavior).
  - When the wizard has any non-default state (any persona selected, any expertise picked, etc.): label reads "**Resume Project**" (or "**Continue Project**").
  - Add a small visual indicator (a dot, an asterisk, or different accent color) so the in-progress state is recognizable without reading.
- **In-progress detection** — a `BuilderScreen.has_in_progress_state()` method that returns True when the user has made any selection beyond defaults. Keep the heuristic simple: any persona selected OR project name entered OR step > 0.
- **Explicit "Start Over" action** somewhere visible (a small button in the wizard's header, or a menu item). Calls the existing `BuilderScreen.reset_wizard()`. The current behavior is "to start over, click somewhere else and come back" which is not discoverable.
- **Tests** for the dynamic label, the indicator, and the explicit Start Over action.

### Out of Scope

- Persisting wizard state across application restarts (an interesting follow-up; do not bundle here).
- Multiple concurrent in-progress projects (the wizard is single-instance).
- A separate "Drafts" screen (also a follow-up, not now).
- Auto-saving wizard state to disk on every change.
- Changing how `_on_back_to_builder` works — it already preserves state correctly.

## Acceptance Criteria

- [ ] (test:tests/test_main_window.py) Sidebar "New Project" label switches to "Resume Project" when `has_in_progress_state()` returns True.
- [ ] (test:tests/test_main_window.py) An in-progress visual indicator (dot/asterisk/accent) is present on the sidebar entry when the wizard has state.
- [ ] (test:tests/test_builder_screen.py) `BuilderScreen.has_in_progress_state()` returns False at fresh start and after `reset_wizard()`; returns True after any persona is selected.
- [ ] (test:tests/test_builder_screen.py) Explicit "Start Over" action exists, is reachable from the wizard, and calls `reset_wizard()`.
- [ ] Manual GUI verification: select a persona → sidebar label changes; click Settings → return via sidebar; the renamed label clearly indicates state is preserved.
- [ ] Manual GUI verification: click "Start Over" → wizard returns to step 0 with empty selections.
- [ ] (test:tests/) All tests pass (`uv run pytest`).
- [ ] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks populated by Team-Lead. Likely wave: BA (decide exact label wording — "Resume" vs "Continue" — and indicator style), Developer (sidebar wiring + in-progress detection + Start Over button), Tech-QA (state-transition tests + manual flow verification).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**BA value-add here.** The label wording ("Resume Project" vs "Continue Project" vs "Builder (in progress)") is a real user-language decision. The indicator visual (dot vs asterisk vs accent) is also user-facing. One short BA pass before Developer implementation is worth it.

**Pairs with BEAN-287.** Both are about "find your way back to in-progress work." Land in any order; they don't conflict on code.

**No state persistence across restarts.** Out of scope. If the user closes the app, wizard state is lost. That's a separate question — file as a follow-up if it matters.

**Don't auto-warn on navigation away.** A confirmation dialog ("you'll lose your changes!") is **not** the goal here — wizard state is already preserved on sidebar nav. The fix is making that preservation visible, not adding friction.

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
