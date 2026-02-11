# BEAN-011: Merge Captain Auto-Merge

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-011 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

When beans are processed on feature branches (especially in parallel), completed work needs to be safely merged into an integration branch. Currently there is no automated merge step — the user would have to manually merge each feature branch. With N parallel workers, this becomes a bottleneck and a source of merge conflicts.

## Goal

Add a Merge Captain stage as the final step of each bean's execution. The Merge Captain (integrator-merge-captain persona) safely merges the bean's feature branch into the `test` branch, handling conflicts and ensuring the branch is up to date before pushing.

## Scope

### In Scope
- Merge Captain as the final stage in the bean execution wave
- Target branch: `test` (configurable, but `test` is the default)
- Safe merge process: pull test branch, merge feature branch, resolve conflicts, push
- Conflict handling: if auto-merge fails, report the conflict and leave for manual resolution
- Update `/long-run` skill to include Merge Captain as the final stage
- Update the integrator-merge-captain agent/persona with auto-merge instructions
- Works for both single-threaded and parallel execution

### Out of Scope
- Merging to main/master (that remains a manual/PR process)
- PR creation (future enhancement)
- CI/CD trigger after merge
- Automatic conflict resolution (conflicts are reported, not auto-resolved)
- Deleting feature branches after merge (left for manual cleanup)

## Acceptance Criteria

- [ ] Merge Captain stage added as the final step after Tech-QA verification
- [ ] Feature branch is merged into `test` branch
- [ ] Merge Captain pulls latest `test` before merging (handles concurrent merges)
- [ ] If merge conflicts occur, Merge Captain reports them clearly and stops
- [ ] Push to `test` succeeds (requires BEAN-009 hook refinement)
- [ ] `/long-run` skill updated to include Merge Captain stage
- [ ] Merge Captain agent/persona instructions updated
- [ ] Works correctly in both sequential and parallel modes

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Wire Merge Captain into Bean Execution Wave | developer | — | Done |
| 02 | Merge Captain Verification | tech-qa | 01 | Done |

> BA and Architect skipped — architecture sketch is already in the bean, and this wires an existing persona into the workflow.

## Notes

Depends on: BEAN-008 (Feature Branch Workflow), BEAN-009 (Push Hook Refinement), BEAN-010 (Parallel Long Run).

**Safe merge sequence:**
1. `git checkout test`
2. `git pull origin test` (get latest — other workers may have merged since)
3. `git merge bean/BEAN-NNN-<slug>` (merge the feature branch)
4. If conflict: report and stop (do not force-resolve)
5. If clean: `git push origin test`
6. Report success to Team Lead

The Merge Captain already exists as a persona in the library (`integrator-merge-captain`). This bean wires that persona into the automated workflow with specific auto-merge instructions.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (single commit, no merge).
