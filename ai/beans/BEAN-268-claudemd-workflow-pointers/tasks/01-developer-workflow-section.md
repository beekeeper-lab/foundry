# BEAN-268 / Task 01: Add Workflow Section to Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-30 09:41 |
| **Completed** | 2026-04-30 09:41 |
| **Duration** | < 1m |

## Goal

Emit a small `## Workflow` section in the generated `CLAUDE.md` that
names the bean workflow and the top 5-7 day-1 slash commands. Section
must be ≤25 lines.

## Inputs

- ai/beans/BEAN-268-claudemd-workflow-pointers/bean.md — full scope and acceptance criteria
- foundry_app/services/compiler.py — `_build_lean_claude_md` (line 450); the section goes between `## Team Orchestration Model` (line 580) and `## Documentation` (line 599)
- ai-team-library/claude/commands/ — list of commands that ship by default (use `long-run`, `show-backlog`, `pick-bean`, `new-bean`, `spawn-task`, `review-beans` as the day-1 pointer set)
- tests/test_compiler.py — TestLeanClaudeMd class around line 1260; add new tests there

## Acceptance Criteria

- [ ] `_build_lean_claude_md` emits a `## Workflow` section after `## Team Orchestration Model` and before `## Documentation`.
- [ ] The section names the bean workflow, points at `ai/beans/_index.md`, and lists 5-7 default slash commands with one-line descriptions.
- [ ] Section is ≤25 lines (counted between the heading and the next `##` heading, exclusive).
- [ ] An agent reading only CLAUDE.md can discover `/long-run` and `/show-backlog` from this section without needing external context.
- [ ] New test asserts the section exists, contains the named commands, and is ≤25 lines.
- [ ] No existing tests broken.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Definition of Done

- Section emitted, tests added, full suite + lint pass.
