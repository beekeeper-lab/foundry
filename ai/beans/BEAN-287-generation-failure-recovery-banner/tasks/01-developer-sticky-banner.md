# Task 01 — Developer: sticky outcome banner + auto-scroll safety net

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 11:47 |
| **Completed** | 2026-05-01 11:47 |
| **Duration** | < 1m |

## Goal

Move the success/failure summary and the "Back to Builder" + "Open Project Folder" buttons into a sticky banner at the top of `GenerationProgressScreen`, above the scroll area. Add an `ensureWidgetVisible` safety-net call so the recovery affordance stays in view even on small windows or under custom themes.

## Inputs

- `ai/beans/BEAN-287-generation-failure-recovery-banner/bean.md` — bean spec
- `foundry_app/ui/screens/generation_progress.py` — `GenerationProgressScreen.__init__()` lines 174-334; `finish()` 428-458; `finish_with_error()` 460-471; `start()` 375-396
- `tests/test_generation_progress.py` — existing tests for finish/finish_with_error/back-button visibility (around lines 200-260)

## Acceptance Criteria

- [ ] `__init__` builds a `_outcome_banner: QFrame` in the outer layout **above** the `QScrollArea`. Banner contains the summary label and an action row holding Back to Builder + Open Project Folder. Banner is `setVisible(False)` until `finish` / `finish_with_error` fires.
- [ ] `_summary_label`, `_back_btn`, `_open_btn` are children of the banner, not the scroll-area container. The duplicate copies inside the scroll-area `layout` are removed.
- [ ] `finish(...)` populates summary (success styling), shows the banner, shows both buttons.
- [ ] `finish_with_error(...)` populates summary (error styling), shows the banner, shows the Back button, hides the Open button.
- [ ] `start()` hides the banner so a fresh run does not display the prior outcome.
- [ ] After `finish_with_error`, the screen calls `ensureWidgetVisible(self._back_btn)` (or equivalent — banner.show + scroll-to-top) so the recovery affordance is on-screen even at ~600px window heights.
- [ ] Existing back-button / signal tests continue to pass; their assertions on `_back_btn.isVisible()` and click signal wiring are preserved.

## Definition of Done

- [ ] Code lands; banner visually sits above scroll content.
- [ ] `uv run pytest tests/test_generation_progress.py -q` passes.
- [ ] `uv run ruff check foundry_app/` passes.
- [ ] Status set to `Done`.

## Notes

- The existing back-button signal wiring is correct (`_back_btn.clicked.connect(self.back_requested.emit)`) — preserve it. Bean spec says "the button works; it's just hidden."
- Keep the log box (`self._log`) where it is. Don't restructure the pipeline-stage list.
- `path_label` may stay in the scroll area below; the banner is for the action surface only.
