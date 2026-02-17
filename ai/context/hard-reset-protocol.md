# Hard Reset Protocol

Recovery procedures for common failure states during bean execution. Use when a bean worker, worktree, or branch gets stuck in a bad state and normal operations can't proceed.

## Pre-Reset Verification Checklist

Before resetting anything, gather information:

- [ ] Identify the stuck bean ID and its current status in `ai/beans/_index.md`
- [ ] Check the status file: `cat /tmp/foundry-worker-BEAN-NNN.status`
- [ ] Check if a worktree exists: `ls /tmp/foundry-worktree-BEAN-NNN/`
- [ ] Check branch state: `git branch --list 'bean/BEAN-NNN-*'`
- [ ] Check for uncommitted work in the worktree: `git -C /tmp/foundry-worktree-BEAN-NNN status` (if worktree exists)
- [ ] Check tmux for running workers: `tmux list-windows` / `tmux list-panes -t workers`
- [ ] Note any partial outputs in `ai/outputs/` or `ai/beans/BEAN-NNN-*/tasks/` that may be worth preserving

## Failure State 1: Stalled Worker

**Symptoms:** Worker tmux window/pane is unresponsive. Status file shows `running` but `updated` timestamp is stale (>5 minutes old). No output activity.

**Recovery:**

1. Kill the worker process:
   - **Separate window mode:** `tmux kill-window -t "bean-NNN"`
   - **Wide mode:** select the pane in the "workers" window and kill it with the tmux kill-pane shortcut
2. Check what work was completed — read the status file and task files:
   ```bash
   cat /tmp/foundry-worker-BEAN-NNN.status
   ls /tmp/foundry-worktree-BEAN-NNN/ai/beans/BEAN-NNN-*/tasks/
   ```
3. If partial work is worth keeping:
   - Commit it from the worktree: `git -C /tmp/foundry-worktree-BEAN-NNN add -A && git -C /tmp/foundry-worktree-BEAN-NNN commit -m "WIP: partial progress before reset"`
4. Remove the worktree: `git worktree remove --force /tmp/foundry-worktree-BEAN-NNN`
5. Clean the status file: `rm /tmp/foundry-worker-BEAN-NNN.status`
6. Reset bean status to `Approved` in `bean.md` and `_index.md` (clear Owner and Started fields)
7. Re-spawn: `/spawn-bean NNN`

## Failure State 2: Merge Conflicts

**Symptoms:** `/internal:merge-bean` reports conflicting files and aborts. The feature branch has diverged from `test`.

**Recovery:**

1. Ensure you are on the feature branch:
   ```bash
   git checkout bean/BEAN-NNN-slug
   ```
2. Merge `test` into the feature branch to surface conflicts locally:
   ```bash
   git merge test
   ```
3. Resolve each conflicted file manually — edit to keep the correct content, then:
   ```bash
   git add <resolved-file>
   ```
4. Complete the merge: `git commit` (accept or edit the merge message)
5. Verify the merged state:
   - `uv run pytest` — all tests pass
   - `uv run ruff check foundry_app/` — lint clean
6. Re-run `/internal:merge-bean NNN` — should now merge cleanly into `test`

**If conflicts are too complex to resolve:**

1. Abort: `git merge --abort`
2. Identify which other bean(s) caused the conflict by checking recent merges to `test`
3. Coordinate with the other bean's owner to agree on resolution
4. Consider rebasing the feature branch onto `test` instead: `git rebase test` (resolve conflicts incrementally per commit)

## Failure State 3: Corrupted Worktree

**Symptoms:** Worktree directory exists but git operations fail inside it (e.g., "not a git repository", "bad object", file permission errors). Or the worktree reference is stale — `git worktree list` shows it but the directory is missing or broken.

**Recovery:**

1. Kill any worker using this worktree (see Failure State 1, step 1)
2. Check if the feature branch has committed work worth preserving:
   ```bash
   git log main..bean/BEAN-NNN-slug --oneline
   ```
3. Force-remove the worktree:
   ```bash
   git worktree remove --force /tmp/foundry-worktree-BEAN-NNN
   ```
4. If that fails (dangling reference), prune stale entries:
   ```bash
   git worktree prune
   ```
5. Clean the status file: `rm -f /tmp/foundry-worker-BEAN-NNN.status`
6. If the feature branch has good commits, re-create the worktree:
   ```bash
   git worktree add /tmp/foundry-worktree-BEAN-NNN bean/BEAN-NNN-slug
   ```
