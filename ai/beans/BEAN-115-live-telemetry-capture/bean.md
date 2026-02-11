# BEAN-115: Live Telemetry Capture Fix

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-115 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-10 |
| **Started** | 2026-02-10 20:56 |
| **Completed** | 2026-02-10 20:58 |
| **Duration** | 2m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The telemetry system (BEAN-080) was designed to auto-record duration and token usage when beans complete, but it isn't working in practice. The /close-loop skill, PostToolUse hook, and /long-run worker prompts all exist but produce empty telemetry rows. After the last /long-run processed 28 beans, every single one had blank telemetry. The root causes are: (1) workers don't compute duration from git timestamps at completion time, (2) token counts are never captured because there's no mechanism to read Claude session stats, and (3) the PostToolUse hook stamps timestamps but doesn't compute derived metrics.

## Goal

When a bean completes (via /long-run worker or manual workflow), its telemetry section is automatically populated with accurate duration (from git timestamps) and token usage (if available from the Claude session). No manual intervention required.

## Scope

### In Scope
- Audit /close-loop skill to understand why it produces empty telemetry
- Fix /close-loop to compute duration from git timestamps (branch create → current time or merge commit)
- Update /long-run worker prompt to ensure /close-loop is invoked with correct data
- Investigate token capture: check if Claude CLI exposes session token counts (e.g., via /cost, API headers, or session files)
- If token data is available, wire it into /close-loop
- If token data is not available, document the limitation and mark token fields as "N/A (not exposed by CLI)"
- Update PostToolUse hook if needed to support the capture flow
- Test with a real bean completion (manual or via /long-run)

### Out of Scope
- Backfilling historical data (that's BEAN-114)
- Telemetry reporting/aggregation (that's BEAN-116)
- Changing the telemetry table format in bean.md
- Per-task token breakdowns (bean-level totals are sufficient)

## Acceptance Criteria

- [ ] When a bean completes via /long-run, its Telemetry section has a non-empty duration value
- [ ] Duration is computed from git timestamps, not estimated or hardcoded
- [ ] Token capture is implemented if Claude CLI exposes the data, or documented as unavailable
- [ ] /close-loop skill produces correct telemetry when invoked manually
- [ ] /long-run worker prompt invokes /close-loop correctly at bean completion
- [ ] Tested with at least one real bean completion showing populated telemetry
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on understanding from BEAN-114 about which git timestamp approach works reliably
- The PostToolUse hook at `.claude/hooks/postToolUse-telemetry-stamp.sh` currently writes timestamps but doesn't compute duration
- Key files to audit: `.claude/skills/close-loop/`, `.claude/skills/long-run/SKILL.md` (worker prompt section), `.claude/hooks/`
- For token capture, check: `claude --help` for usage/cost commands, `~/.claude/` for session logs, Claude API response headers

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 2m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
