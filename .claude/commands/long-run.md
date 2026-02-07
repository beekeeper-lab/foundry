# /long-run Command

Claude Code slash command that puts the Team Lead in autonomous mode, processing beans from the backlog until the backlog is empty or no actionable beans remain. Supports sequential (default) and parallel (`--fast N`) modes.

## Purpose

Automates the manual loop of picking a bean, decomposing it into tasks, executing the team wave, verifying results, and committing — then moving on to the next bean. The Team Lead selects beans based on priority, dependencies, and logical ordering.

## Usage

```
/long-run [--fast N]
```

- `--fast N` -- Run N beans in parallel using tmux child windows (optional).

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Backlog | `ai/beans/_index.md` | Yes (must exist with at least one actionable bean) |
| Bean workflow | `ai/context/bean-workflow.md` | Yes (reference for lifecycle) |
| tmux session | Environment (`$TMUX`) | Required only when `--fast` is used |

## Process

1. **Read backlog** — Parse `ai/beans/_index.md`. Identify beans with status `New` or `Picked`.
2. **Check for actionable beans** — If no beans are actionable (all `Done`, `Deferred`, or blocked by dependencies), report "Backlog clear — no actionable beans" and stop.
3. **Select best bean** — Apply selection heuristics (see Options below) to choose the single best bean to work on next.
4. **Pick the bean** — Update status to `In Progress` in both `bean.md` and `_index.md`. Set owner to `team-lead`.
5. **Create feature branch** — Create and checkout `bean/BEAN-NNN-<slug>` from current HEAD. All work for this bean happens on this branch.
6. **Decompose into tasks** — Read the bean's Problem Statement, Goal, Scope, and Acceptance Criteria. Create numbered task files in the bean's `tasks/` directory. Assign owners and dependencies following the wave: BA → Architect → Developer → Tech-QA (skip roles not needed).
7. **Execute the wave** — Process each task in dependency order:
   - Read the task file and all referenced inputs
   - Produce the required outputs in `ai/outputs/<persona>/`
   - Update the task status to `Done`
8. **Verify acceptance criteria** — Check every criterion in the bean's AC list. Run tests and lint if applicable.
9. **Close the bean** — Update status to `Done` in both `bean.md` and `_index.md`.
10. **Commit on feature branch** — Stage all changed files and commit with message: `BEAN-NNN: <title>`. The commit goes on the `bean/BEAN-NNN-<slug>` branch.
11. **Merge to test** — Execute `/merge-bean` to merge the feature branch into `test`: checkout test, pull latest, merge with `--no-ff`, push. If merge conflicts occur, report and stop.
12. **Return to main** — Checkout the main branch: `git checkout main`.
13. **Report progress** — Summarize what was completed: bean title, tasks executed, branch name, merge commit, files changed.
14. **Loop** — Go back to step 1. Continue until no actionable beans remain.

## Output

| Artifact | Path | Description |
|----------|------|-------------|
| Task files | `ai/beans/BEAN-NNN-<slug>/tasks/` | Decomposed tasks for each bean |
| Persona outputs | `ai/outputs/<persona>/` | Work products from each task |
| Updated beans | `ai/beans/BEAN-NNN-<slug>/bean.md` | Status updates through lifecycle |
| Updated index | `ai/beans/_index.md` | Status changes for processed beans |
| Git commits | Git history | One commit per completed bean |
| Progress report | Console output | Summary after each bean completes |

## Options

### Bean Selection Heuristics

The Team Lead selects the next bean using these criteria in priority order:

| Priority | Criterion | Example |
|----------|-----------|---------|
| 1 | **Explicit priority** | High > Medium > Low |
| 2 | **Inter-bean dependencies** | If BEAN-X depends on BEAN-Y, do Y first |
| 3 | **Logical ordering** | Infrastructure before features, data models before UI |
| 4 | **ID order** | Lower IDs first (tiebreaker) |

Dependencies between beans may be stated in the bean's Notes section or Scope section. The Team Lead should read candidate beans to assess implicit dependencies even when not explicitly stated.

