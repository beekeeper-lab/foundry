# Task 04: Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01, 02, 03 |
| **Status** | Done |
| **Started** | 2026-02-16 01:04 |
| **Completed** | 2026-02-16 01:04 |
| **Duration** | < 1m |

## Goal

Verify all changes meet acceptance criteria. Run tests and lint.

## Acceptance Criteria

- [ ] `ai/context/token-pricing.md` has correct Opus 4 rates
- [ ] Bean template has Cost column and Total Cost row
- [ ] Telemetry report skill references config file and specifies cost computation
- [ ] telemetry-stamp.py reads pricing from config, computes cost, writes to bean.md
- [ ] `uv run pytest` passes
- [ ] `uv run ruff check foundry_app/ .claude/hooks/` lint clean
