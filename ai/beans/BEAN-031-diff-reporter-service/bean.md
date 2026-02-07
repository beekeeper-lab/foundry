# BEAN-031: Diff Reporter Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-031 |
| **Status** | New |
| **Priority** | Low |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The generator orchestrator calls `_stub_diff_report()` as a placeholder. When `spec.generation.write_diff_report` is True and overlay mode produces an `OverlayPlan`, the system should generate a human-readable `diff-report.md` summarizing what changed (creates, updates, deletes). Without this service, users have no summary of overlay changes.

## Goal

Implement a `DiffReporterService` that generates a `diff-report.md` file summarizing overlay changes from the `OverlayPlan`.

## Scope

### In Scope
- Implement `foundry_app/services/diff_reporter.py`
- Function: `write_diff_report(plan: OverlayPlan, output_dir: Path) -> StageResult`
- Generate markdown report with: total creates/updates/deletes, grouped file lists
- Include timestamp and run context
- Only called in overlay mode when `write_diff_report=True`
- Replace `_stub_diff_report()` in generator with real call
- Comprehensive test suite

### Out of Scope
- Interactive diff viewer UI
- File content diffs (just paths and action types)

## Acceptance Criteria

- [ ] `foundry_app/services/diff_reporter.py` exists with `write_diff_report()` function
- [ ] Generates markdown report with create/update/delete sections
- [ ] Handles empty overlay plans gracefully
- [ ] Generator stub replaced with real service call
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Models already exist: `OverlayPlan`, `FileAction`, `FileActionType` in `core/models.py`
- Generator stub at `generator.py:61-64`
- Generator already computes `OverlayPlan` in `_compare_trees()`
- Depends on BEAN-016 (models) and BEAN-032 (generator orchestrator), both Done
