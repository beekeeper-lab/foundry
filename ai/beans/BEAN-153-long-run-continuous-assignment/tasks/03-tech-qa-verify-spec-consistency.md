# Task 03: Verify Spec Consistency and Completeness

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01, 02 |
| **Status** | Done |
| **Started** | 2026-02-17 04:38 |
| **Completed** | 2026-02-17 04:38 |
| **Duration** | < 1m |

## Goal

Independently verify that the updated spawn-bean.md and long-run.md specs are internally consistent, complete, and preserve all existing behavior while adding the continuous assignment loop.

## Inputs

- `.claude/commands/internal/spawn-bean.md` — updated spawn-bean spec
- `.claude/commands/long-run.md` — updated long-run spec
- `ai/beans/BEAN-153-long-run-continuous-assignment/bean.md` — acceptance criteria

## Verification Checklist

- [ ] spawn-bean.md Step 4 dashboard loop has integrated numbered steps for: done-detection, worktree cleanup, merge, index update, backlog re-read, replacement spawn
- [ ] spawn-bean.md includes concrete bash `while true` polling snippet
- [ ] spawn-bean.md has no separate disconnected "Worker completion" sub-section
- [ ] long-run.md Parallel Phase 4 is consistent with spawn-bean Step 4
- [ ] long-run.md explicitly states re-read-backlog-each-cycle behavior
- [ ] Exit condition is identical in both files: all done AND no approved beans remain
- [ ] `--wide` mode behavior is preserved in spawn-bean.md
- [ ] Status file protocol unchanged
- [ ] Sequential mode in long-run.md unchanged
- [ ] Worker prompt text unchanged (workers don't need modification)
- [ ] No references to removed sections (stale cross-references)
- [ ] All bean-153 acceptance criteria are satisfied

## Definition of Done

All verification checks pass. Any issues found are fixed or flagged.
