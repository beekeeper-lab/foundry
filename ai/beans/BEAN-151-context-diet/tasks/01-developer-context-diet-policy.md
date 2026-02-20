# Task 01: Document Context Diet Policy

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-17 04:08 |
| **Completed** | 2026-02-17 04:09 |
| **Duration** | 1m |

## Goal

Add a "Context Diet" policy document and integrate references to it in the spawn-bean worker prompts and the bean workflow. The policy establishes guidelines for minimizing unnecessary context consumption during bean execution.

## Inputs

- `ai/context/bean-workflow.md` — current workflow (add context diet section)
- `.claude/commands/internal/spawn-bean.md` — worker prompt templates (add context diet reference)

## Acceptance Criteria

- [ ] Context diet policy section added to `ai/context/bean-workflow.md`
- [ ] Guidelines distinguish essential vs. optional context per task type (App, Process, Infra)
- [ ] Worker prompts in spawn-bean reference the context diet
- [ ] Policy is concise (fits in one markdown section) and actionable

## Definition of Done

- Context diet policy is documented in `ai/context/bean-workflow.md`
- Spawn-bean worker prompts include a context diet instruction
- No contradictions with existing workflow documentation
