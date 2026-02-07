# Skill: Long Run

## Description

Puts the Team Lead into autonomous backlog processing mode. The Team Lead reads the bean backlog, selects the best bean to work on, decomposes it into tasks, executes the full team wave, verifies acceptance criteria, commits the result, and loops to the next bean. Continues until no actionable beans remain or an unrecoverable error occurs.

## Trigger

- Invoked by the `/long-run` slash command.
- Should only be used by the Team Lead persona.
- Requires at least one bean in `_index.md` with status `New` or `Picked`.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| backlog | Markdown file | Yes | `ai/beans/_index.md` — master bean index |
| bean_workflow | Markdown file | Yes | `ai/context/bean-workflow.md` — lifecycle reference |
| bean_files | Markdown files | Yes | Individual `bean.md` files in `ai/beans/BEAN-NNN-<slug>/` |
| fast | Integer | No | Number of parallel workers. When provided, enables parallel mode via tmux. |
| category | String | No | Filter beans by category: `App`, `Process`, or `Infra`. Case-insensitive. When provided, only beans matching this category are processed. |
| tmux_session | Environment | No | `$TMUX` — required only when `fast` is provided |

## Process

### Phase 0: Mode Detection

0. **Check mode** — If `fast` input is provided, go to **Parallel Mode** (below). Otherwise, continue with sequential mode (Phase 1).

### Phase 1: Backlog Assessment

1. **Read the backlog index** — Parse `ai/beans/_index.md` to get all beans and their statuses.
2. **Filter actionable beans** — Select beans with status `New`, or `Picked` with no Owner or with your own Owner. Exclude `Done`, `Deferred`, beans blocked by unfinished dependencies, and beans locked by another agent (status `Picked` or `In Progress` with a different Owner). If `category` is provided, further filter to only beans whose Category column matches (case-insensitive).
3. **Check stop condition** — If no actionable beans exist (or none match the category filter), report final summary and exit. If category is active, mention it: "No actionable beans matching category: Process."

### Phase 2: Bean Selection

4. **Read candidate beans** — For each actionable bean, read its `bean.md` to understand priority, scope, dependencies, and notes.
5. **Apply selection heuristics** — Choose the single best bean:
   - **Priority first:** High beats Medium beats Low.
   - **Dependencies second:** If Bean A depends on Bean B (stated in Notes or Scope), select B first.
   - **Logical order third:** Infrastructure and foundational work before features. Data models before UI. Shared utilities before consumers.
   - **ID order last:** Lower bean IDs first as a tiebreaker.
6. **Announce selection** — Print the **Header Block** and **Task Progress Table** from the Team Lead Communication Template (see `.claude/agents/team-lead.md`). If a category filter is active, include it in the header: `[Category: Process]`. This is the first thing visible in the tmux pane.

### Phase 3: Bean Execution

7. **Pick the bean** — Update status to `In Progress` in both `bean.md` and `_index.md`. Set owner to `team-lead`.
8. **Ensure test branch exists** — Check if `test` branch exists locally. If not, create it: `git checkout -b test main && git checkout -`.
9. **Create feature branch** — Create and checkout the feature branch (mandatory for every bean):
   - Branch name: `bean/BEAN-NNN-<slug>` (derived from the bean directory name)
   - Command: `git checkout -b bean/BEAN-NNN-<slug>`
   - If the branch already exists (e.g., resuming after an error), check it out instead.
   - All work happens on this branch. Never commit to `main`.
10. **Decompose into tasks** — Read the bean's Problem Statement, Goal, Scope, and Acceptance Criteria. Create numbered task files in `ai/beans/BEAN-NNN-<slug>/tasks/`:
    - Name: `01-<owner>-<slug>.md`, `02-<owner>-<slug>.md`, etc.
    - Follow the wave: BA → Architect → Developer → Tech-QA.
    - Skip roles when not needed (e.g., skip BA/Architect for markdown-only beans).
    - Each task file includes: Owner, Depends On, Goal, Inputs, Acceptance Criteria, Definition of Done.
11. **Update bean task table** — Fill in the Tasks table in `bean.md` with the created tasks.

### Phase 4: Wave Execution

12. **Execute tasks in dependency order** — For each task:
    - Read the task file and all referenced inputs.
    - Perform the work as the assigned persona.
    - Write outputs to `ai/outputs/<persona>/`.
    - Update the task status to `Done` in the task file and the bean's task table.
    - Reprint the **Header Block + Task Progress Table** after each status change.
13. **Skip inapplicable roles** — If a role has no meaningful contribution for a bean (e.g., Architect for a documentation-only bean), skip it. Document the skip reason in the bean's Notes section.

### Phase 5: Verification & Closure

14. **Verify acceptance criteria** — Check every criterion in the bean's Acceptance Criteria section. For code beans: run tests (`uv run pytest`) and lint (`uv run ruff check`).
15. **Close the bean** — Update status to `Done` in both `bean.md` and `_index.md`.
16. **Commit on feature branch** — Stage all files changed during this bean's execution. Commit with message: `BEAN-NNN: <bean title>`. The commit goes on the `bean/BEAN-NNN-<slug>` branch.

### Phase 5.5: Merge Captain

17. **Merge to test branch** — Execute the `/merge-bean` skill to merge the feature branch into `test`:
    - Checkout `test`, pull latest, merge `bean/BEAN-NNN-<slug>` with `--no-ff`, push.
    - If merge conflicts occur: report the conflicts, abort the merge, leave the bean on its feature branch, and stop the loop.
    - If merge succeeds: continue.
