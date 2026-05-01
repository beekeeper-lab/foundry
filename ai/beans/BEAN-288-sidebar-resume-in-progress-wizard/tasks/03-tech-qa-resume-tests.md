# Task 03 — Tech-QA: state-transition tests for sidebar + Start Over

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 02 |
| **Status** | Done |
| **Started** | 2026-05-01 11:54 |
| **Completed** | 2026-05-01 11:54 |
| **Duration** | < 1m |

## Goal

Lock BEAN-288's behavior under tests: in-progress detection, Start Over reset, sidebar label flip, and indicator presence.

## Inputs

- `ai/beans/BEAN-288-sidebar-resume-in-progress-wizard/bean.md` — acceptance criteria
- `ai/beans/BEAN-288-sidebar-resume-in-progress-wizard/tasks/02-developer-resume-sidebar.md` — implementation contract
- `tests/test_builder_screen.py`
- `tests/test_main_window.py`

## Acceptance Criteria

### Builder screen
- [ ] (test:tests/test_builder_screen.py) `has_in_progress_state()` returns False at fresh start.
- [ ] (test:tests/test_builder_screen.py) Returns True after entering a project name; True after selecting a persona; True after navigating past step 0.
- [ ] (test:tests/test_builder_screen.py) `start_over()` returns the wizard to step 0, clears project name, clears persona selection, and afterwards `has_in_progress_state()` is False.
- [ ] (test:tests/test_builder_screen.py) `state_changed` signal fires when the answer flips (entering text, selecting a persona, advancing step).

### Main window
- [ ] (test:tests/test_main_window.py) Builder-button tooltip / accessible name reflects "Resume Project" when wizard has state, "New Project" otherwise. (Tooltip is the cheapest way to verify the rename without rasterizing the icon.)
- [ ] (test:tests/test_main_window.py) An in-progress flag (`_builder_in_progress` attribute or equivalent on `MainWindow`) is True after the wizard goes in-progress and False after `start_over()`.
- [ ] (test:tests/test_main_window.py) The builder button refreshes when `BuilderScreen.state_changed` fires.

### Suite-wide
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check foundry_app/` passes.

## Definition of Done

- [ ] Tests added under existing class structure.
- [ ] Tests are deterministic and offscreen-safe.
- [ ] Status set to `Done`.
