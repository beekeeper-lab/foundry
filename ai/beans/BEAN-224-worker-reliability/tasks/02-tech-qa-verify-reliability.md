# Task 02: Verify Worker Reliability Improvements

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01-developer-update-worker-reliability |
| **Status** | Done |
| **Started** | 2026-02-21 18:10 |
| **Completed** | 2026-02-21 18:11 |
| **Duration** | 1m |

## Goal

Verify worker prompt and dashboard loop reliability improvements are consistent across all files.

## Verification Checklist

- [x] Worker prompts in `.claude/` include: incremental commits, error-exit, execution time guidance, heartbeat (3 files)
- [x] Worker prompts in `ai-team-library/claude/` include the same instructions (3 files)
- [x] Dashboard loop in `.claude/` includes automated stale recovery (10+ minutes, kill+cleanup)
- [x] Dashboard loop in `ai-team-library/claude/` mirrors local
- [x] No contradictions between SKILL.md and command .md versions
- [x] Spawn-bean status file protocol is consistent with worker instructions
- [x] Tests pass (`uv run pytest`) — 659 passed
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Acceptance Criteria

- [x] All verification items pass
- [x] Local and library templates are consistent

## Definition of Done

Full verification complete. Worker reliability instructions consistently documented across all template files.
