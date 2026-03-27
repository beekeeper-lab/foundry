# Task 01: Fix Worktree Session Resolution in telemetry-stamp.py

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-03-27 11:12 |
| **Completed** | — |
| **Duration** | — |

## Goal

Fix `find_session_jsonl()` in `.claude/hooks/telemetry-stamp.py` so it correctly locates the JSONL session file when the hook runs inside a git worktree (e.g., `/tmp/foundry-worktree-BEAN-NNN`).

## Inputs

- `.claude/hooks/telemetry-stamp.py` — the hook to modify (lines 518-580: `find_session_jsonl()` and `find_git_toplevel()`)
- `~/.claude/projects/` — where Claude Code stores JSONL session files, organized by project path hash

## Acceptance Criteria

- [ ] `find_session_jsonl()` uses `git rev-parse --show-toplevel` to resolve the real repo root when cwd is a worktree
- [ ] When the worktree-specific project hash (e.g., `-tmp-foundry-worktree-BEAN-NNN`) has no JSONL files, falls back to the main repo's project hash (e.g., `-home-gregg-Nextcloud-workspace-foundry`)
- [ ] Does NOT fall back to an unrelated project's JSONL (the dangerous global fallback)
- [ ] Stderr logging indicates when worktree-to-main-repo fallback is used
- [ ] Existing non-worktree behavior is unchanged

## Definition of Done

- Code changes in `telemetry-stamp.py` only
- All existing tests pass
- Lint clean
