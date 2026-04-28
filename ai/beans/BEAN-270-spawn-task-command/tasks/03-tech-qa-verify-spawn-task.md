# Task 03: Verify BEAN-270 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 02 |
| **Status** | Done |
| **Started** | 2026-04-28 19:30 |
| **Completed** | 2026-04-28 19:31 |
| **Duration** | 1m |

## Goal

Independently verify every acceptance criterion in the bean and the two
upstream tasks. Produce a verification report at
`ai/outputs/tech-qa/bean-270-verification.md` listing each criterion, the
evidence (file path, line range, command output excerpt), and a PASS/FAIL
decision. Stop the bean if any criterion fails.

For criteria that require a manual interactive test (the actual tmux spawn
flow), document them as **MANUAL — pending user verification** with clear
reproduction steps. Do not pretend autonomous verification covers them.

## Inputs

- `ai/beans/BEAN-270-spawn-task-command/bean.md`
- `ai/beans/BEAN-270-spawn-task-command/tasks/01-architect-spawn-task-adr.md`
- `ai/beans/BEAN-270-spawn-task-command/tasks/02-developer-spawn-task-implementation.md`
- `ai/context/decisions.md` — the ADR
- `ai-team-library/claude/skills/spawn-task/SKILL.md`
- `ai-team-library/claude/commands/spawn-task.md`
- `.claude/skills/spawn-task/SKILL.md`
- `.claude/commands/spawn-task.md`
- `ai-team-library/personas/team-lead/persona.md`
- `.claude/agents/team-lead.md`
- `ai-team-library/claude/skills/long-run/SKILL.md`
- `.claude/skills/long-run/SKILL.md`

## Acceptance Criteria

- [ ] Verification report exists at `ai/outputs/tech-qa/bean-270-verification.md`.
- [ ] Each bean acceptance criterion (8 criteria) has a row with PASS / FAIL / MANUAL.
- [ ] ADR check: `ai/context/decisions.md` contains the BEAN-270 ADR with
      all three decision points (detection rule, prompt schema, banner
      heuristic) explicitly addressed.
- [ ] Library command file is ≤ 30 lines (`wc -l`).
- [ ] Library command file does NOT contain `## Process` or `## Error
      Conditions` headings (`grep -E '^## (Process|Error Conditions)'`
      returns nothing).
- [ ] Library skill file does contain `## Process` and at least one
      `## Acceptance Criteria` or equivalent quality gate section.
- [ ] Both Team-Lead persona docs reference `/spawn-task`.
- [ ] Both `/long-run` skills reference `/spawn-task`.
- [ ] `uv run pytest` passes — captured tail output in the report.
- [ ] `uv run ruff check foundry_app/` passes — captured output in the report.

## Definition of Done

- Verification report committed.
- All non-manual criteria verified PASS, or the report flags failures and
  the bean stops.
- Manual criteria are clearly enumerated with reproduction steps for the
  user to exercise.
