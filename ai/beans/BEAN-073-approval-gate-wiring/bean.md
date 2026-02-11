# BEAN-073: Approval Gate Wiring

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-073 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-09 |
| **Completed** | 2026-02-09 |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

Beans created by `/backlog-refinement` go straight to `New` status and can be immediately picked up by `/long-run`. There is no human approval gate — the user has no chance to review scope, priority, or acceptance criteria before work begins. The status lifecycle needs a new `Unapproved` state and the `Picked` state should be dropped (it serves no practical purpose).

## Goal

Implement the new bean lifecycle: `Unapproved → Approved → In Progress → Done`. Update all skills, commands, agents, and docs that reference bean statuses. Drop the `Picked` status entirely.

## Scope

### In Scope
- New lifecycle: `Unapproved → Approved → In Progress → Done` (plus `Deferred`)
- Update `_bean-template.md`: default status to `Unapproved`
- Update `_index.md`: status key table with new statuses, drop `Picked`
- Update `/backlog-refinement`: create beans as `Unapproved`
- Update `/new-bean`: default status to `Unapproved`
- Update `/long-run`: only pick `Approved` beans (skip `Unapproved`)
- Update `/spawn-bean`: same — only pick `Approved` beans
- Update `/pick-bean`: only allow picking `Approved` beans, go straight to `In Progress` (remove `Picked` logic)
- Update `/bean-status`: replace `Picked` with `Unapproved`/`Approved` grouping
- Update `/show-backlog`: update `--status` filter values
- Update `/backlog-consolidate`: default filter from `New` to `Unapproved`
- Update `.claude/agents/team-lead.md`: lifecycle references
- Update `README.md`: Bean Lifecycle section

### Out of Scope
- Obsidian integration (that's BEAN-072)
- Migrating existing beans (all 71 are `Done`, no migration needed)
- Adding approval timestamps or approval-by fields

## Acceptance Criteria

- [x] `_bean-template.md` has `Unapproved` as default status
- [x] `/backlog-refinement` creates beans with status `Unapproved`
- [x] `/new-bean` creates beans with status `Unapproved`
- [x] `/long-run` skips `Unapproved` beans, only picks `Approved`
- [x] `/spawn-bean` only picks `Approved` beans
- [x] `/pick-bean` only accepts `Approved` beans, transitions to `In Progress`
- [x] `/pick-bean` no longer has a `Picked` state or `--start` flag distinction
- [x] `/bean-status` shows `Unapproved` and `Approved` groups, no `Picked`
- [x] `/show-backlog` accepts `unapproved` and `approved` as filter values
- [x] `/backlog-consolidate` defaults to `Unapproved`
- [x] `_index.md` status key reflects new lifecycle
- [x] Team Lead agent references updated lifecycle
- [x] README Bean Lifecycle section updated
- [x] No references to `Picked` or `New` status remain in skills/commands/agents
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- BEAN-072 (Obsidian review skill) depends on this bean for the `Unapproved` status to exist
- BEAN-074 (workflow docs) depends on this bean for the canonical lifecycle definition
- All 71 existing beans are `Done` — no migration needed
- The `Deferred` status is unchanged

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 7s).