18. **Return to main** — Checkout the main branch: `git checkout main`.
19. **Report progress** — Print the **Completion Summary** from the Team Lead Communication Template: bean title, task counts, branch name, files changed, notes, and remaining backlog status.

### Phase 6: Loop

20. **Return to Phase 1** — Read the backlog again. If actionable beans remain, process the next one. If not, report final summary and exit.

---

## Parallel Mode

When `fast N` is provided, the Team Lead orchestrates N parallel workers instead of processing beans sequentially.

### Parallel Phase 1: tmux Detection

1. **Check tmux** — Verify `$TMUX` environment variable is set.
   - If not set: display "Parallel mode requires tmux. Please restart Claude Code inside a tmux session and re-run `/long-run --fast N`." Then exit.
   - If set: proceed.

### Parallel Phase 2: Backlog Assessment

2. **Read the backlog index** — Same as sequential Phase 1: parse `_index.md`, filter actionable beans (skip locked beans owned by other agents). Apply `category` filter if provided.
3. **Check stop condition** — If no actionable beans (or none matching category), report and exit.
4. **Read candidate beans** — Read each actionable bean's `bean.md` to understand dependencies.

### Parallel Phase 3: Worker Spawning

5. **Select independent beans** — From the actionable set, select up to N beans that have no unmet inter-bean dependencies. Beans that depend on other pending or in-progress beans are queued, not parallelized.
6. **Update bean statuses** — Mark each selected bean as `In Progress` in both `bean.md` and `_index.md`. Set owner to `team-lead`.
7. **Spawn workers** — For each selected bean, open a tmux child window:
   ```
   tmux new-window -n "bean-NNN" "claude --print '
   Process BEAN-NNN-<slug> through the full team wave:
   1. Create feature branch bean/BEAN-NNN-<slug>
   2. Decompose into tasks
   3. Execute the wave (BA → Architect → Developer → Tech-QA)
   4. Verify acceptance criteria
   5. Commit on the feature branch
   6. Update bean status to Done
   7. Merge feature branch into test (Merge Captain)
   '"
   ```
8. **Record worker assignments** — Track which window is processing which bean.

### Parallel Phase 4: Progress Monitoring

9. **Monitor workers** — Periodically read `_index.md` to detect status changes as workers complete beans.
10. **Report completions** — As each worker finishes (bean moves to `Done`), report in the main window.
11. **Assign next bean** — When a worker becomes idle:
    - Re-read the backlog for newly unblocked beans.
    - If an independent actionable bean exists, assign it to the idle worker by spawning a new tmux window.
    - If no more beans, let the worker stay idle.

### Parallel Phase 5: Completion

12. **Check termination** — When all workers are idle and no actionable beans remain, report final summary and exit.
13. **Final report** — Output: total beans processed, parallel vs sequential breakdown, all branch names created, remaining backlog status.

### Bean Assignment Rules

- Only assign beans with no unmet dependencies on other in-progress or pending beans.
- If fewer than N independent beans are available, spawn only as many workers as there are beans.
- Never assign the same bean to multiple workers.
- The main window orchestrates only — it does not process beans itself.

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| task_files | Markdown files | Task decompositions in each bean's `tasks/` directory |
| persona_outputs | Various files | Work products in `ai/outputs/<persona>/` |
| updated_beans | Markdown files | Bean status updated through lifecycle |
| updated_index | Markdown file | `_index.md` kept in sync with bean statuses |
| git_commits | Git commits | One commit per completed bean |
| progress_reports | Console text | Summary after each bean and at completion |

## Quality Criteria

- Each bean goes through the complete lifecycle: pick → decompose → execute → verify → close.
- No bean is skipped without explanation.
- Bean selection follows the documented heuristics consistently.
- All acceptance criteria are verified before marking a bean as Done.
- Tests and lint pass for every code bean before closing.
- Each bean is committed separately for clean git history.
- The loop terminates cleanly when the backlog is empty.
- In parallel mode: dependent beans are never assigned simultaneously.
- In parallel mode: the main window orchestrates only, never processes beans itself.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `EmptyBacklog` | No beans in `_index.md` | Report and exit cleanly |
| `NoActionableBeans` | All remaining beans are `Done`, `Deferred`, or blocked | Report status summary and exit |
| `TaskFailure` | A task cannot be completed | Report failure details, leave bean `In Progress`, stop loop |
| `TestFailure` | Tests or lint fail | Attempt to fix; if unresolvable, report and stop |
| `CommitFailure` | Git error during commit | Report error and stop for manual resolution |
| `MergeConflict` | Merge to test branch fails due to conflicts | Report conflicting files, abort merge, stop loop |
| `NotInTmux` | `--fast` used but `$TMUX` is not set | Instruct user to restart in tmux |
| `WorkerFailure` | A parallel worker fails on its bean | Report which worker/bean failed; other workers continue |

On error in sequential mode: the current bean stays `In Progress` and the loop stops. The user can inspect the state, fix the issue, and either re-run `/long-run` or manually complete the bean.

On error in parallel mode: a single worker failure does not stop other workers. The failed bean stays `In Progress`. The main window reports the failure and continues monitoring remaining workers.

## Dependencies

- Backlog index at `ai/beans/_index.md`
- Bean workflow at `ai/context/bean-workflow.md`
- Individual bean files at `ai/beans/BEAN-NNN-<slug>/bean.md`
- Git repository in a clean state (no uncommitted changes)
