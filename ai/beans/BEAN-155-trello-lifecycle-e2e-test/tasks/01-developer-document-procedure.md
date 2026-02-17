# Task 01: Document Trello Lifecycle Test Procedure

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-17 05:11 |
| **Completed** | 2026-02-17 05:12 |
| **Duration** | 1m |
| **Tokens** | — |

## Goal

Document the expected Trello card state transitions at each bean lifecycle stage and write a step-by-step test procedure.

## Inputs

- `ai/context/bean-workflow.md` — Bean lifecycle specification
- `.claude/skills/long-run/SKILL.md` — Long-run skill (Trello sync steps)
- `.claude/commands/internal/trello-load.md` — Trello import command
- BEAN-154 execution log — Real example of the lifecycle in action

## Definition of Done

- [ ] Test procedure document created at `ai/outputs/developer/trello-lifecycle-test-procedure.md`
- [ ] Expected Trello card states defined for each lifecycle stage
- [ ] Procedure covers import, in-progress, and completion transitions
- [ ] Gaps between expected and actual behavior identified (if any)
