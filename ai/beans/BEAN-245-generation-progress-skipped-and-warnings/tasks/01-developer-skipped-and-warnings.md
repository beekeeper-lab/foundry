# Task 01: Pipeline Skipped Callback + Warnings List Propagation

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 16:50 |
| **Completed** | 2026-04-17 16:50 |
| **Duration** | < 1m |

## Goal

Close the two UX gaps in the generation-progress screen: disabled conditional stages must render as "Skipped" instead of "Pending," and warning *content* must reach the user (not just the count).

## Inputs

- `foundry_app/services/generator.py::_run_pipeline`
- `foundry_app/ui/generation_worker.py`
- `foundry_app/ui/main_window.py` (`_on_stage_progress`, `_on_generation_ok`)
- `foundry_app/ui/screens/generation_progress.py` (`finish`, `mark_stage_skipped`)
- BEAN-245 acceptance criteria.

## Implementation

- **`_run_pipeline`** — added `elif stage_callback: stage_callback(key, "skipped", 0)` branches for `seed_tasks` and `diff_report` when those options are disabled. Single callback, file_count=0.
- **`GenerationWorker.finished_ok`** — changed signal type from `Signal(int, int, str)` to `Signal(int, list, str)`. The worker now emits `list(manifest.all_warnings)` instead of `len(...)`, carrying full warning messages to the UI.
- **`MainWindow._on_stage_progress`** — added `elif status == "skipped": self._progress_screen.mark_stage_skipped(stage_key)`.
- **`MainWindow._on_generation_ok`** — signature updated to accept `warnings: list` and now passes both `warnings=len(warnings)` and `warnings_list=warnings` to `finish()`.
- **`GenerationProgressScreen.finish`** — added `warnings_list: list[str] | None = None` kwarg. Each warning is appended to the log area prefixed with `⚠ `. `mark_stage_skipped` now also appends a `Stage: <key> — skipped` line to the log for consistency with other stage transitions.

## Tests Added / Updated

- `tests/test_generator.py::TestStageCallback::test_stage_keys_match_expected_set` — expected-set updated: disabled stages now emit `skipped` callbacks, so the key set includes `seed_tasks` + `diff_report` even when disabled.
- New `test_disabled_conditional_stages_emit_skipped` asserts the skipped callbacks fire and no done/running calls are emitted for disabled stages.
- `tests/test_generation_progress.py` — added `test_finish_appends_warnings_to_log`, `test_finish_without_warnings_list_is_backward_compatible`, `test_mark_stage_skipped_logs`.

## Acceptance Criteria

- [x] Disabled stages render "Skipped" at completion.
- [x] Log area shows one `⚠` line per warning from `manifest.all_warnings`.
- [x] `GenerationWorker.finished_ok` signal type is `Signal(int, list, str)`.
- [x] Unit tests cover the skipped-callback emission.
- [x] `test_stage_keys_match_expected_set` updated and passes.
- [x] All tests pass (`uv run pytest` → 1804 passed).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Manual Verification

Manual `uv run foundry` inspection is deferred to Tech-QA Task 02 (the developer ran the full test suite, including the UI widget tests on generation_progress, which exercise the same code paths headlessly).

## Definition of Done

- All files committed on feature branch, tests + lint pass, behavior verified via tests.
