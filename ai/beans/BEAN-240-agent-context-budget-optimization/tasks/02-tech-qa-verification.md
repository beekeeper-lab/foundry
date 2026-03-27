# Task 02: Tech-QA Verification

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-03-27 11:45 |
| **Completed** | 2026-03-27 11:45 |
| **Duration** | < 1m |

## Goal

Verify context budget guidance is complete, consistent, and actionable.

## Inputs

- Task 01 changes to agent files, bean-workflow.md, and long-run skill
- Bean acceptance criteria

## Verification Plan

1. **Review context budget sections** — Verify guidelines are specific and actionable
2. **Cross-check consistency** — Ensure agent files and bean-workflow align
3. **Test execution** — Run `uv run pytest` and `uv run ruff check foundry_app/`
4. **AC check** — Verify all acceptance criteria

## Acceptance Criteria

- [ ] Code review passes
- [ ] All tests pass
- [ ] Lint clean
- [ ] All bean AC verified

## Definition of Done

- Review complete, tests pass, lint clean
