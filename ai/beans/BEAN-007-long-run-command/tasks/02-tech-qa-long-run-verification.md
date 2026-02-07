# Task 02: Long Run Command Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Verify that the `/long-run` command and skill are complete, correctly formatted, and consistent with existing commands/skills.

## Inputs

- `ai/beans/BEAN-007-long-run-command/bean.md` — acceptance criteria
- `.claude/commands/long-run.md` — new command
- `.claude/skills/long-run/SKILL.md` — new skill
- `.claude/agents/team-lead.md` — updated agent
- `.claude/commands/pick-bean.md` — reference format
- `.claude/skills/pick-bean/SKILL.md` — reference format

## Acceptance Criteria

- [ ] All files exist and are non-empty
- [ ] Command format matches existing commands (sections, tables, examples)
- [ ] Skill format matches existing skills (sections, tables, process steps)
- [ ] Bean selection heuristics cover priority, dependencies, logical order
- [ ] Full lifecycle is documented (pick → decompose → wave → verify → close → commit → loop)
- [ ] Stop condition is clear
- [ ] Team Lead agent references `/long-run`
- [ ] QA report written to `ai/outputs/tech-qa/bean-007-long-run-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation.
