# BEAN-237: Telemetry Missing Session Graceful Fallback

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-237 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-03-27 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

When `find_session_jsonl()` cannot locate any JSONL file for the current session, the telemetry-stamp hook silently falls through and writes no token data to the bean telemetry table. The sentinel dashes remain, giving no indication that a capture attempt was made and failed. Worse, the current fallback path (`find the most recently modified JSONL from any project directory`) can return a JSONL from a completely unrelated project or session, producing wildly incorrect token counts.

## Goal

When no matching JSONL session can be found, the telemetry system degrades gracefully: it writes a recognizable marker (not sentinel dashes) indicating "capture failed", logs the reason, and never uses an unrelated session's JSONL as a fallback.

## Scope

### In Scope
- Remove the dangerous global fallback in `find_session_jsonl()` that picks the most recently modified project directory when the current project hash isn't found
- When no JSONL is found, write a marker like `N/A` or `(no session)` to the telemetry table instead of leaving sentinels
- Log a clear stderr message explaining why capture failed (cwd, expected project hash, what was searched)
- Ensure the summary table still computes correctly when some tasks have `N/A` token values (skip them in sums)

### Out of Scope
- Fixing worktree resolution (BEAN-229)
- Fixing long-run batch isolation (BEAN-230)
- Retrying or deferring capture to a later time

## Acceptance Criteria

- [ ] `find_session_jsonl()` never returns a JSONL from an unrelated project directory
- [ ] When no JSONL is found, telemetry row shows `N/A` for Tokens In, Tokens Out, and Cost
- [ ] Summary table computation skips `N/A` rows without errors
- [ ] Stderr log includes: cwd path, expected project hash, directories searched
- [ ] The `telemetry-report` skill handles `N/A` values without crashing
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

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

Part of a 3-bean split investigating telemetry accuracy. See also BEAN-235 (worktree session fix) and BEAN-236 (long-run batch isolation).

This bean addresses the "last resort" case. After BEAN-229 and BEAN-230, most sessions should be correctly identified. This bean ensures the remaining edge cases fail safely rather than silently corrupting data.

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
