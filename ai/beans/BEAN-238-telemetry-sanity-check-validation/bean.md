# BEAN-238: Telemetry Sanity-Check Validation

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-238 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-03-27 |
| **Started** | 2026-03-27 15:03 |
| **Completed** | 2026-03-27 15:06 |
| **Duration** | 3m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The telemetry-stamp hook writes whatever token counts it computes without any plausibility check. This has produced beans with 15 input tokens (impossible — the system prompt alone is >10K tokens) and beans with 5M+ input tokens for 1 minute of work (plausible for billing but worth flagging). Without validation at write time, bad data enters the bean record and is only discovered later during manual review.

## Goal

The telemetry-stamp hook validates token counts before writing them and flags implausible values, preventing silently corrupt data from entering bean records.

## Scope

### In Scope
- Add plausibility bounds to `telemetry-stamp.py` before writing token data:
  - **Floor:** Any real Claude session has at least ~5,000 input tokens (system prompt + CLAUDE.md). Values below this threshold are suspect.
  - **Ceiling warning:** Input tokens >5M for a single task is unusual. Don't reject, but log a warning.
  - **Zero check:** If delta_in or delta_out is exactly 0, that likely means watermark == current (no work done) — flag it.
- When a value fails the floor check, write `N/A (suspect)` instead of the bad number
- Log the suspect value and reason to stderr so it's visible in hook output
- Add a `--validate` flag to the telemetry-report skill that scans all beans and reports rows with suspect data

### Out of Scope
- Fixing the root causes of bad data (BEAN-229, 230, 231)
- Auto-correcting bad data
- Changing the token pricing or cost computation logic

## Acceptance Criteria

- [ ] Token values below 5,000 input tokens are flagged as suspect and not written as real data
- [ ] Token values above 5M log a warning but are still written (they may be legitimately high)
- [ ] Zero-delta tokens are flagged and not written
- [ ] Stderr logs explain why a value was rejected
- [ ] `/telemetry-report --validate` lists all beans with suspect telemetry data
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Sanity Check Implementation | Developer | — | Done |
| 2 | Tech-QA Verification | Tech-QA | 01 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| .claude/shared (submodule) | +67 -2 |
| ai/beans/BEAN-238-.../bean.md | +29 -17 |
| ai/beans/BEAN-238-.../tasks/01-developer-sanity-checks.md | +43 |
| ai/beans/BEAN-238-.../tasks/02-tech-qa-verification.md | +35 |
| ai/beans/_index.md | +1 -1 |

## Notes

This bean is a safety net. Even after BEAN-235/236/237 fix the root causes, new edge cases may appear. Validation catches them at write time rather than during manual review weeks later.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Sanity Check Implementation | Developer | 2m | 3,599,542 | 3,269 | $5.80 |
| 2 | Tech-QA Verification | Tech-QA | < 1m | 296,032 | 313 | $0.49 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 2m |
| **Total Tokens In** | 3,895,574 |
| **Total Tokens Out** | 3,582 |
| **Total Cost** | $6.29 |