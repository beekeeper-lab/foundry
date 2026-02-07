# Task 02: Feature Branch Workflow Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Verify that all feature branch workflow updates are complete, consistent, and match existing patterns.

## Inputs

- `ai/beans/BEAN-008-feature-branch-workflow/bean.md` — acceptance criteria
- `.claude/commands/pick-bean.md` — updated command
- `.claude/skills/pick-bean/SKILL.md` — updated skill
- `.claude/commands/long-run.md` — updated command
- `.claude/skills/long-run/SKILL.md` — updated skill
- `ai/context/bean-workflow.md` — updated workflow doc

## Acceptance Criteria

- [ ] All bean acceptance criteria traced and met
- [ ] Branch naming convention is consistent across all files
- [ ] No contradictions between command, skill, and workflow docs
- [ ] QA report written to `ai/outputs/tech-qa/bean-008-feature-branch-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation.
