---
name: approve-bean
description: "- Invoked by the /internal:approve-bean slash command. - Called by a reviewer (user or Team Lead) during the approval step of the bean lifecycle (see §2 Approval in ai/context/bean-workflow.md)."
---

# Skill: Approve Bean

## Description

Gates the `Unapproved → Approved` transition for a bean. Validates that the bean's required fields are populated, then flips its Status to `Approved` in both `bean.md` and `ai/beans/_index.md`, and records a commit with the approver's rationale. A bean that fails validation is refused with a list of missing fields — no status change, no commit.

## Trigger

- Invoked by the `/internal:approve-bean` slash command.
- Called by a reviewer (user or Team Lead) during the approval step of the bean lifecycle (see §2 Approval in `ai/context/bean-workflow.md`).

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| bean_id | String | Yes | Bean identifier (e.g., `BEAN-260` or `260`) |
| rationale | String | No | Optional short note on why the bean is being approved (appears in commit message) |

## Process

### Phase 1: Resolve & Validate

1. **Resolve bean directory** — Find `ai/beans/BEAN-NNN-*/` matching the supplied ID. If none exists, error with `BeanNotFound`.
2. **Read `bean.md`** — Verify current Status is `Unapproved`. If it is already `Approved`, `In Progress`, or `Done`, error with `AlreadyTransitioned` and exit (no commit).
3. **Run approval check** — Call the Python validator:
   ```python
   from foundry_app.services.bean_approval import check_bean_approvable
   result = check_bean_approvable(bean_md_path)
   ```
   The validator returns `ApprovalCheck(ok, missing, bean_id)`. It checks:
   - Metadata: **Priority** and **Category** are not placeholders.
   - Body: `## Problem Statement`, `## Goal`, `## Scope` (In Scope list), and `## Acceptance Criteria` each contain at least one non-boilerplate content line.
4. **On failure** — Print a human-readable message naming each missing field, e.g.:
   ```
   Cannot approve BEAN-260: missing or placeholder fields:
     - Scope
     - Acceptance Criteria
   Fix these fields in ai/beans/BEAN-260-*/bean.md and retry.
   ```
   Exit without modifying any file. No commit.

### Phase 2: Approve

5. **Update `bean.md`** — Set the `**Status**` metadata row to `Approved`.
6. **Update `ai/beans/_index.md`** — Find the backlog row for this bean and update its Status column to `Approved`. Preserve alignment.
7. **Stage and commit** — Stage both files and commit atomically with the message:
   ```
   Approve BEAN-NNN: <bean title>
   ```
   When `--rationale` is provided, append it as a body line: `Rationale: <text>`.
   The commit author is taken from the git identity — this is the audit trail for "who approved".
8. **Report** — Print the bean ID, title, and commit hash.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| updated_bean | Markdown file | `bean.md` with Status set to `Approved` |
| updated_index | Markdown file | `_index.md` row updated |
| commit | Git commit | Single commit containing both file updates |
| report | Console text | Bean ID, title, commit hash, and any applied rationale |

## Quality Criteria

- Validation runs before any edit — failures cause zero file changes.
- Both `bean.md` and `_index.md` are updated in a single commit (atomic).
- Commit message uniquely identifies the bean and captures the rationale when supplied.
- Already-Approved / In-Progress / Done beans cannot be re-approved.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `BeanNotFound` | No `ai/beans/BEAN-NNN-*/` directory matches the ID | Check the bean ID or list the backlog |
| `AlreadyTransitioned` | Bean status is not `Unapproved` | No action needed — bean has already left the approval gate |
| `ValidationFailed` | One or more required fields are missing or placeholder | Populate the named fields in `bean.md` and retry |
| `IndexRowNotFound` | Bean is missing from `ai/beans/_index.md` | Re-scan `_index.md` or re-add the bean with `/new-bean` |

## Dependencies

- Python validator at `foundry_app/services/bean_approval.py` (pytest-covered in `tests/test_bean_approval.py`).
- Bean template at `ai/beans/_bean-template.md` (defines the field shape and placeholder strings).
- Backlog index at `ai/beans/_index.md`.
