# BEAN-015: Long Run Category Filter

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-015 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The `/long-run` command currently processes all actionable beans in the backlog regardless of type. With the new category system (App, Process, Infra), there's no way to tell the team lead "only work on Process beans" or "only work on Infra beans." This matters because different categories may need different environments, review gates, or sequencing — and sometimes you want to batch all the Process changes together without touching App code.

## Goal

Add a `--category` (or `-c`) flag to the `/long-run` command that filters the backlog to only process beans matching the specified category. When provided, the team lead skips beans outside that category during backlog assessment. Works in both sequential and parallel (`--fast N`) modes.

## Scope

### In Scope
- Add `--category` input to the long-run skill (`SKILL.md`)
- Update Phase 1 (Backlog Assessment) to filter by category when the flag is present
- Update Parallel Phase 2 to filter by category when the flag is present
- Update the long-run command definition to accept the new flag
- Support values: `App`, `Process`, `Infra` (case-insensitive)
- When no `--category` is provided, behavior is unchanged (all actionable beans)
- Update announcement/reporting to show which category filter is active

### Out of Scope
- Multi-category filtering (e.g., `--category App,Process`) — keep it simple, one at a time
- Changes to bean selection heuristics beyond the category filter
- Changes to the bean template or index format (already done in BEAN-014 work)
- New categories beyond App/Process/Infra

## Acceptance Criteria

- [ ] `/long-run --category Process` processes only beans with Category = Process
- [ ] `/long-run --category App` processes only beans with Category = App
- [ ] `/long-run --category Infra` processes only beans with Category = Infra
- [ ] Category matching is case-insensitive (`process`, `Process`, `PROCESS` all work)
- [ ] `/long-run` without `--category` processes all actionable beans (no regression)
- [ ] `/long-run --fast 3 --category Process` works in parallel mode
- [ ] The announcement step reports which category filter is active
- [ ] If no actionable beans match the category, the command reports cleanly and exits
- [ ] Long-run SKILL.md documents the new `--category` input
- [ ] Long-run command definition includes `--category` flag
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Update long-run SKILL.md with --category input and filtering logic | developer | — | Done |
| 2 | Update long-run command definition to accept --category flag | developer | 1 | Done |
| 3 | Verify filtering works in sequential and parallel modes | tech-qa | 1, 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on the category infrastructure from BEAN-014 work (categories in `_index.md` and each `bean.md`).
- The category field is read from `_index.md` during backlog assessment, so no need to open each bean.md individually for filtering.
- This bean should be run after the other agent finishes BEAN-014 to ensure the category field is stable.

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

> Duration backfilled from git timestamps (single commit, no merge).
