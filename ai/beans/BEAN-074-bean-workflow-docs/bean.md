# BEAN-074: Bean Workflow Docs Update

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-074 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

The bean workflow documentation in `ai/context/bean-workflow.md` describes the old lifecycle (`New → Picked → In Progress → Done`) and does not mention the Obsidian review process or the approval gate. After BEAN-073 changes the lifecycle and BEAN-072 adds Obsidian review, the canonical workflow spec needs to reflect reality.

## Goal

Update `ai/context/bean-workflow.md` to document the new `Unapproved → Approved → In Progress → Done` lifecycle, the Obsidian review step, and the approval gate that prevents unapproved beans from entering execution.

## Scope

### In Scope
- Update `ai/context/bean-workflow.md` lifecycle diagram and status table
- Document the Obsidian review process as part of the workflow
- Document the approval gate (what `/long-run` and `/pick-bean` check)
- Update the "Multi-Agent Environment" section if it references `Picked` or `New`
- Ensure consistency with the changes made in BEAN-073

### Out of Scope
- Changes to skills or commands (that's BEAN-073)
- Obsidian setup instructions (that's BEAN-072)
- Changes to application code

## Acceptance Criteria

- [ ] `ai/context/bean-workflow.md` shows `Unapproved → Approved → In Progress → Done` lifecycle
- [ ] No references to `Picked` or `New` status in the workflow doc
- [ ] Obsidian review process is documented as a step between creation and execution
- [ ] Approval gate behavior is documented (what checks `/long-run` performs)
- [ ] `Deferred` status is still documented
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-073 (approval gate wiring) for the canonical lifecycle definition
- Depends on BEAN-072 (Obsidian review skill) for the review process details

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