7. If starting fresh, reset the bean to `Approved` and re-spawn

## Failure State 4: Broken Branch

**Symptoms:** Feature branch exists but is in a bad state — points to a bad commit, has been accidentally merged elsewhere, or has diverged in a way that can't be cleanly resolved.

**Recovery (preserve work):**

1. Create a backup branch before doing anything:
   ```bash
   git branch backup/BEAN-NNN-slug bean/BEAN-NNN-slug
   ```
2. Identify the last good commit on the branch:
   ```bash
   git log bean/BEAN-NNN-slug --oneline
   ```
3. Reset the branch to the last good commit:
   ```bash
   git branch -f bean/BEAN-NNN-slug <good-commit-hash>
   ```
4. If the branch needs to start fresh from main:
   ```bash
   git branch -f bean/BEAN-NNN-slug main
   ```
5. Remove and recreate the worktree (if one exists):
   ```bash
   git worktree remove --force /tmp/foundry-worktree-BEAN-NNN
   git worktree add /tmp/foundry-worktree-BEAN-NNN bean/BEAN-NNN-slug
   ```
6. Cherry-pick any good commits from the backup if needed:
   ```bash
   git -C /tmp/foundry-worktree-BEAN-NNN cherry-pick <commit-hash>
   ```

**Recovery (start over):**

1. Remove the worktree: `git worktree remove --force /tmp/foundry-worktree-BEAN-NNN`
2. Delete the branch: coordinate with the user — `git branch -D` is blocked by policy, so the user must approve this action
3. Reset bean status to `Approved` in `bean.md` and `_index.md`
4. Re-spawn: `/spawn-bean NNN` (creates a fresh branch and worktree)

## Failure State 5: Stuck Status Files

**Symptoms:** Status file shows `running` or `blocked` but no worker is actually running. Dashboard shows stale workers. Or status file is malformed/empty.

**Recovery:**

1. Confirm no worker is running for this bean:
   ```bash
   tmux list-windows | grep -i "bean-NNN"
   tmux list-panes -a | grep -i "bean-NNN"
   ```
2. If no worker is found, the status file is orphaned. Remove it:
   ```bash
   rm /tmp/foundry-worker-BEAN-NNN.status
   ```
3. Check the actual state of the bean — read `bean.md` and task files to determine real progress
4. If the bean was actually completed (all tasks done, outputs exist):
   - Update `bean.md` status to `Done`
   - Proceed with `/internal:merge-bean NNN`
5. If the bean is partially done:
   - Update task statuses in `bean.md` to reflect actual completion
   - Reset incomplete tasks to `Pending`
   - Re-spawn the worker: `/spawn-bean NNN`
6. To clean up all orphaned status files at once:
   ```bash
   rm /tmp/foundry-worker-*.status
   ```

## Post-Reset Verification Checklist

After performing any reset, verify the system is clean:

- [ ] No orphaned worktrees: `git worktree list` shows only expected entries
- [ ] No orphaned status files: `ls /tmp/foundry-worker-*.status` matches only active workers
- [ ] Bean status in `_index.md` and `bean.md` are consistent (same status, same owner)
- [ ] Feature branch is in expected state: `git log main..bean/BEAN-NNN-slug --oneline`
- [ ] No tmux windows/panes running dead workers: `tmux list-windows`
- [ ] If bean was reset to `Approved`: Owner is cleared, Started is `—`
- [ ] If bean was re-spawned: new status file exists and shows `starting` or `decomposing`
- [ ] Tests still pass on `test` branch (if a merge was involved): `uv run pytest`

## Quick Reference

| Failure | Key Command | Result |
|---------|-------------|--------|
| Kill worker | `tmux kill-window -t "bean-NNN"` | Stops the Claude process |
| Remove worktree | `git worktree remove --force /tmp/foundry-worktree-BEAN-NNN` | Cleans worktree directory |
| Prune stale refs | `git worktree prune` | Removes dangling worktree entries |
| Clean status file | `rm /tmp/foundry-worker-BEAN-NNN.status` | Removes orphaned status |
| Clean all status | `rm /tmp/foundry-worker-*.status` | Nuclear option for status files |
| Check worktrees | `git worktree list` | Shows all active worktrees |
| Re-spawn bean | `/spawn-bean NNN` | Creates fresh worktree + worker |
