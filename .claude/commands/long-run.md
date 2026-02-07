# /long-run Command

Claude Code slash command that puts the Team Lead in autonomous mode, processing beans from the backlog sequentially until the backlog is empty or no actionable beans remain.

## Purpose

Automates the manual loop of picking a bean, decomposing it into tasks, executing the team wave, verifying results, and committing — then moving on to the next bean. The Team Lead selects beans based on priority, dependencies, and logical ordering.

## Usage

```
/long-run
```

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Backlog | `ai/beans/_index.md` | Yes (must exist with at least one actionable bean) |
| Bean workflow | `ai/context/bean-workflow.md` | Yes (reference for lifecycle) |

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
11. **Return to main** — Checkout the main branch: `git checkout main`. The feature branch is left ready for merge (see Merge Captain workflow).
12. **Report progress** — Summarize what was completed: bean title, tasks executed, branch name, files changed.
13. **Loop** — Go back to step 1. Continue until no actionable beans remain.

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

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `EmptyBacklog` | No beans in `_index.md` | Report "No beans in backlog" and stop |
| `NoActionableBeans` | All beans are `Done`, `Deferred`, or blocked | Report status summary and stop |
| `TaskFailure` | A task's acceptance criteria cannot be met | Report the failure, leave bean as `In Progress`, stop the loop |
| `TestFailure` | Tests or lint fail after implementation | Attempt to fix; if unresolvable, report and stop |
| `MergeConflict` | Git conflict during commit | Report the conflict and stop for manual resolution |

When the loop stops due to an error, the current bean remains `In Progress` so the user can inspect and resume.

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
