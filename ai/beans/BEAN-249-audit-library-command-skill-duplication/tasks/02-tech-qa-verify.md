# BEAN-249 / Task 02: Verify Audit and Trim

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01-developer-audit-and-trim |
| **Status** | Done |
| **Started** | 2026-04-30 09:07 |
| **Completed** | 2026-04-30 09:09 |
| **Duration** | 2m |

## Goal

Independently verify that every acceptance criterion in BEAN-249 holds
after the developer's audit and trim pass.

## Inputs

- ai/beans/BEAN-249-audit-library-command-skill-duplication/bean.md — acceptance criteria
- ai/outputs/team-lead/bean-249-command-skill-audit.md — audit table (developer output)
- ai-team-library/claude/commands/ — all trimmed command files
- ai-team-library/claude/skills/ — paired skills (verify any migrated content landed here)
- examples/small-python-team.yml — composition used in smoke generation

## Acceptance Criteria

- [ ] Run: every command file is ≤30 lines.
      `awk 'END{print FILENAME, NR}' ai-team-library/claude/commands/*.md`
      (or equivalent) — verify no file exceeds 30.
- [ ] Run: no command file contains forbidden sections.
      `grep -lE '^## (Process|Error Conditions|Quality Criteria)$' ai-team-library/claude/commands/*.md`
      should return nothing.
- [ ] Audit table at `ai/outputs/team-lead/bean-249-command-skill-audit.md` exists
      and has one row per command. Verify the row count matches the count of
      command files.
- [ ] Run: `uv run foundry-cli generate examples/small-python-team.yml
      --library ai-team-library --output /tmp/bean-249-tech-qa-smoke`
      and confirm the generated `commands/` directory contains all expected files.
- [ ] Run: `uv run pytest` — all tests pass.
- [ ] Run: `uv run ruff check foundry_app/` — lint clean.
- [ ] Spot-check 3 trimmed commands at random: confirm they retain title,
      one-sentence description, usage, argument list (if applicable), and a
      pointer to the paired skill.

## Definition of Done

- All checks PASS. If any check fails, hand back to developer with the
  specific failure recorded in this file.
