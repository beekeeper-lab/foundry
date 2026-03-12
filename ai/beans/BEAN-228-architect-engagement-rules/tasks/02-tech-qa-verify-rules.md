# Task 02: Verify Architect Engagement Rules

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-02-23 20:06 |
| **Completed** | 2026-02-23 20:06 |
| **Duration** | < 1m |

## Goal

Verify that the new architect engagement rules are clear, actionable, consistent across all three files, and correctly address the user's concerns about the architect being underutilized.

## Inputs

- `.claude/agents/team-lead.md` — updated Participation Decisions section
- `.claude/agents/architect.md` — updated "When You Are Activated" section
- `ai/context/bean-workflow.md` — updated "Inclusion Criteria for Optional Personas" section
- `ai/beans/BEAN-228-architect-engagement-rules/bean.md` — acceptance criteria
- `ai/beans/BEAN-228-architect-engagement-rules/tasks/01-developer-architect-rules.md` — developer task

## Verification Checklist

- [ ] Rules are numbered and clearly defined
- [ ] Each rule can be evaluated with a yes/no answer (no ambiguity)
- [ ] Rules cover all scenarios from user's Trello card: refactoring, early setup, ADR creation
- [ ] Rules explicitly exclude trivial changes
- [ ] All three files have consistent rules (no contradictions)
- [ ] Rules lower the activation threshold vs. the previous criteria
- [ ] Cross-references between files are valid
- [ ] No formatting issues or broken markdown
- [ ] Rules are practical — applying them to past beans (e.g., BEAN-216 Rename Stack to Expertise) would correctly engage the architect

## Definition of Done

All verification checks pass. Any issues found are fixed or flagged. Rules are confirmed to be clear, actionable, and consistent.
