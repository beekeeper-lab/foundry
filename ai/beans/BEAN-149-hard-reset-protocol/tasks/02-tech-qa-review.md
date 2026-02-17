# Task 02: Review Hard Reset Protocol

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | Task 01 |
| **Status** | Done |
| **Started** | 2026-02-17 04:09 |
| **Completed** | 2026-02-17 04:09 |
| **Duration** | < 1m |

## Goal

Verify the hard reset protocol document is clear, complete, and covers all common failure states.

## Inputs

- `ai/context/hard-reset-protocol.md` — the protocol document from Task 01
- `ai/beans/BEAN-149-hard-reset-protocol/bean.md` — acceptance criteria
- `ai/context/bean-workflow.md` — bean lifecycle reference

## Definition of Done

- [ ] All five failure states are covered (stalled workers, merge conflicts, corrupted worktrees, broken branches, stuck status files)
- [ ] Each recovery procedure is step-by-step and unambiguous
- [ ] Pre/post verification checklists are present and complete
- [ ] No contradictions with existing policies (git-policy.md, safety-policy.md)
- [ ] Instructions are actionable — a new team member could follow them without prior context
