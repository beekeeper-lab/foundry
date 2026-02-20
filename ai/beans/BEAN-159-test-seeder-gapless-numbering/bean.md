# BEAN-159: Test Seeder Task Numbering Is Gapless with Mixed Personas

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-159 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:11 |
| **Completed** | 2026-02-20 20:15 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

When the team includes both known and unknown personas, the seeder should produce gapless sequential task numbers (no skipped IDs from unrecognized personas). No test currently verifies this behavior.

## Goal

Add a test with `["developer", "unknown-role", "architect"]`, extract all row numbers from the output, and assert they form a contiguous 1..N sequence with no gaps. Confirms the counter logic handles adversarial input correctly.

## Scope

### In Scope
- Add a test verifying gapless task numbering with mixed known/unknown personas
- Test with a team list containing an unrecognized persona

### Out of Scope
- Modifying the seeder's numbering logic
- Changing how unknown personas are handled

## Acceptance Criteria

- [x] Test uses a team list with both known and unknown personas (e.g., `["developer", "unknown-role", "architect"]`)
- [x] Test extracts row numbers from seeder output and asserts they are contiguous 1..N
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add gapless numbering test with mixed personas | Developer | — | Done |
| 2 | Verify gapless numbering test | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention — sequential 2-task wave, single file modified.

## Notes

Ensures counter logic handles adversarial input correctly — no gaps from unrecognized personas.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6997cafe7efb03f79bd2ebcd |
| **Card Name** | Test seeder task numbering is gapless with mixed personas |
| **Card URL** | https://trello.com/c/kYNdilH5/32-test-seeder-task-numbering-is-gapless-with-mixed-personas |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add gapless numbering test with mixed personas | Developer | < 1m | 346,031 | 638 | $0.66 |
| 2 | Verify gapless numbering test | Tech-QA | 3m | 514,491 | 534 | $0.91 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 3m |
| **Total Tokens In** | 860,522 |
| **Total Tokens Out** | 1,172 |
| **Total Cost** | $1.57 |