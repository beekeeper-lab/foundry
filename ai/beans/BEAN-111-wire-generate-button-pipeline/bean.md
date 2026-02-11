# BEAN-111: Wire Generate Button to Pipeline with Progress

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-111 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-10 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The "Generate Project" button on the Review page does nothing when clicked. The signal chain from `ReviewPage` → `BuilderScreen` emits `generate_requested` with a `CompositionSpec`, but `MainWindow` never connects to that signal. The existing `GenerationProgressScreen` (with spinner, progress bar, stage indicators, and "Open Project Folder" button) is fully built but never displayed. Users click the button and nothing happens — the core workflow is broken.

## Goal

Clicking "Generate Project" launches the generation pipeline on a background thread, switches the view to the existing `GenerationProgressScreen` with live progress updates, and upon completion shows the output folder path with a button to open it in the system file manager.

## Scope

### In Scope
- Connect `BuilderScreen.generate_requested` signal in `MainWindow`
- Run `generator.generate_project()` on a `QThread` worker to keep the UI responsive
- Switch view to `GenerationProgressScreen` when generation starts
- Wire stage-by-stage progress callbacks (scaffold → compile → copy_assets → seed → safety → diff_report) to the progress screen's existing stage indicators
- Show the spinner during execution (already implemented in `GenerationProgressScreen`)
- On success: call `finish()` with summary, show output folder path, enable "Open Project Folder" button
- Wire "Open Project Folder" button to `QDesktopServices.openUrl()` / `xdg-open` for the generated folder
- On error: call `finish_with_error()` with the error message
- Provide a way to navigate back to the builder after generation (success or failure)

### Out of Scope
- Cancellation support (stop mid-generation)
- Generation history/log persistence
- Modifying the generation pipeline itself (services layer)
- Changing the GenerationProgressScreen layout or styling

## Acceptance Criteria

- [ ] Clicking "Generate Project" on the Review page triggers project generation
- [ ] The view switches to `GenerationProgressScreen` showing the spinner immediately
- [ ] Stage indicators update in real-time as each pipeline stage completes
- [ ] If generation takes longer than ~1 second, the user sees the spinner (not a frozen UI)
- [ ] On success, the output folder path is displayed to the user
- [ ] On success, "Open Project Folder" button is visible and opens the folder in the system file manager
- [ ] On error, an error message is displayed on the progress screen
- [ ] User can navigate back to the builder after generation completes (success or failure)
- [ ] UI remains responsive during generation (no blocking the main thread)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- `GenerationProgressScreen` already has spinner, progress bar, stage widgets, log area, and "Open Project Folder" button — all built but unwired
- `BuilderScreen.generate_requested(CompositionSpec)` signal exists and fires correctly
- `generator.generate_project()` in `foundry_app/services/generator.py` is the entry point
- Key files: `foundry_app/ui/main_window.py`, `foundry_app/ui/screens/builder_screen.py`, `foundry_app/ui/screens/generation_progress.py`, `foundry_app/services/generator.py`
- Related done beans: BEAN-032 (Generator Orchestrator), BEAN-033 (Generation Progress Screen), BEAN-067 (Wire Compiler & Asset Copier)

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
