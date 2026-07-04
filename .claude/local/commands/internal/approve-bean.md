---
name: approve-bean
description: "Makes bean approval a deliberate, audited action. Without this command, beans move from Unapproved to Approved via manual edits that can skip validation. The command refuses to approve beans with missing required fields, eliminating the 'approved but incomplete' failure mode called out by the 2026-04-17 external audit."
---

# /internal:approve-bean Command

Approve a bean — gate the `Unapproved → Approved` transition behind a criteria check, then update `bean.md` and `_index.md` atomically.

## Purpose

Makes bean approval a deliberate, audited action. Without this command, beans move from `Unapproved` to `Approved` via manual edits that can skip validation. The command refuses to approve beans with missing required fields, eliminating the "approved but incomplete" failure mode called out by the 2026-04-17 external audit.

## Usage

```
/internal:approve-bean <NNN> [--rationale "<text>"]
```

- `<NNN>` — Bean identifier (e.g., `260` or `BEAN-260`).
- `--rationale` — Optional short note explaining the approval decision. Recorded in the commit body.

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Bean ID | Positional argument | Yes |
| Rationale | `--rationale` flag | No |

## Process

1. **Resolve** — Locate `ai/beans/BEAN-NNN-*/bean.md`.
2. **Guard** — If current Status is not `Unapproved`, report and exit (no changes).
3. **Validate** — Call `foundry_app.services.bean_approval.check_bean_approvable()`. If `ok=False`, print the missing-field list and exit without editing.
4. **Approve** — Set Status to `Approved` in `bean.md` and the matching row of `ai/beans/_index.md`.
5. **Commit** — Single commit: `Approve BEAN-NNN: <title>`, with `Rationale: <text>` in the body when provided.
6. **Report** — Print bean ID, title, and commit hash.

## Output

| Artifact | Path | Description |
|----------|------|-------------|
| Updated bean | `ai/beans/BEAN-NNN-<slug>/bean.md` | Status changed to `Approved` |
| Updated index | `ai/beans/_index.md` | Backlog row status updated |
| Commit | git | One commit that includes both file changes |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--rationale <text>` | None | Short justification recorded in the commit message body |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `BeanNotFound` | No bean directory matches the ID | Verify the ID with `/show-backlog` |
| `AlreadyTransitioned` | Status is not `Unapproved` | Bean has already left the approval gate — no action needed |
| `ValidationFailed` | Required fields are missing or placeholder | Populate the listed fields in `bean.md` and retry |
| `IndexRowNotFound` | Bean missing from `_index.md` | Re-add the bean to the backlog index |

## Examples

**Approve a bean with a rationale:**
```
/internal:approve-bean 260 --rationale "Closes the audit gap on silent approvals."
```

**Approve without a rationale:**
```
/internal:approve-bean 260
```

**Rejected approval (validation fails):**
```
$ /internal:approve-bean 261
Cannot approve BEAN-261: missing or placeholder fields:
  - Scope
  - Acceptance Criteria
Fix these fields in ai/beans/BEAN-261-*/bean.md and retry.
```
