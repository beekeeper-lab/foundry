# BEAN-058: Add Branded Spinner Graphic

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-058 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Foundry has no animated loading indicator. The Generation Progress screen uses static Unicode symbols (▶ for "Running...") and a progress bar, but there is no visual animation that communicates active processing. This makes the app feel static during long-running operations. A branded spinner graphic has been provided — a gear-themed Foundry emblem — that should rotate to indicate activity.

## Goal

Add the provided gear graphic to the project, create a reusable `SpinnerWidget` that rotates the image, and integrate it into the Generation Progress screen alongside the existing stage list and progress bar. The widget should be reusable so any future screen can show the branded spinner during wait states.

## Scope

### In Scope
- Copy the source graphic (`/home/gregg/Downloads/ChatGPT Image Feb 7, 2026, 08_02_28 PM.png`) into `resources/icons/foundry-spinner.png`
- Create a reusable `SpinnerWidget` class in `foundry_app/ui/widgets/spinner_widget.py`
  - Accepts a size parameter (default 48x48)
  - Uses `QPropertyAnimation` to rotate the image continuously
  - Provides `start()` and `stop()` methods
  - Handles the `QPixmap` scaling and smooth rotation via `QTransform`
- Integrate the spinner into `foundry_app/ui/screens/generation_progress.py`
  - Display the spinner alongside the stage list (e.g., near the top or next to running stages)
  - Start spinning when generation begins, stop when it finishes or errors
- Ensure the image file is packaged (update `pyproject.toml` if needed — may already be covered by BEAN-043)
- Add tests for the SpinnerWidget class

### Out of Scope
- Replacing the existing progress bar or stage list — spinner is additive
- Using the spinner as an indeterminate-only progress indicator (the stage list still shows discrete progress)
- Generating multiple image sizes or formats
- Adding the spinner to screens other than Generation Progress (the widget is reusable, but wiring it into other screens is future work)

## Acceptance Criteria

- [ ] `resources/icons/foundry-spinner.png` exists in the repository
- [ ] `foundry_app/ui/widgets/spinner_widget.py` exists with a `SpinnerWidget` class
- [ ] `SpinnerWidget` has `start()` and `stop()` methods that control rotation animation
- [ ] `SpinnerWidget` renders at 48x48 by default with smooth rotation
- [ ] Generation Progress screen shows the spinning gear during generation
- [ ] Spinner starts when `start()` is called and stops when `finish()` or `finish_with_error()` is called
- [ ] Spinner does not consume excessive CPU (uses `QPropertyAnimation`, not a tight QTimer loop)
- [ ] No new dependencies introduced (uses only PySide6 built-in animation classes)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Copy spinner PNG to `resources/icons/foundry-spinner.png` | developer | | Pending |
| 2 | Create `SpinnerWidget` class in `foundry_app/ui/widgets/spinner_widget.py` | developer | 1 | Pending |
| 3 | Integrate spinner into `generation_progress.py` | developer | 2 | Pending |
| 4 | Add unit tests for `SpinnerWidget` | tech-qa | 2 | Pending |
| 5 | Verify spinner renders and animates correctly during generation | tech-qa | 3 | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Source image: `/home/gregg/Downloads/ChatGPT Image Feb 7, 2026, 08_02_28 PM.png`
- Target location: `resources/icons/foundry-spinner.png`
- The gear/cog design of the graphic naturally suggests rotation — spinning it communicates "working/processing"
- Implementation approach: Use `QGraphicsView` + `QGraphicsPixmapItem` with `QPropertyAnimation` on the rotation property, or use a custom `paintEvent` with `QTransform.rotate()`. The `QPropertyAnimation` approach is smoother and more CPU-efficient.
- The `resources/icons/` directory already exists (used by BEAN-043 for the logo)
- If BEAN-043 has already updated `pyproject.toml` to include `resources/`, this bean doesn't need to repeat that
- Current Generation Progress screen is at `foundry_app/ui/screens/generation_progress.py`
- The spinner widget should be generic enough to use in future loading states (library indexing, export, etc.)

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 5s).