### Parallel Mode (`--fast N`)

When `--fast N` is specified, the Team Lead orchestrates N parallel workers instead of processing beans sequentially.

**tmux detection:**
1. Check if `$TMUX` environment variable is set.
2. If not in tmux, display: "Parallel mode requires tmux. Please restart Claude Code inside a tmux session and re-run `/long-run --fast N`."
3. If in tmux, proceed with worker spawning.

**Worker spawning:**
1. Select up to N independent beans from the backlog (beans with no unmet inter-bean dependencies).
2. For each selected bean, spawn a tmux child window:
   ```
   tmux new-window -n "bean-NNN" "claude --print '
   Process BEAN-NNN-<slug> through the full team wave:
   1. Create feature branch bean/BEAN-NNN-<slug>
   2. Decompose into tasks
   3. Execute the wave (BA → Architect → Developer → Tech-QA)
   4. Verify acceptance criteria
   5. Commit on the feature branch
   6. Update bean status to Done
   '"
   ```
3. The main window remains the orchestrator — it does not process beans itself.

**Bean assignment rules:**
- Only assign beans that have no unmet dependencies on other in-progress or pending beans.
- If fewer than N independent beans are available, spawn only as many workers as there are beans.
- As a worker completes its bean, check for newly-unblocked beans and assign the next one.

**Progress monitoring:**
- Periodically read `_index.md` to check for status changes (workers update it as they complete).
- Report progress in the main window as beans move to `Done`.
- When all workers are idle and no actionable beans remain, report completion and exit.

| Flag | Default | Description |
|------|---------|-------------|
| `--fast N` | Off (sequential) | Run up to N beans in parallel using tmux child windows |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `EmptyBacklog` | No beans in `_index.md` | Report "No beans in backlog" and stop |
| `NoActionableBeans` | All beans are `Done`, `Deferred`, or blocked | Report status summary and stop |
| `TaskFailure` | A task's acceptance criteria cannot be met | Report the failure, leave bean as `In Progress`, stop the loop |
| `TestFailure` | Tests or lint fail after implementation | Attempt to fix; if unresolvable, report and stop |
| `MergeConflict` | Git conflict during commit | Report the conflict and stop for manual resolution |
| `NotInTmux` | `--fast` used but `$TMUX` is not set | Instruct user to restart in tmux |
| `WorkerFailure` | A parallel worker fails on its bean | Report which worker/bean failed; other workers continue |

When the loop stops due to an error, the current bean remains `In Progress` so the user can inspect and resume. In parallel mode, a single worker failure does not stop other workers.

## Examples

**Run the full backlog:**
```
/long-run
```
Team Lead reads the backlog, picks the highest-priority unblocked bean, processes it through the team wave, commits, and moves on to the next. Continues until backlog is clear.

**Typical output after each bean:**
```
✓ BEAN-007 (Long Run Command) — Done
  Tasks: 01-developer (Done), 02-tech-qa (Done)
  Committed: a1b2c3d
  Remaining: 5 beans (3 actionable)
  Next: BEAN-006 (Backlog Refinement Command)
```

**When backlog is clear:**
```
✓ Long run complete
  Beans processed: 4
  Backlog status: 0 actionable, 2 deferred
```

**Parallel mode with 3 workers:**
```
/long-run --fast 3
```
Team Lead detects tmux, selects 3 independent beans, spawns 3 child windows. Each worker processes one bean on its own feature branch. As workers finish, the Team Lead assigns the next unblocked bean.

**Typical parallel output:**
```
⚡ Parallel mode: 3 workers
  Worker 1: BEAN-012 (User Auth) — In Progress
  Worker 2: BEAN-013 (Dashboard) — In Progress
  Worker 3: BEAN-014 (Mobile API) — In Progress

✓ Worker 2: BEAN-013 (Dashboard) — Done [bean/BEAN-013-dashboard]
  Assigning: BEAN-015 (Notifications) → Worker 2

✓ All workers idle. Long run complete.
  Beans processed: 5 (3 parallel + 2 sequential)
  Backlog status: 0 actionable
```
