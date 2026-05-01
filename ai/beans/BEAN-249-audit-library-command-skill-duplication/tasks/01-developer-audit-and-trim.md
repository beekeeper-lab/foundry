# BEAN-249 / Task 01: Audit and Trim Library Commands

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-30 08:54 |
| **Completed** | 2026-04-30 09:07 |
| **Duration** | 13m |

## Goal

Audit every command/skill pair in `ai-team-library/claude/`, trim each
command to ≤30 lines (removing Process / Error / Quality sections that
duplicate the skill), and produce a single audit table that records the
before/after line counts and overlap notes.

## Inputs

- ai/beans/BEAN-249-audit-library-command-skill-duplication/bean.md — full scope and acceptance criteria
- ai-team-library/claude/commands/ — all command markdown files (33 files)
- ai-team-library/claude/skills/ — paired skill `SKILL.md` files
- ai-team-library/claude/commands/run.md — example of an already-short command (20 lines)
- ai-team-library/claude/commands/spawn-task.md — example of a short command (27 lines)
- ai-team-library/claude/commands/show-backlog.md — example of a moderately short command (45 lines)

## Acceptance Criteria

- [ ] Audit table written to `ai/outputs/team-lead/bean-249-command-skill-audit.md`
      with one row per command/skill pair: `command, paired skill, before-lines,
      after-lines, overlap notes, content migrated to skill (if any)`.
- [ ] Every `ai-team-library/claude/commands/*.md` is ≤30 lines.
- [ ] No command file contains "## Process" or "## Error Conditions" or "## Quality Criteria"
      sections — those live in skills only.
- [ ] Each trimmed command keeps: title, one-sentence description, usage block,
      argument list (if any), pointer to the skill file path.
- [ ] Any command-only content not present in the paired skill is migrated INTO
      the skill (not deleted) before trimming the command.
- [ ] Commands without a paired skill are flagged in the audit table; if a
      paired skill should exist, note it as a follow-up.
- [ ] `uv run foundry-cli generate examples/small-python-team.yml --library
      ai-team-library --output /tmp/bean-249-smoke` succeeds and the output
      directory contains the expected `commands/` files.

## Definition of Done

- All commands ≤30 lines, audit table complete, smoke generation passes,
  no command-only content lost (either preserved in command or migrated
  to skill).

## Notes

- The `dev-loop/` subdirectory under `commands/` may contain nested
  command files — include them in the audit if they exist.
- Don't touch the skills in this task. If a skill is missing detail
  that's currently in a command, add it to the skill before trimming.
- `long-run.md` (256 lines) and `spawn-bean.md` (342 lines) are the
  largest violators and deserve careful migration of any command-only
  detail into their paired skills.
