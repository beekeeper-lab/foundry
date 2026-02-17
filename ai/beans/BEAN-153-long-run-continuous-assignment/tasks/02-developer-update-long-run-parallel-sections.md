# Task 02: Update long-run Parallel Mode Sections

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-02-17 04:36 |
| **Completed** | 2026-02-17 04:37 |
| **Duration** | 1m |

## Goal

Update `.claude/commands/long-run.md` parallel mode sections to be consistent with the rewritten spawn-bean dashboard loop from Task 01. Ensure the long-run spec's own description of replacement spawning is integrated into the flow, not disconnected.

## Inputs

- `.claude/commands/long-run.md` — current long-run spec (Parallel Mode section)
- `.claude/commands/internal/spawn-bean.md` — updated spawn-bean spec (from Task 01)
- `ai/beans/BEAN-153-long-run-continuous-assignment/bean.md` — acceptance criteria

## Work

1. Update "Parallel Phase 4: Dashboard Monitoring" (steps 10-12) to reference the integrated dashboard loop from spawn-bean Step 4, ensuring consistency.

2. Ensure step 12 ("Merge, update index, and assign next bean") explicitly states:
   - Re-read `_index.md` fresh each cycle (not pre-computed queue)
   - The loop runs until no approved beans remain (no max limit)
   - Exit condition matches spawn-bean: all done AND no approved beans

3. Verify "Bean Assignment Rules" section doesn't describe replacement logic in a disconnected way — it should point to the integrated loop.

4. No changes to sequential mode, `--wide` mode references, or worker prompts.

## Acceptance Criteria

- [ ] Parallel Phase 4 is consistent with updated spawn-bean Step 4
- [ ] Re-read-backlog-each-cycle is explicitly stated
- [ ] Exit condition matches: all done AND no approved beans remain
- [ ] Sequential mode unchanged
- [ ] No disconnected replacement logic sections

## Definition of Done

All acceptance criteria checked, long-run.md updated.
