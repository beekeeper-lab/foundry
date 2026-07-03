# Skill: Merge Bean

## Description

Safely merges a bean's feature branch into the `main` branch. Handles pulling latest changes, detecting merge conflicts, and reporting results. This is the Merge Captain's primary operation — the final stage of the bean execution wave.

## Trigger

- Invoked by the `/merge-bean` slash command.
- Called automatically by `/long-run` as the final stage after bean verification.
- Should be executed by the Team Lead (acting as Merge Captain) or the integrator-merge-captain persona.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| bean_id | String | Yes | Bean identifier (e.g., `BEAN-011` or `11`) |
| target_branch | String | No | Branch to merge into (default: `main`) |
| bean_dir | Directory | Yes | `ai/beans/BEAN-NNN-<slug>/` — resolved from bean_id |

## Process

### Phase 1: Validation

1. **Resolve bean directory** — Find the bean directory matching the ID in `ai/beans/`.
2. **Read bean status** — Parse `bean.md`. Confirm status is `Done`.
   - If not `Done`: report `BeanNotDone` error and exit.
2a. **VDD gate** — Confirm a passing VDD report exists at the canonical
    path `ai/outputs/tech-qa/vdd-<NNN>.md` (zero-padded NNN to match the
    bean ID).
    - If the file is missing: report `VDDMissing` error naming the bean
      and exit. Suggest re-running `/vdd <bean-id>`.
    - Read the file. If the **Aggregate verdict** line is `FAIL` or
      `EMPTY`: report `VDDFail` error with the verdict and the report
      path, and exit.
    - `PARTIAL` is allowed only when the bean has a manual sign-off
      note in its Notes section (Team-Lead override). Otherwise refuse
      with `VDDPartial`.
    - `PASS` proceeds to Step 3.
3. **Aggregate telemetry** — Before merging, compute and fill the bean's Telemetry summary table:
   - Read all per-task rows from the bean's Telemetry table in `bean.md`.
   - **Total Tasks:** count of task rows with data.
   - **Total Duration:** sum all task durations. Parse `Xm` and `Xh Ym` formats, sum minutes, format result as `Xm` (under 1h) or `Xh Ym` (1h+).
   - **Total Tokens In:** sum all Tokens In values (parse comma-formatted numbers). Format result with commas.
   - **Total Tokens Out:** sum all Tokens Out values. Format result with commas.
   - Write the computed totals to the bean's Telemetry summary table (replacing `—` placeholders).
   - If telemetry data is missing or incomplete, fill what is available and note gaps.
4. **Derive feature branch name** — Extract from the bean directory name: `bean/BEAN-NNN-<slug>`.
5. **Verify feature branch exists** — Run `git branch --list bean/BEAN-NNN-<slug>`.
   - If not found: report `BranchNotFound` error and exit.

### Phase 2: Prepare Target

6. **Checkout target branch** — `git checkout main` (or specified target).
   - If the target branch doesn't exist locally: this is an error — `main` should always exist.
7. **Pull latest** — `git pull origin main`.
   - If the remote branch doesn't exist yet (first merge), skip pull.

### Phase 3: Merge

8. **Merge feature branch** — `git merge bean/BEAN-NNN-<slug> --no-ff`.
   - The `--no-ff` flag preserves a merge commit even if fast-forward is possible, making the merge visible in history.
9. **Check merge result**:
   - **Clean merge**: proceed to Phase 4.
   - **Conflict**: go to Conflict Handling (below).

### Phase 4: Push & Cleanup

10. **Push to remote** — `git push origin main`.
    - If push fails (e.g., another worker pushed first), pull and retry once.
11. **Delete feature branch** — `git branch -d bean/BEAN-NNN-<slug>`.
    - If the branch is also on the remote: `git push origin --delete bean/BEAN-NNN-<slug>`.
    - If delete fails (e.g., worktree reference), log a warning but continue.
12. **Return to main** — `git checkout main`.
13. **Report success** — Output: bean title, feature branch name (deleted), target branch, merge commit hash, and telemetry summary totals.

### Conflict Handling

If step 9 detects merge conflicts:

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
| `VDDMissing` | `ai/outputs/tech-qa/vdd-<NNN>.md` does not exist | Run `/vdd <bean-id>` and re-attempt the merge |
| `VDDFail` | VDD report's aggregate verdict is `FAIL` | Fix the failing criteria, re-run `/vdd`, retry merge |
| `VDDPartial` | VDD report's aggregate verdict is `PARTIAL` (manual items) | Tech-QA confirms manually; re-run `/vdd --manual=pass` or add a Notes override |
| `VDDEmpty` | Bean has no Acceptance Criteria | Add criteria to the bean and re-run VDD |
| `BranchNotFound` | Feature branch doesn't exist in git | Was the bean processed with `--no-branch`? Create branch manually or skip merge |
| `MergeConflict` | Auto-merge fails due to conflicting changes | Report files, abort merge, return to feature branch |
| `PushFailure` | Push rejected or network error | Pull and retry once; if still failing, report for manual resolution |
| `TargetNotFound` | Target branch doesn't exist on remote | Verify repository setup — `main` should always exist |

## Dependencies

- Bean must have status `Done` in its `bean.md`
- VDD report at `ai/outputs/tech-qa/vdd-<NNN>.md` with aggregate verdict
  `PASS` (see `claude/skills/vdd/SKILL.md`)
- Feature branch `bean/BEAN-NNN-<slug>` must exist
- Git repository in a clean state (no uncommitted changes)
- Push permissions for the target branch (see `.claude/hooks/hook-policy.md`)
