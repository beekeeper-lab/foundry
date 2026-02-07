# Task 01: Create Bean Management Commands and Skills

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Create `/new-bean`, `/pick-bean`, and `/bean-status` commands with corresponding skills. Commands go in `.claude/commands/`, skills in `.claude/skills/`. Follow the existing command/skill format.

## Inputs

- `ai/beans/BEAN-003-bean-commands/bean.md` — acceptance criteria
- `.claude/commands/new-work.md` — reference command format
- `.claude/skills/new-work/SKILL.md` — reference skill format
- `ai/beans/_bean-template.md` — template the `/new-bean` command should use
- `ai/beans/_index.md` — index the commands should update

## Acceptance Criteria

- [ ] `.claude/commands/new-bean.md` exists with full command spec
- [ ] `.claude/commands/pick-bean.md` exists with full command spec
- [ ] `.claude/commands/bean-status.md` exists with full command spec
- [ ] `.claude/skills/new-bean/SKILL.md` exists with implementation detail
- [ ] `.claude/skills/pick-bean/SKILL.md` exists with implementation detail
- [ ] `.claude/skills/bean-status/SKILL.md` exists with implementation detail
- [ ] Commands follow existing format (Purpose, Usage, Process, Output, Examples)
- [ ] Skills follow existing format (Description, Trigger, Inputs, Process, Outputs, Quality Criteria)
- [ ] `uv run pytest` — all tests still pass (no source changes)
- [ ] `uv run ruff check foundry_app/` — still clean

## Definition of Done

All 6 files created. Commands describe the user-facing interface. Skills describe the implementation steps. No Python source changes needed — these are prompt-based commands for Claude Code agents.
