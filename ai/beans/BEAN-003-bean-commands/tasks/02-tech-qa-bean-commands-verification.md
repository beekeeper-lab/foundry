# Task 02: Bean Commands Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Verify that all bean management commands and skills are complete, correctly formatted, and consistent with existing commands/skills.

## Inputs

- `ai/beans/BEAN-003-bean-commands/bean.md` — acceptance criteria
- `.claude/commands/new-bean.md`, `pick-bean.md`, `bean-status.md` — new commands
- `.claude/skills/new-bean/`, `pick-bean/`, `bean-status/` — new skills
- `.claude/commands/new-work.md` — reference format

## Acceptance Criteria

- [ ] All 6 files exist and are non-empty
- [ ] Command format matches existing commands (sections, tables, examples)
- [ ] Skill format matches existing skills (sections, tables, process steps)
- [ ] `/new-bean` correctly references the bean template and index
- [ ] `/pick-bean` correctly describes status transitions
- [ ] `/bean-status` correctly describes backlog summary output
- [ ] `uv run pytest` — all tests pass
- [ ] QA report written to `ai/outputs/tech-qa/bean-003-bean-commands-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation.
