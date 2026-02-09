# Skill: Merge Bean

## Description

Safely merges a bean's feature branch into the `test` integration branch. Handles pulling latest changes, detecting merge conflicts, and reporting results. This is the Merge Captain's primary operation — the final stage of the bean execution wave.

## Trigger

- Invoked by the `/merge-bean` slash command.
- Called automatically by `/long-run` as the final stage after bean verification.
- Should be executed by the Team Lead (acting as Merge Captain) or the integrator-merge-captain persona.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| bean_id | String | Yes | Bean identifier (e.g., `BEAN-011` or `11`) |
| target_branch | String | No | Branch to merge into (default: `test`) |
| bean_dir | Directory | Yes | `ai/beans/BEAN-NNN-<slug>/` — resolved from bean_id |

## Process

### Phase 1: Validation

1. **Resolve bean directory** — Find the bean directory matching the ID in `ai/beans/`.
2. **Read bean status** — Parse `bean.md`. Confirm status is `Done`.
   - If not `Done`: report `BeanNotDone` error and exit.
3. **Derive feature branch name** — Extract from the bean directory name: `bean/BEAN-NNN-<slug>`.
4. **Verify feature branch exists** — Run `git branch --list bean/BEAN-NNN-<slug>`.
   - If not found: report `BranchNotFound` error and exit.

### Phase 2: Prepare Target

5. **Checkout target branch** — `git checkout test` (or specified target).
   - If the target branch doesn't exist locally, create it: `git checkout -b test`.
6. **Pull latest** — `git pull origin test`.
   - If the remote branch doesn't exist yet (first merge), skip pull.

### Phase 3: Merge

7. **Merge feature branch** — `git merge bean/BEAN-NNN-<slug> --no-ff`.
   - The `--no-ff` flag preserves a merge commit even if fast-forward is possible, making the merge visible in history.
8. **Check merge result**:
   - **Clean merge**: proceed to Phase 4.
   - **Conflict**: go to Conflict Handling (below).

### Phase 4: Push & Cleanup

9. **Push to remote** — `git push origin test`.
   - If push fails (e.g., another worker pushed first), pull and retry once.
10. **Delete feature branch** — `git branch -d bean/BEAN-NNN-<slug>`.
    - If the branch is also on the remote: `git push origin --delete bean/BEAN-NNN-<slug>`.
    - If delete fails (e.g., worktree reference), log a warning but continue.
11. **Return to main** — `git checkout main`.
12. **Report success** — Output: bean title, feature branch name (deleted), target branch, merge commit hash.

### Conflict Handling

If step 8 detects merge conflicts:

1. **List conflicting files** — Report each file with conflicts.
2. **Abort the merge** — `git merge --abort` to restore the target branch to its pre-merge state.
3. **Return to feature branch** — `git checkout bean/BEAN-NNN-<slug>`.
4. **Report failure** — List the conflicting files and instruct the user to resolve manually.
5. **Exit** — Do not attempt automatic conflict resolution.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| merge_commit | Git commit | Merge commit on the target branch |
| merge_report | Console text | Summary: bean, branches, commit hash, or conflict details |

## Quality Criteria

- The target branch is always pulled before merging (handles concurrent merges).
- Merge uses `--no-ff` to preserve merge history.
- Conflicts are never auto-resolved — they are reported clearly.
- After a successful merge, the feature branch is deleted (local + remote) and the working directory returns to `main`.
- After a failed merge, the working directory returns to the feature branch (branch is preserved for conflict resolution).
- Push failures trigger one retry after pull.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `BeanNotDone` | Bean status is not `Done` | Finish the bean first, then merge |
| `BranchNotFound` | Feature branch doesn't exist in git | Was the bean processed with `--no-branch`? Create branch manually or skip merge |
| `MergeConflict` | Auto-merge fails due to conflicting changes | Report files, abort merge, return to feature branch |
| `PushFailure` | Push rejected or network error | Pull and retry once; if still failing, report for manual resolution |
| `TargetNotFound` | Target branch doesn't exist on remote | Create locally and push; this is normal for the first merge |

## Dependencies

- Bean must have status `Done` in its `bean.md`
- Feature branch `bean/BEAN-NNN-<slug>` must exist
- Git repository in a clean state (no uncommitted changes)
- Push permissions for the target branch (see `.claude/hooks/hook-policy.md`)
