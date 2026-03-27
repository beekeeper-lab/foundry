# BEAN-236: Telemetry Long-Run Batch Session Isolation

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-236 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-03-27 |
| **Started** | 2026-03-27 11:27 |
| **Completed** | 2026-03-27 11:37 |
| **Duration** | 10m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

When `/long-run` processes multiple beans in sequence within one Claude Code session, the telemetry watermark system breaks down. The watermark records the cumulative token count at task start, then computes a delta at task completion. However, when multiple beans are completed in rapid succession (e.g., BEAN-142 through BEAN-152 — all Process beans done in ~1 minute each), the watermarks either:

1. Are never saved because the task status transitions from Pending to Done in a single edit (skipping the "In Progress" state where watermarks are recorded)
2. Share the same JSONL session, so the delta between one bean's end and the next bean's start is near-zero

Evidence: BEAN-142 through BEAN-152 all show 15–113 total input tokens — impossibly low values that represent only the `input_tokens` field (non-cached) from perhaps a single API turn, not the full context.

## Goal

Token telemetry is accurate for beans processed sequentially in a single `/long-run` session, with each bean's token usage isolated from the others.

## Scope

### In Scope
- Investigate and fix the watermark save/load cycle for beans that transition directly to Done (skipping In Progress)
- Ensure `telemetry-stamp.py` saves a watermark when a task first appears as "In Progress" OR when it transitions directly to "Done" without a prior watermark
- If no watermark exists at Done time, compute tokens from the last known watermark (previous task's completion) rather than using full session tokens
- Add a "session token checkpoint" mechanism: after each task completion, record the current cumulative tokens so the next task's delta starts from the right baseline

### Out of Scope
- Worktree session resolution (BEAN-229)
- Missing session fallback behavior (BEAN-231)
- Changes to the `/long-run` skill itself
- Backfilling historical data

## Acceptance Criteria

- [ ] When a task goes from Pending to Done in one edit, a watermark is still recorded and delta computed
- [ ] Sequential tasks in one session have isolated token counts (task 2 doesn't include task 1's tokens)
- [ ] The checkpoint mechanism persists across bean boundaries within one session
- [ ] Process beans (which may involve only markdown edits, not code) still capture accurate token counts
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Watermark Checkpoint Mechanism | Developer | — | Done |
| 2 | Tech-QA Verification | Tech-QA | 01 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Part of a 3-bean split investigating telemetry accuracy. See also BEAN-235 (worktree session fix) and BEAN-237 (missing session fallback).

The key insight: BEAN-142 through BEAN-152 were all Process beans executed in a long-run batch. None have `.telemetry.json` watermark files. The telemetry values (15–113 tokens in) are impossibly low, suggesting the watermark was never saved and the fallback path produced garbage data.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Watermark Checkpoint Mechanism | Developer | 7m | 4,689,651 | 8,553 | $8.26 |
| 2 | Tech-QA Verification | Tech-QA | < 1m | 525,811 | 833 | $0.93 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 7m |
| **Total Tokens In** | 5,215,462 |
| **Total Tokens Out** | 9,386 |
| **Total Cost** | $9.19 |