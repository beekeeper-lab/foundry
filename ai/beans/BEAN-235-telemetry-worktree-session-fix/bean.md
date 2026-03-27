# BEAN-235: Telemetry Worktree Session Resolution Fix

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-235 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-03-27 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

When beans run in git worktrees (e.g., `/tmp/foundry-worktree-BEAN-NNN`), the telemetry-stamp hook's `find_session_jsonl()` cannot locate the correct JSONL session file. The function builds a project hash from `Path.cwd()` (e.g., `-tmp-foundry-worktree-BEAN-176`), but Claude Code stores the JSONL under the worktree's own project hash directory. When the worktree is cleaned up, that JSONL directory is orphaned and eventually lost. The fallback logic then picks the most recently modified JSONL from any project directory, which may belong to a completely different session — producing wildly incorrect token counts.

Confirmed: zero `.telemetry.json` watermark files exist for any worktree-executed bean, and worktree JSONL directories (e.g., `~/.claude/projects/-tmp-foundry-worktree-BEAN-*`) contain no JSONL files despite having been created.

## Goal

`find_session_jsonl()` reliably locates the correct session JSONL when running inside a git worktree, so that token watermarks are saved and delta calculations produce accurate per-task token counts.

## Scope

### In Scope
- Fix `find_session_jsonl()` in `.claude/hooks/telemetry-stamp.py` to correctly resolve the JSONL path when `cwd` is a worktree under `/tmp/`
- Use `git rev-parse --git-common-dir` (already used by `find_session_jsonl` for `find_git_toplevel`) to map worktree cwd back to the main repo's project hash
- Add fallback: if the worktree-specific project hash has no JSONL, try the main repo's project hash before the global fallback
- Add stderr logging when falling back so issues are visible in hook output

### Out of Scope
- Fixing the long-run batch session isolation problem (BEAN-230)
- Fixing the missing-session fallback behavior (BEAN-231)
- Changing how Claude Code itself stores JSONL files
- Backfilling historical bean telemetry data

## Acceptance Criteria

- [ ] `find_session_jsonl()` returns the correct JSONL when cwd is a git worktree
- [ ] Token watermarks are saved for tasks executed in worktrees
- [ ] Token deltas are computed correctly (not zero, not full-session) for worktree beans
- [ ] Stderr logging indicates when worktree resolution is used
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

Part of a 3-bean split investigating telemetry accuracy. See also BEAN-236 (long-run batch isolation) and BEAN-237 (missing session fallback).

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
