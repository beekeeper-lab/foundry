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

## Process

### Phase 1: Backlog Assessment

1. **Read the backlog index** — Parse `ai/beans/_index.md` to get all beans and their statuses.
2. **Filter actionable beans** — Select beans with status `New` or `Picked`. Exclude `Done`, `Deferred`, and beans blocked by unfinished dependencies.
3. **Check stop condition** — If no actionable beans exist, report final summary and exit.

### Phase 2: Bean Selection

4. **Read candidate beans** — For each actionable bean, read its `bean.md` to understand priority, scope, dependencies, and notes.
5. **Apply selection heuristics** — Choose the single best bean:
   - **Priority first:** High beats Medium beats Low.
   - **Dependencies second:** If Bean A depends on Bean B (stated in Notes or Scope), select B first.
   - **Logical order third:** Infrastructure and foundational work before features. Data models before UI. Shared utilities before consumers.
   - **ID order last:** Lower bean IDs first as a tiebreaker.
6. **Announce selection** — Report which bean was selected and why.

### Phase 3: Bean Execution

7. **Pick the bean** — Update status to `In Progress` in both `bean.md` and `_index.md`. Set owner to `team-lead`.
8. **Decompose into tasks** — Read the bean's Problem Statement, Goal, Scope, and Acceptance Criteria. Create numbered task files in `ai/beans/BEAN-NNN-<slug>/tasks/`:
   - Name: `01-<owner>-<slug>.md`, `02-<owner>-<slug>.md`, etc.
   - Follow the wave: BA → Architect → Developer → Tech-QA.
   - Skip roles when not needed (e.g., skip BA/Architect for markdown-only beans).
   - Each task file includes: Owner, Depends On, Goal, Inputs, Acceptance Criteria, Definition of Done.
9. **Update bean task table** — Fill in the Tasks table in `bean.md` with the created tasks.

### Phase 4: Wave Execution

10. **Execute tasks in dependency order** — For each task:
    - Read the task file and all referenced inputs.
    - Perform the work as the assigned persona.
    - Write outputs to `ai/outputs/<persona>/`.
    - Update the task status to `Done` in the task file and the bean's task table.
11. **Skip inapplicable roles** — If a role has no meaningful contribution for a bean (e.g., Architect for a documentation-only bean), skip it. Document the skip reason in the bean's Notes section.

### Phase 5: Verification & Closure

12. **Verify acceptance criteria** — Check every criterion in the bean's Acceptance Criteria section. For code beans: run tests (`uv run pytest`) and lint (`uv run ruff check`).
13. **Close the bean** — Update status to `Done` in both `bean.md` and `_index.md`.
14. **Commit changes** — Stage all files changed during this bean's execution. Commit with message: `BEAN-NNN: <bean title>`.
15. **Report progress** — Output a summary: bean title, tasks completed, files changed, remaining backlog status.

### Phase 6: Loop

16. **Return to Phase 1** — Read the backlog again. If actionable beans remain, process the next one. If not, report final summary and exit.

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

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `EmptyBacklog` | No beans in `_index.md` | Report and exit cleanly |
| `NoActionableBeans` | All remaining beans are `Done`, `Deferred`, or blocked | Report status summary and exit |
| `TaskFailure` | A task cannot be completed | Report failure details, leave bean `In Progress`, stop loop |
| `TestFailure` | Tests or lint fail | Attempt to fix; if unresolvable, report and stop |
| `CommitFailure` | Git error during commit | Report error and stop for manual resolution |

On error: the current bean stays `In Progress` and the loop stops. The user can inspect the state, fix the issue, and either re-run `/long-run` or manually complete the bean.

## Dependencies

- Backlog index at `ai/beans/_index.md`
- Bean workflow at `ai/context/bean-workflow.md`
- Individual bean files at `ai/beans/BEAN-NNN-<slug>/bean.md`
- Git repository in a clean state (no uncommitted changes)
