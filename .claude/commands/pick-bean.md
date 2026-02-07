# /pick-bean Command

Claude Code slash command that lets the Team Lead pick one or more beans from the backlog for decomposition and execution.

## Purpose

Updates a bean's status from `New` to `Picked` (or `In Progress`) in both the bean's own `bean.md` and the backlog index `_index.md`. This is the Team Lead's formal declaration that a bean has been selected for the current work cycle.

## Usage

```
/pick-bean <bean-id> [--start]
```

- `bean-id` -- The bean ID to pick (e.g., `BEAN-006` or just `6`).

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Bean ID | Positional argument | Yes |
| Start immediately | `--start` flag | No (defaults to `Picked` status) |

## Process

1. **Resolve bean** -- Parse the bean ID (accept `BEAN-006`, `006`, or `6`). Locate the bean directory in `ai/beans/`.
2. **Validate state** -- Confirm the bean's current status is `New` or `Deferred`. Warn if already `Picked` or `In Progress`.
3. **Update bean.md** -- Set Status to `Picked` (or `In Progress` if `--start` is used). Set Owner to `team-lead`.
4. **Update index** -- Update the matching row in `ai/beans/_index.md` with the new status and owner.
5. **Confirm** -- Display the bean ID, title, new status, and a reminder to decompose into tasks if starting.

## Output

| Artifact | Path | Description |
|----------|------|-------------|
| Updated bean | `ai/beans/BEAN-{NNN}-{slug}/bean.md` | Status and Owner fields updated |
| Updated index | `ai/beans/_index.md` | Matching row updated |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--start` | `false` | Set status directly to `In Progress` instead of `Picked` |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `BeanNotFound` | No bean directory matches the given ID | Check `ai/beans/_index.md` for valid IDs |
| `AlreadyActive` | Bean is already `Picked` or `In Progress` | No action needed — bean is already active |
| `BeanDone` | Bean status is `Done` | Cannot pick a completed bean — create a follow-up bean instead |

## Examples

**Pick a bean for review:**
```
/pick-bean BEAN-006
```
Sets BEAN-006 to `Picked` status with `team-lead` as owner.

**Pick and immediately start:**
```
/pick-bean 6 --start
```
Sets BEAN-006 to `In Progress` and assigns to `team-lead`. Ready for task decomposition.

**Pick by short ID:**
```
/pick-bean 3
```
Resolves to BEAN-003, sets status to `Picked`.
