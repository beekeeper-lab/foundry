# BEAN-260: Approval Gate — Command + Criteria

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-260 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 19:02 |
| **Completed** | 2026-04-17 19:19 |
| **Duration** | 1270h 11m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

External audit (2026-04-17): "No approval gate defined. Bean lifecycle says Unapproved → Approved, but no command, no owner, no criteria for the transition. In practice approvals will happen silently or not at all."

The bean workflow documents the `Unapproved → Approved` transition but doesn't specify the mechanism. In practice, users edit the Status field manually and update `_index.md`. There is no command, no criteria checklist, no audit trail, and no default owner. This is a correctness gap — beans slip into execution without deliberate gating.

## Goal

Transitioning a bean from `Unapproved` → `Approved` is a deliberate, documented action with:
- A command (`/approve-bean NNN` or `/internal:approve-bean`) that performs the edits.
- A documented checklist of approval criteria (complete Problem Statement, Goal, Scope, Acceptance Criteria; priority set; category set).
- A default owner (the user) and an audit trail (commit message with rationale).

## Scope

### In Scope
- Add `/internal:approve-bean NNN` (or `/approve-bean`) command + skill. The skill:
  1. Validates the bean has a non-empty Problem Statement, Goal, Scope, Acceptance Criteria, Priority, and Category.
  2. Fails with actionable messages if any are missing.
  3. If valid: sets Status to `Approved` in `bean.md` and in `_index.md`. Commits with a message that names the bean and optionally the approver's rationale.
- Documented approval checklist in `ai/context/bean-workflow.md` under an "Approval Gate" section.
- Tests: a well-formed bean approves cleanly; a malformed bean is rejected with specific field names.

### Out of Scope
- Multi-step approval (e.g., BA approval separate from stakeholder approval).
- Auto-approval heuristics.
- Retroactively validating every existing Approved bean.

## Acceptance Criteria

- [x] New skill `/internal:approve-bean` (or `/approve-bean`) exists with a clear SKILL.md.
- [x] Matching short command doc in `.claude/commands/` that invokes the skill.
- [x] Skill validates required fields before approving; rejects with actionable messages listing missing fields.
- [x] Skill updates `bean.md` Status and `_index.md` Status atomically (one commit).
- [x] `ai/context/bean-workflow.md` gains an "Approval Gate" section with the checklist.
- [x] Tests cover the happy path (valid bean) and at least two failure cases (missing criterion, missing scope).
- [x] All tests pass (`uv run pytest`).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention — sequential Developer → Tech-QA is appropriate for this bean's shared-resource writes (single skill + command + doc).

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement approve-bean validator, skill, command, and workflow docs | developer | — | Done |
| 2 | Verify approval gate implementation meets acceptance criteria | tech-qa | 1 | Done |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Naming.** "Internal" prefix follows the pattern of `/internal:trello-load`, `/internal:merge-bean`, etc. — skills that manipulate project state. Either naming is acceptable; pick one during implementation.

**Interaction with BEAN-073.** BEAN-073 "Approval Gate Wiring" is already Done — audit what it produced before implementing. This bean may be completing or extending that earlier work rather than starting from scratch.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Implement approve-bean validator, skill, command, and workflow docs | developer | < 1m | N/A (suspect) | N/A (suspect) | — |
| 2 | Verify approval gate implementation meets acceptance criteria | tech-qa | < 1m | N/A (suspect) | N/A (suspect) | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |