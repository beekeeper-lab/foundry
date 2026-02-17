# Task 01: Write Hard Reset Protocol Document

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-17 04:08 |
| **Completed** | 2026-02-17 04:09 |
| **Duration** | 1m |

## Goal

Create `ai/context/hard-reset-protocol.md` — a concise, actionable document covering recovery procedures for common failure states during bean execution.

## Inputs

- `ai/context/bean-workflow.md` — bean lifecycle and branch strategy
- `ai/context/git-policy.md` — git safety guardrails
- `ai/context/safety-policy.md` — safety posture and blocked operations
- `ai/beans/BEAN-149-hard-reset-protocol/bean.md` — acceptance criteria

## Definition of Done

- [ ] `ai/context/hard-reset-protocol.md` exists
- [ ] Covers recovery for: stalled workers, merge conflicts, corrupted worktrees, broken branches, stuck status files
- [ ] Each failure state has step-by-step recovery instructions
- [ ] Pre-reset verification checklist included
- [ ] Post-reset verification checklist included
- [ ] Document is concise and actionable (not verbose)
