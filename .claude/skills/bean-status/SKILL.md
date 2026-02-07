# Skill: Bean Status

## Description

Reads the beans backlog and produces a formatted summary of all beans grouped by status. Optionally includes task-level detail for active beans. This is the Team Lead's dashboard command for understanding what work is new, in progress, or complete.

## Trigger

- Invoked by the `/bean-status` slash command.
- Called by the Team Lead during planning, standups, or retrospectives.
- Can be invoked by any persona who wants to see the current backlog state.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| filter | Enum: `new`, `picked`, `in-progress`, `done`, `deferred` | No | Show only beans with this status. Default: show all. |
| verbose | Boolean | No | Include task breakdown for active beans. Default: false. |

## Process

1. **Read backlog index** -- Parse `ai/beans/_index.md` to extract the Backlog table. For each row, capture: Bean ID, Title, Priority, Status, Owner.

2. **Enrich with task data** (if `--verbose`) -- For each bean that is `Picked` or `In Progress`:
   - Read the bean's `bean.md`
   - Parse the Tasks table to count: total tasks, pending, in progress, done
   - Note any blocked tasks

3. **Apply filter** -- If a status filter is provided, include only beans matching that status.

4. **Group by status** -- Organize beans into groups:
   - In Progress (most important — active work)
   - Picked (next up)
   - New (backlog)
   - Deferred (parked)
   - Done (completed)

5. **Format output** -- Produce a readable summary:
   ```
   ## Bean Backlog Summary

   **Totals:** 3 Done | 1 In Progress | 2 New

   ### In Progress
   | Bean ID | Title | Priority | Owner | Tasks |
   |---------|-------|----------|-------|-------|
   | BEAN-003 | Bean Commands | Medium | team-lead | 1/2 done |

   ### New
   | Bean ID | Title | Priority |
   |---------|-------|----------|
   | BEAN-001 | Backlog Seeding | Medium |
   ```

6. **Highlight actionable items** -- At the bottom, add a "Next Actions" section:
   - Beans with status `New` that are ready to pick
   - Beans `In Progress` with all tasks `Done` that are ready to close
   - Beans `In Progress` with blocked tasks

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| status_summary | Text | Formatted backlog summary displayed in the conversation |

## Quality Criteria

- All beans in `_index.md` are represented in the output.
- Status counts are accurate.
- Task counts (in verbose mode) match the actual task files.
- The output is scannable — a Team Lead can understand the backlog state in 10 seconds.
- Actionable items are highlighted so the Team Lead knows what to do next.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `IndexNotFound` | `ai/beans/_index.md` does not exist | No beans backlog — create it with `/new-bean` |
| `EmptyBacklog` | Index has no bean rows | Create beans with `/new-bean` |

## Dependencies

- Backlog index at `ai/beans/_index.md`
- Individual bean files at `ai/beans/BEAN-{NNN}-{slug}/bean.md` (for verbose mode)
