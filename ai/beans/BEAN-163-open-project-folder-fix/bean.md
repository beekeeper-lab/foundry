# BEAN-163: Fix Open Project Folder Button

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-163 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:11 |
| **Completed** | 2026-02-20 20:14 |
| **Duration** | 3m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

On the last page of the Foundry wizard (after project generation), there is a large "Open Project Folder" button. Clicking it does nothing. This may be a general bug or specific to Arch Linux — the file manager opener may not work on all Linux distributions.

## Goal

Investigate the Open Project Folder button implementation, identify why it fails (likely a platform-specific issue with file manager detection on Linux), and fix it to work cross-platform.

## Scope

### In Scope
- Investigate the current implementation of the Open Project Folder button
- Identify the root cause (likely `QDesktopServices.openUrl()` or `subprocess` call)
- Fix the implementation to work on Linux (including Arch), macOS, and Windows
- Add fallback mechanisms (e.g., `xdg-open` on Linux, `open` on macOS, `explorer` on Windows)

### Out of Scope
- Redesigning the post-generation screen
- Adding other post-generation actions

## Acceptance Criteria

- [x] Open Project Folder button opens the generated project directory in the system file manager
- [x] Works on Linux (tested with `xdg-open` fallback)
- [x] Cross-platform logic handles macOS (`open`) and Windows (`explorer`) as well
- [x] Graceful error handling if no file manager is available
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Fix open folder to use subprocess | Developer | — | Done |
| 2 | Test open folder fix | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention — sequential Developer → Tech-QA wave, single file modified.

## Notes

User reported this on Arch Linux. Check if `QDesktopServices.openUrl()` is being used (known to be unreliable on some Linux distros) vs direct subprocess calls to `xdg-open`.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 699844ce79bdf800e861ef0b |
| **Card Name** | Open Project Folder Button |
| **Card URL** | https://trello.com/c/sVwmiBeQ/37-open-project-folder-button |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Fix open folder to use subprocess | Developer | < 1m | 1,489,281 | 2,243 | $3.70 |
| 2 | Test open folder fix | Tech-QA | < 1m | 1,978,028 | 3,470 | $4.72 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 3,467,309 |
| **Total Tokens Out** | 5,713 |
| **Total Cost** | $8.42 |