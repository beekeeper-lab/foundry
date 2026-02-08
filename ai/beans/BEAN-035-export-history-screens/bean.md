# BEAN-035: Export & History Screens

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-035 |
| **Status** | Done |
| **Priority** | Low |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

After generating projects, users have no way to browse past generation runs, export generated projects as archives, or re-generate from a saved composition. An Export screen and History screen would provide project management and auditability.

## Goal

Implement two PySide6 UI screens: (1) Export Screen for archiving generated projects as ZIP/tarball, and (2) History Screen for browsing past generation runs and their manifests.

## Scope

### In Scope
- Implement `foundry_app/ui/screens/export_screen.py`
  - List recently generated projects
  - Export as ZIP or tarball via `shutil.make_archive`
  - Show file size, date, file count
- Implement `foundry_app/ui/screens/history_screen.py`
  - Browse past manifests from generated project roots
  - Display run metadata: date, composition used, files written
  - "Re-generate" action to reload composition and trigger generation
- Catppuccin Mocha theme styling
- Integrate with main window sidebar navigation
- Comprehensive test suites for both screens

### Out of Scope
- Cloud storage export
- Version comparison between runs
- Manifest editing

## Acceptance Criteria

- [x] Export screen renders and lists generated projects
- [x] Export produces valid ZIP/tarball archives (via shutil.make_archive)
- [x] History screen renders and displays past runs
- [x] Re-generate action emits signal with project path
- [x] Both screens integrate with main window (via signals)
- [x] All tests pass (`uv run pytest`) — 27 PySide6 tests
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement export screen | Developer | — | Done |
| 2 | Implement history screen | Developer | — | Done |
| 3 | Write tests (15+12 tests) | Tech-QA | 1,2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-016 (models/IO), BEAN-017 (main window), both Done
- Uses `shutil.make_archive` for export
- Manifest model exists in `core/models.py`
- Composition I/O in `foundry_app/io/composition_io.py`
