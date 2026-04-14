# Task 02: Verify Worktree Session Resolution Fix

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-03-27 11:17 |
| **Completed** | 2026-03-27 11:21 |
| **Duration** | 4m |

## Goal

Verify that the `find_session_jsonl()` fix correctly handles worktree paths, main repo paths, and edge cases. Review the code for correctness and robustness.

## Inputs

- `.claude/hooks/telemetry-stamp.py` — modified hook
- Task 01 changes

## Acceptance Criteria

- [ ] `find_session_jsonl()` correctly maps worktree cwd to main repo project hash
- [ ] Non-worktree (normal repo) behavior is unchanged
- [ ] The dangerous global fallback (picking any recent project's JSONL) is removed or guarded
- [ ] Stderr messages are clear and actionable
- [ ] No regressions in existing `find_git_toplevel()` behavior
- [ ] Code follows existing patterns in the file (error handling, Path usage)

## Definition of Done

- Code review complete
- Any issues found are fixed
- All tests pass (`uv run pytest`)
- Lint clean (`uv run ruff check foundry_app/`)
