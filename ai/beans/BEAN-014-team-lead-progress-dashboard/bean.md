# BEAN-014: Team Lead Progress Dashboard

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-014 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

When the team lead processes a bean (especially during `/long-run` or parallel `--fast N` via tmux), the user has no structured way to see what's happening at a glance. Output is a wall of verbose narration — useful for debugging but terrible for monitoring. In a tmux setup with multiple windows, the user needs to glance at a pane and instantly know: which bean, which task, what status. Today that requires reading through pages of chatter.

## Goal

Define and enforce a structured communication template that every team lead session uses. The template puts a **bean header** and **live task-progress table** at the top of output, keeps verbose work chatter below, and ends with a clean completion summary for the merge captain handoff. The result: any tmux pane is instantly scannable.

## Scope

### In Scope
- Define the three-section communication template (Header, Task Table, Work Log)
- Embed the template into the team lead agent instructions (`.claude/agents/team-lead.md`)
- Update the long-run skill (`SKILL.md`) to reference the template at announcement and progress-report steps
- Specify re-presentation rules (when to re-print the header + table)
- Specify output ordering: header and table at top, work narration below, questions/prompts at bottom
- Define the completion summary format for merge captain handoff

### Out of Scope
- Changes to individual persona agents (BA, Architect, Developer, Tech-QA) — they keep their current output style
- Terminal UI / TUI rendering (this is plain markdown output, not a curses dashboard)
- Changes to the tmux spawning logic in parallel mode
- Changes to bean.md schema or task file format

## Acceptance Criteria

- [ ] Team lead agent (`.claude/agents/team-lead.md`) contains the full communication template specification
- [ ] Template defines a **Header Block**: bean ID, title, and 1-2 sentence summary — printed once at bean start and re-printed on every table update
- [ ] Template defines a **Task Progress Table** with columns: #, Task, Owner, Status, Parallel — re-printed whenever any task status changes
- [ ] Template specifies output ordering: header + table at top, work narration scrolls below, interactive prompts (questions to user) appear at bottom
- [ ] Template defines a **Completion Summary**: conversational recap of work done, decisions made, and handoff notes for merge captain
- [ ] Long-run skill (`SKILL.md`) references the template at "Announce selection" (Phase 2 step 6) and "Report progress" (Phase 5.5 step 18)
- [ ] The team lead is instructed to suppress or minimize verbose per-task narration in favor of the structured table
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design the communication template (header, table, work log, completion summary formats) | team-lead | — | Done |
| 2 | Update team-lead agent with template spec and output-ordering rules | developer | 1 | Done |
| 3 | Update long-run SKILL.md to reference template at announcement and progress steps | developer | 1 | Done |
| 4 | Verify template renders correctly in a simulated bean walkthrough | tech-qa | 2, 3 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- This bean modifies agent instructions and skill docs only — no Python code changes expected, so tests/lint criteria are a pass-through verification.
- The template should work well in both sequential and parallel (`--fast N`) tmux modes.
- Key design constraint: tmux panes may be narrow. The table should be readable at ~100 columns.
- The header + table should be the first thing visible when you glance at a tmux pane. Think of it like a process monitor — the "top" of `htop`, not a log file.
