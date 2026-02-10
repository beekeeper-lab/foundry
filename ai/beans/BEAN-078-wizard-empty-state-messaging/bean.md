# BEAN-078: Wizard Empty-State Messaging

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-078 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-09 |
| **Completed** | 2026-02-09 |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

When no library is loaded (either because `library_root` isn't configured or the library path is invalid), the Personas, Stacks, and Hook Packs wizard pages show blank content with no explanation. The user sees a heading, a subtitle, and an empty scroll area. Combined with the silent Next button failure (BEAN-077), this creates a completely dead-end experience where the user has no idea what's wrong or how to fix it.

## Goal

When a wizard page has no content because the library isn't loaded, the user sees a clear, actionable message directing them to configure the library root in Settings.

## Scope

### In Scope
- Add an empty-state message to PersonaSelectionPage when `_cards` is empty after `load_personas()` or if never called
- Add an empty-state message to StackSelectionPage when no stacks are loaded
- Add an empty-state message to HookSafetyPage when no hook packs are loaded
- Message text: "No library loaded. Go to Settings and configure your Library Root to populate this page."
- Style the message consistently with the existing warning label style

### Out of Scope
- Auto-navigation to Settings (clicking the message doesn't navigate)
- Inline library path picker on the wizard page itself
- Auto-detection of library root (covered by BEAN-075)

## Acceptance Criteria

- [x] Persona page shows an empty-state message when no personas are loaded
- [x] Stack page shows an empty-state message when no stacks are loaded
- [x] Hook/Safety page shows an empty-state message when no hook packs are loaded
- [x] Empty-state message disappears when library is loaded (e.g., user configures Settings and returns to wizard)
- [x] Message is styled with `TEXT_SECONDARY` color and centered in the scroll area
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add empty-state label to PersonaSelectionPage | team-lead | | Done |
| 2 | Add empty-state label to StackSelectionPage | team-lead | | Done |
| 3 | Add empty-state label to HookSafetyPage | team-lead | | Done |
| 4 | Toggle visibility in load_*() methods | team-lead | 1-3 | Done |
| 5 | Add tests for empty-state visibility | team-lead | 1-4 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- **Key files:** `persona_page.py`, `stack_page.py`, `hook_safety_page.py` in `foundry_app/ui/screens/builder/wizard_pages/`
- The empty-state label should be added to the scroll area container, visible by default, and hidden when `load_*()` populates cards
- This bean is independent of BEAN-075 (auto-detect) — even with auto-detect, the empty-state message is valuable as a fallback when detection fails
- BEAN-077 (disable Next button) complements this — together they provide full feedback for the "no library" case

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
