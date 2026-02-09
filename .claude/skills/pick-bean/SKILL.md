# Skill: Pick Bean

## Description

Updates a bean's status from `New` to `Picked` (or `In Progress`), assigning ownership to the Team Lead. This is the formal act of selecting a bean from the backlog for decomposition and execution. Updates both the bean's own file and the backlog index to keep them in sync.

## Trigger

- Invoked by the `/pick-bean` slash command.
- Called by the Team Lead during sprint planning or backlog grooming.
- Should only be used by the Team Lead persona.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| bean_id | Text | Yes | Bean ID to pick (e.g., `BEAN-006`, `006`, or `6`) |
| start | Boolean | No | If true, set status to `In Progress` instead of `Picked`. Defaults to false. |

## Process

1. **Parse bean ID** -- Accept flexible formats:
   - `BEAN-006` → `BEAN-006`
   - `006` → `BEAN-006`
   - `6` → `BEAN-006`
   Zero-pad to three digits.

2. **Locate bean directory** -- Scan `ai/beans/` for a directory starting with `BEAN-{NNN}-`. If not found, error with `BeanNotFound`.

3. **Re-read `_index.md`** -- Check the bean's current status and owner in the index. Another agent may have claimed it since you last read the backlog.

4. **Read current state** -- Open the bean's `bean.md`. Parse the metadata table to get current Status and Owner.

5. **Check lock** -- Validate the bean is available:
   - `New` or `Deferred` (no Owner) → available, proceed
   - `Picked` or `In Progress` with **your** Owner → already yours, proceed (idempotent)
   - `Picked` or `In Progress` with **a different** Owner → error with `BeanLocked`: "Bean is claimed by another agent. Pick a different bean."
   - `Done` → error with `BeanDone`, cannot re-pick a completed bean

5. **Determine new status** -- If `start` is true: `In Progress`. Otherwise: `Picked`.

6. **Update bean.md** -- In the metadata table:
   - Set `Status` to the new status
   - Set `Owner` to `team-lead`
   - If `start` is true (status → In Progress): set `Started` to the current timestamp (`YYYY-MM-DD HH:MM`). This is when the bean clock starts.

7. **Update backlog index** -- In `ai/beans/_index.md`, find the row matching `BEAN-{NNN}` and update:
   - Status column to the new status
   - Owner column to `team-lead`

8. **Ensure test branch exists** -- Check if the `test` integration branch exists locally:
   - Run: `git branch --list test`
   - If it doesn't exist, create it: `git checkout -b test main && git checkout -` (create from main, then return)

9. **Create feature branch** -- Always create the feature branch when starting:
   - If `start` is true:
     - Derive the slug from the bean directory name (e.g., `BEAN-006-backlog-refinement`)
     - Run: `git checkout -b bean/BEAN-NNN-<slug>`
     - If the branch already exists, check it out instead of creating.
   - Feature branching is mandatory. Every bean gets its own branch.

10. **Confirm** -- Report: bean ID, title, new status, branch name, and next step:
    - If `Picked`: "Ready for review. Use `/pick-bean {id} --start` when ready to decompose."
    - If `In Progress`: "Ready for decomposition on branch `bean/BEAN-NNN-<slug>`. Create task files in `tasks/` subdirectory."

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| updated_bean | Markdown file | `bean.md` with Status and Owner updated |
| updated_index | Markdown file | `_index.md` with matching row updated |
| feature_branch | Git branch | `bean/BEAN-NNN-<slug>` (created when `--start` is used) |
| confirmation | Text | Bean ID, title, new status, branch name, and next step |

## Quality Criteria

- Both `bean.md` and `_index.md` are updated atomically (both or neither).
- Status transitions are valid: only `New` or `Deferred` beans can be picked.
- Owner is always set to `team-lead` when picking.
- The operation is idempotent: picking an already-picked bean is a no-op with a warning.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `BeanNotFound` | No bean directory matches the ID | Check `_index.md` for valid IDs |
| `AlreadyActive` | Bean is already `Picked` or `In Progress` by you | Warning only — no action needed |
| `BeanLocked` | Bean is `Picked` or `In Progress` with a different Owner | Pick a different bean — this one is claimed by another agent |
| `BeanDone` | Bean status is `Done` | Cannot re-pick; create a follow-up bean with `/new-bean` |

## Dependencies

- Backlog index at `ai/beans/_index.md`
- Bean file at `ai/beans/BEAN-{NNN}-{slug}/bean.md`
