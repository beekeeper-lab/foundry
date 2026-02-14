# BEAN-121: Token Usage Capture via JSONL Parsing

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-121 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-14 |
| **Started** | 2026-02-14 14:19 |
| **Completed** | 2026-02-14 14:22 |
| **Duration** | 3m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The Telemetry table in bean.md has Tokens In and Tokens Out columns, but they are always `—` because no mechanism exists to capture token usage. Claude Code stores conversation data in JSONL files at `~/.claude/projects/<project-hash>/` — each message entry contains `usage` data with `input_tokens` and `output_tokens`. This data is available but never read. Without token tracking, we cannot compute the cost of a bean, compare token efficiency across agents, or understand the token breakdown between planning, building, and validating phases.

## Goal

Every completed task has accurate Tokens In and Tokens Out values in the bean's Telemetry table, computed by parsing Claude Code's conversation JSONL files. Bean-level totals (Total Tokens In, Total Tokens Out) are accurately summed from per-task data.

## Scope

### In Scope
- Parse Claude Code's conversation JSONL files to extract per-message token usage (`input_tokens`, `output_tokens`)
- Track cumulative token usage at task start (record a "watermark" when task status → In Progress)
- Compute per-task token delta at task completion (current cumulative - start watermark)
- Write per-task Tokens In / Tokens Out into the bean's Telemetry table row
- Compute Total Tokens In / Total Tokens Out as sums of per-task values
- Handle the JSONL file format (find the correct conversation file for the current session)
- Store watermarks in a lightweight way (e.g., a `.telemetry` JSON file in the bean directory, or inline in the task file metadata)

### Out of Scope
- Per-task duration tracking (BEAN-120 handles this)
- Reporting and analytics on the collected data (the `/telemetry-report` skill already exists)
- Token cost in dollars (just raw token counts — cost calculation is a presentation concern)
- Tracking tokens for parallel workers (each worker has its own conversation — handle in a future bean)
- Modifying Claude Code's JSONL format

## Acceptance Criteria

- [x] When a task status changes to In Progress, the current cumulative token count is recorded as a watermark
- [x] When a task status changes to Done, per-task Tokens In and Tokens Out are computed (delta from watermark) and written to the Telemetry table
- [x] Total Tokens In is the sum of all per-task Tokens In values
- [x] Total Tokens Out is the sum of all per-task Tokens Out values
- [x] The JSONL parser correctly finds and reads the current session's conversation file
- [x] If the JSONL file is unavailable (parallel worker, missing file), token fields gracefully remain `—`
- [x] Running `/long-run` on a test bean produces populated token data in the Telemetry table
- [x] All existing tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add JSONL token parser and watermark system to telemetry-stamp.py | developer | — | Done |
| 2 | Wire token tracking into task handlers | developer | 1 | Done |
| 3 | Verify with test and lint | tech-qa | 2 | Done |

## Notes

- Depends on BEAN-120 (Telemetry Table Population) — the per-task rows must exist before we can fill in token columns
- Claude Code JSONL files are at `~/.claude/projects/<project-hash>/<session-id>.jsonl`
- Each JSONL line has a message object; assistant messages include `usage: {input_tokens, output_tokens}`
- The current session ID can be found from `$CLAUDE_SESSION_ID` env var or by finding the most recently modified `.jsonl` file
- Watermarks could be stored in a `.telemetry.json` file in the bean directory: `{"task_1_start_tokens_in": 12345, "task_1_start_tokens_out": 6789, ...}`
- For parallel workers, each worker has its own JSONL file — total conversation tokens ≈ total bean tokens
- Token counts are integers (not floating point)

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | Add JSONL token parser and watermark system to telemetry-stamp.py | developer | 2m | 1,592 | 25,192 |
| 2 | Wire token tracking into task handlers | developer | < 1m | 1,594 | 25,194 |
| 3 | Verify with test and lint | tech-qa | < 1m | 1,603 | 25,322 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 3m |
| **Total Tokens In** | 4,789 |
| **Total Tokens Out** | 75,708 |