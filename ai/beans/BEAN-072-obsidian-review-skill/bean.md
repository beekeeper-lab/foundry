# BEAN-072: Obsidian Review Skill

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-072 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-09 |
| **Completed** | 2026-02-09 |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

There is no way to review beans outside the terminal. The Team Lead creates beans via `/backlog-refinement`, but the user has no comfortable way to read, edit, and approve them before they enter the execution pipeline. Obsidian provides a rich markdown editing environment ideal for reviewing bean specs.

## Goal

A new `/review-beans` skill + command that generates a filtered Map of Content (MOC) file linking to beans matching a given status and/or category, then opens Obsidian pointed at the `ai/beans/` directory. The user can review and edit bean files directly — including changing status from `Unapproved` to `Approved`.

## Scope

### In Scope
- New skill: `.claude/skills/review-beans/SKILL.md`
- New command: `.claude/commands/review-beans.md`
- Generate a filtered MOC file (`ai/beans/_review.md`) with links to matching beans
- Accept `--status` and `--category` filters (default: `--status unapproved`)
- Open Obsidian via `obsidian://open?vault=...` URI or `obsidian` CLI pointing at `ai/beans/`
- MOC includes bean title, status, priority, and category for quick scanning

### Out of Scope
- Syncing a separate Obsidian vault (edits happen in-place on real files)
- Obsidian plugins or custom themes
- Automatic detection of status changes (the user edits, `/long-run` reads)

## Acceptance Criteria

- [x] `/review-beans` command exists and is documented
- [x] `/review-beans` generates `ai/beans/_review.md` with filtered bean links
- [x] Default filter is `--status unapproved`
- [x] `--category` filter works (App, Process, Infra)
- [x] Obsidian opens targeting the beans directory
- [x] User can edit bean status in Obsidian and changes persist (they're editing real files)
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-073 (approval gate wiring) for the `Unapproved` status to exist
- Obsidian URI scheme: `obsidian://open?vault=beans&path=_review.md` or similar
- If Obsidian is not installed, fall back to printing the MOC path for manual opening

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

> Duration backfilled from git timestamps (commit→merge, 31s).
