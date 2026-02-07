# Task 01: Update Commands, Skills, and Workflow for Feature Branches

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Update `/pick-bean`, `/long-run`, and `bean-workflow.md` to incorporate feature branch creation as part of the bean execution lifecycle.

## Inputs

- `ai/beans/BEAN-008-feature-branch-workflow/bean.md` — acceptance criteria
- `.claude/commands/pick-bean.md` — command to update
- `.claude/skills/pick-bean/SKILL.md` — skill to update
- `.claude/commands/long-run.md` — command to update
- `.claude/skills/long-run/SKILL.md` — skill to update
- `ai/context/bean-workflow.md` — workflow doc to update

## Implementation

1. **`bean-workflow.md`**: Add a "Branch Strategy" section documenting:
   - Naming convention: `bean/BEAN-NNN-<slug>`
   - Branch created when bean moves to `In Progress`
   - All commits for the bean go on the feature branch
   - Branch cleanup after merge (future — BEAN-011)

2. **`/pick-bean` command + skill**: Add a `--branch` flag (default: true when `--start` is used):
   - Creates `bean/BEAN-NNN-<slug>` branch from current HEAD
   - Checks out the new branch
   - Step added after status update

3. **`/long-run` command + skill**: Update Phase 3 (Bean Execution) to:
   - Create feature branch before decomposing
   - All wave work happens on the branch
   - Commit on the branch (not main)
   - After closing, note that branch is ready for merge

## Acceptance Criteria

- [ ] `bean-workflow.md` documents branch naming convention and strategy
- [ ] `/pick-bean` skill creates feature branch when starting a bean
- [ ] `/long-run` skill creates feature branch per bean
- [ ] Branch naming convention: `bean/BEAN-NNN-<slug>`
- [ ] All formats match existing patterns

## Definition of Done

All files updated. Branch strategy documented.
