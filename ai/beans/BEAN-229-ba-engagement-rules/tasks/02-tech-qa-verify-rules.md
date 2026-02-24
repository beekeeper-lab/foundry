# Task 02: Verify BA Engagement Rules

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-02-23 20:54 |
| **Completed** | 2026-02-23 20:55 |
| **Duration** | 1m |

## Goal

Verify that the new BA engagement rules are clear, actionable, consistent across all three files, and correctly address the user's concerns about the BA being underutilized. Verify both the full-mode and partial-mode workflows are well-defined.

## Inputs

- `.claude/agents/team-lead.md` — updated Participation Decisions section
- `.claude/agents/ba.md` — updated "When You Are Activated" section
- `ai/context/bean-workflow.md` — updated BA mode flag and inclusion criteria
- `ai/beans/BEAN-229-ba-engagement-rules/bean.md` — acceptance criteria

## Verification Checklist

- [ ] BA Mode flag is defined with clear Full/Partial options and default specified
- [ ] Full mode workflow is complete: requirements register location, pre-bean steps, handoff format
- [ ] Partial mode rules are numbered and each is yes/no evaluable
- [ ] Partial mode covers: ambiguity, user-facing changes, documentation tasks, scope uncertainty
- [ ] Exclusion list is defined for partial mode
- [ ] All three files have consistent rules (no contradictions)
- [ ] Rules lower the BA activation threshold vs. previous criteria
- [ ] Cross-references between files are valid
- [ ] No formatting issues or broken markdown
- [ ] Retroactive validation: applying rules to past beans produces expected results
  - BEAN-036 (Update About Dialog Text): user-facing → BA WOULD be engaged (Rule 2). CORRECT.
  - BEAN-053 (P0 Bug Fixes): bug fix → BA NOT engaged. CORRECT.
  - BEAN-228 (Architect Engagement Rules): process definition → BA WOULD be engaged (Rule 4). Reasonable.

## Definition of Done

All verification checks pass. Any issues found are fixed or flagged. Both modes are confirmed well-defined and consistent.
