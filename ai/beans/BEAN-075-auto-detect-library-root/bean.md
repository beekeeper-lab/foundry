# BEAN-075: Auto-Detect Library Root

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-075 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The wizard's Select Team Personas page (and Stacks/Hooks pages) appear empty on first launch because `library_root` defaults to an empty string. Users must manually navigate to Settings and configure the path before the wizard is usable. Since `ai-team-library/` ships inside the foundry repo as a sibling to `foundry_app/`, the application should auto-detect it.

## Goal

The wizard populates personas, stacks, and hook packs automatically on first launch without requiring any manual settings configuration.

## Scope

### In Scope
- Auto-detect `ai-team-library/` relative to the application package directory
- Persist the detected path to QSettings so it survives across sessions
- Validation that the detected directory contains `personas/` before using it
- Logging of detection result (found or not found)

### Out of Scope
- Empty-state UX messaging on the persona page (can be a separate bean if needed)
- Environment variable overrides (e.g., `FOUNDRY_LIBRARY_ROOT`)
- Searching multiple locations or parent directories beyond the repo root

## Acceptance Criteria

- [ ] On first launch with no `library_root` configured, the wizard auto-detects `ai-team-library/` and populates all 13 personas
- [ ] The auto-detected path is persisted to QSettings so subsequent launches use it directly
- [ ] If `library_root` is already set in settings, auto-detection is skipped (user override preserved)
- [ ] If auto-detection fails (e.g., running from a different directory), no crash or error — page stays empty as before
- [ ] Detection logic resolves relative to `foundry_app/` package location (not CWD)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add `_detect_library_root()` method to `MainWindow` | | | Pending |
| 2 | Wire auto-detection into `_apply_initial_settings()` | | 1 | Pending |
| 3 | Add unit test for detection logic | | 1 | Pending |
| 4 | Manual smoke test — launch with empty settings | | 2 | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- **Detection strategy:** Resolve `foundry_app/__init__.py` → parent → parent → check for `ai-team-library/personas/`
- **Key file:** `foundry_app/ui/main_window.py` — `_apply_initial_settings()` method (lines 249-255)
- The same fix benefits stacks and hook packs since they all flow through `set_library_index()`

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
