# Task 01: Create Long Run Command & Skill

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Create the `/long-run` command and skill files, and update the Team Lead agent to reference them.

## Inputs

- `ai/beans/BEAN-007-long-run-command/bean.md` — acceptance criteria and notes
- `ai/context/bean-workflow.md` — bean lifecycle reference
- `.claude/commands/pick-bean.md` — reference command format
- `.claude/skills/pick-bean/SKILL.md` — reference skill format
- `.claude/agents/team-lead.md` — agent to update

## Implementation

1. Create `.claude/commands/long-run.md` with all standard sections (Purpose, Usage, Inputs, Process, Output, Options, Error Handling, Examples)
2. Create `.claude/skills/long-run/SKILL.md` with all standard sections (Description, Trigger, Inputs, Process, Outputs, Quality Criteria, Error Conditions, Dependencies)
3. Update `.claude/agents/team-lead.md` to add `/long-run` to the Skills & Commands table

### Command/Skill Content

The `/long-run` process should define:
1. Read `_index.md` to find actionable beans (status `New` or `Picked`)
2. Select the best bean using heuristics: priority (High > Medium > Low), inter-bean dependencies, logical ordering, then ID order as tiebreaker
3. Pick the bean (update status to `In Progress`)
4. Decompose into tasks with the standard wave (BA → Architect → Developer → Tech-QA, skipping where appropriate)
5. Execute each task in dependency order
6. Verify acceptance criteria
7. Mark bean as `Done`, commit changes
8. Loop: check for next actionable bean, repeat or stop if backlog is empty

## Acceptance Criteria

- [ ] `.claude/commands/long-run.md` exists with all standard sections
- [ ] `.claude/skills/long-run/SKILL.md` exists with all standard sections
- [ ] Command format matches existing commands (9 sections)
- [ ] Skill format matches existing skills (8 sections)
- [ ] Bean selection heuristics are clearly documented
- [ ] Full bean lifecycle (pick → decompose → wave → verify → close → commit) is defined
- [ ] Stop condition documented (empty backlog or no actionable beans)
- [ ] Team Lead agent updated with `/long-run` in Skills & Commands table

## Definition of Done

All 3 files created/updated. Format matches existing commands and skills.
