# BEAN-245: Fix Generation Progress — Skipped Stages and Warnings Display

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-245 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Two UX bugs in the generation-progress screen, both observed on `test` branch today (2026-04-17):

1. **Stage rows stuck at "Pending" forever.** In `foundry_app/services/generator.py::_run_pipeline`, conditional stages — `seed_tasks` and `diff_report` — are silently skipped when disabled in the composition. No stage-progress callback fires. The UI's `PIPELINE_STAGES` list in `foundry_app/ui/screens/generation_progress.py` always includes these eight stages, so disabled stages sit at "Pending" forever. The `set_skipped()` method exists on the stage widget (with en-dash icon + "Skipped" label) but nothing calls it from the pipeline. Result: user completes a generation, sees "Generation complete in 0.1s" and "146 files written", yet the "Generate diff report" row still says "Pending" — confusing.
2. **Warning count shown but content hidden.** `GenerationWorker.finished_ok` is a `Signal(int, int, str)` — `(total_files, warnings_count, output_path)`. Only the count reaches the UI. When the generator emits warnings (e.g., `"Expertise 'clean-code' missing conventions.md"` or `"Unresolved placeholders in ai/generated/members/code-quality-reviewer.md: strictness"`), the user sees "4 warnings" but has no way to read them. They exist on `manifest.all_warnings` but are dropped at the signal boundary.

## Goal

1. Conditional stages that are skipped emit a `skipped` callback; the UI marks their rows as "Skipped" (en-dash icon, "Skipped" label) instead of leaving them at "Pending."
2. Warning contents are surfaced to the user, not just the count. The simplest approach: append each warning to the generation-progress log area (which already exists) with a warning prefix.

## Scope

### In Scope
- Update `foundry_app/services/generator.py::_run_pipeline` to emit `stage_callback(key, "skipped", 0)` for `seed_tasks` and `diff_report` when they're disabled in the composition.
- Update `foundry_app/ui/main_window.py::_on_stage_progress` to handle `status == "skipped"` by calling `self._progress_screen.mark_stage_skipped(stage_key)`.
- Change `GenerationWorker.finished_ok` signal signature from `(int, int, str)` to `(int, list, str)` — passing the full warnings list instead of just a count.
- Update `GenerationProgressScreen.finish()` to accept a `warnings_list` keyword argument and append each warning to the log area (preserve the existing `warnings` int arg for the summary label).
- Unit tests for the skipped-stage callback emission and for warnings-list propagation.
- Existing test `test_stage_keys_match_expected_set` in `tests/test_generator.py` updated to assert `skipped` status for disabled stages.

### Out of Scope
- Redesigning the generation-progress screen layout.
- Fixing the warnings themselves (e.g., the `clean-code` missing `conventions.md` warning is a library content issue; the `strictness` placeholder is BEAN-243).
- Adding a separate "Warnings" dialog or dedicated warnings panel.

## Acceptance Criteria

- [ ] Generating a project with `write_diff_report=False` and `seed_tasks=False` leaves both stage rows marked "Skipped" (en-dash icon) at completion — not "Pending."
- [ ] Generation-progress log area contains one line per warning in `manifest.all_warnings`, with a warning prefix (e.g., `⚠ <warning text>`).
- [ ] `GenerationWorker.finished_ok` signal signature updated to carry `list` of warnings, not `int` count.
- [ ] Unit test: `_run_pipeline` emits `(stage_key, "skipped", 0)` for disabled `seed_tasks` / `diff_report`.
- [ ] Existing `test_stage_keys_match_expected_set` updated and passes.
- [ ] Manual verification: run `uv run foundry` → generate a project with default options → observe "Skipped" stages and warning text in the log.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**Origin.** User ran the generation pipeline from the GUI, observed the "Generate diff report" row stuck at "Pending" after the other stages finished, and noted there was no way to see what the reported "4 warnings" were. Confirmed root cause by inspecting the pipeline's skip paths and the worker signal shape.

**Independent from BEAN-242..244.** This bug is pure UX and does not affect correctness of the generated output. It can be picked without touching the compile pipeline or scaffold.

**Files to touch (small surface):**
- `foundry_app/services/generator.py` (_run_pipeline: 2 `stage_callback` calls added)
- `foundry_app/ui/generation_worker.py` (1 signal signature change, 1 emit call updated)
- `foundry_app/ui/main_window.py` (_on_stage_progress: 1 elif branch added; _on_generation_ok: receive list)
- `foundry_app/ui/screens/generation_progress.py` (finish: add `warnings_list` kwarg, append to log)
- `tests/test_generator.py` (update `test_stage_keys_match_expected_set`)

Fits blast-radius budget (≤10 files, ≤1 boundary, ≤300 lines).

**Downstream verification:**

| System | Impact | Verification Command |
|--------|--------|---------------------|
| Tests  | Generator + UI tests | `uv run pytest tests/test_generator.py tests/test_generation_progress.py tests/test_main_window.py` |
| Lint   | `foundry_app/` changes | `uv run ruff check foundry_app/` |
| Manual | Run the GUI, generate a project | `uv run foundry` then inspect progress screen |

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
