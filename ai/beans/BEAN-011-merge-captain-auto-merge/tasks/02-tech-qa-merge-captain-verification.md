# Task 02: Merge Captain Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Verify the Merge Captain wiring is complete, consistent, and well-documented.

## Inputs

- `ai/beans/BEAN-011-merge-captain-auto-merge/bean.md` — acceptance criteria
- `.claude/commands/merge-bean.md` — new command
- `.claude/skills/merge-bean/SKILL.md` — new skill
- `.claude/skills/long-run/SKILL.md` — updated skill
- `.claude/agents/team-lead.md` — updated agent

## Acceptance Criteria

- [ ] All bean acceptance criteria traced and met
- [ ] Safe merge sequence is complete and correct
- [ ] Conflict handling is clear (report, don't auto-resolve)
- [ ] Sequential and parallel modes both reference Merge Captain
- [ ] No contradictions with existing `/long-run` flow
- [ ] QA report written to `ai/outputs/tech-qa/bean-011-merge-captain-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation.
