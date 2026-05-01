# Task 02 — Developer: dynamic sidebar + has_in_progress_state + Start Over

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-05-01 11:54 |
| **Completed** | 2026-05-01 11:54 |
| **Duration** | < 1m |

## Goal

When the wizard has any non-default state, the sidebar shows the user how to return to it (renamed icon + dot indicator), and the wizard itself surfaces an explicit "Start Over" action that resets the state.

## Inputs

- `ai/beans/BEAN-288-sidebar-resume-in-progress-wizard/bean.md`
- `ai/beans/BEAN-288-sidebar-resume-in-progress-wizard/tasks/01-ba-label-decision.md` — locks wording + visuals
- `foundry_app/ui/main_window.py` — sidebar nav button construction (lines 207-244 build nav buttons; the builder button is at index 0)
- `foundry_app/ui/screens/builder_screen.py` — wizard owner; `reset_wizard()` exists at line 200 but only resets the page index, not selections
- `foundry_app/ui/icons/builder.svg` — contains the literal "New Project" text that gets rendered into the sidebar button's icon

## Acceptance Criteria

### `BuilderScreen.has_in_progress_state()`
- [ ] New method returns True when any of: a project name is entered, any persona is selected, any expertise is selected, any architecture choice is set, or the page index is > 0.
- [ ] Returns False at fresh start and after `start_over()`.
- [ ] Emits a `state_changed: Signal` whenever the answer would change (wired to existing per-page `selection_changed` / text-changed signals).

### `BuilderScreen.start_over()`
- [ ] New method clears each page's state (project name, persona selection, expertise selection, architecture, hooks page is left at safe defaults) and returns to step 0.
- [ ] After call, `has_in_progress_state()` returns False.

### Wizard "Start Over" button
- [ ] New ghost-style button in the wizard's nav row labeled "Start Over". Visible only when `has_in_progress_state()` is True; hidden otherwise.
- [ ] Click triggers `start_over()`.

### Sidebar dynamic label + indicator
- [ ] `MainWindow` listens to `BuilderScreen.state_changed` and re-renders the builder nav button when the answer flips.
- [ ] When `has_in_progress_state()` is True: the builder icon's "New Project" text is replaced with "Resume Project" (do this by str-replacing on the SVG bytes before rendering — no second asset).
- [ ] When True: a small filled dot in `ACCENT_PRIMARY` (~7 px) is painted onto the rendered icon at the top-right corner with a small inset.
- [ ] When False: the original icon (with "New Project" text and no dot) is restored.

## Definition of Done

- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check foundry_app/` passes.
- [ ] Status set to `Done`.

## Notes

- Refactor the builder-icon rendering into a small `_render_builder_icon(in_progress: bool) -> QIcon` helper on `MainWindow` so the test surface is small and the code path is unified between construction and dynamic updates.
- Do not introduce a second SVG file — the str-replace approach keeps the asset surface flat.
- Keep `reset_wizard()` semantics for callers that intentionally only want the page-index reset; `start_over()` is the new "clear-and-reset" verb.
