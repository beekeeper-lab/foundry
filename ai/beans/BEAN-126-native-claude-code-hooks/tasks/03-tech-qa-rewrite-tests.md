# Task 03: Rewrite Safety Writer Tests for Native Hook Format

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 02 |
| **Status** | Done |
| **Started** | 2026-02-16 00:05 |
| **Completed** | 2026-02-16 00:07 |
| **Duration** | 2m |

## Goal

Rewrite `tests/test_safety_writer.py` to verify the new native Claude Code hook format instead of the old custom safety model.

## Inputs

- `tests/test_safety_writer.py` — Current tests to rewrite
- `foundry_app/services/safety_writer.py` — Updated implementation from Task 02

## Approach

1. Rewrite test classes to verify `hooks` key instead of `safety` key
2. Test that PreToolUse/PostToolUse arrays contain correct entries for selected packs
3. Test that disabled packs produce no hooks
4. Test empty pack list produces empty hook arrays
5. Test posture-based defaults (baseline/hardened/regulated)
6. Keep edge case tests (existing dir, overwrites, pretty-print, newline)

## Acceptance Criteria

- [ ] All tests verify native hook format (`hooks.PreToolUse`/`hooks.PostToolUse`)
- [ ] Tests cover: packs selected, no packs, disabled packs, posture defaults
- [ ] Edge case tests preserved (directory creation, overwrite, formatting)
- [ ] All tests pass (`uv run pytest tests/test_safety_writer.py -v`)

## Definition of Done

Tests rewritten and all passing.
