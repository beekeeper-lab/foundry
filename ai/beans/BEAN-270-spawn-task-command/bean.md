# BEAN-270: `/spawn-task` Persona-Scoped Delegation Command

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-270 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-28 |
| **Started** | 2026-04-28 17:56 |
| **Completed** | 2026-04-28 19:32 |
| **Duration** | 1h 36m (corrected 2026-07) |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

Today, "delegation" inside a bean is just writing task files (`tasks/NN-<owner>-<slug>.md`) — the same Claude session then plays Developer, then plays Tech-QA. There is no `Agent`/`Task` tool call between roles. The supervisor is supervising itself in a single context window, accumulating role baggage and losing the isolation benefit of the Anthropic supervisor pattern.

`/spawn-bean` exists, but always spawns Team-Lead for a *full bean lifecycle* (`ai-team-library/claude/commands/spawn-bean.md:8-9, 125, 165-193`). There is no way to dispatch a single specialist for a single task with only that task's context.

This is the highest-leverage gap from the architectural review: without true per-task delegation, the supervisor pattern is convention only.

## Goal

A new `/spawn-task` command lets the Team-Lead dispatch a focused specialist worker for a single task. The command auto-detects the runtime environment:

- **In tmux**: spawn a tmux worker in a git worktree (process-isolated, parallelizable, like `/spawn-bean` does today).
- **Not in tmux**: invoke the `Agent` tool with `subagent_type=<persona>` (in-process subagent, fresh context, single Claude session orchestrates).

Either way, the worker receives only the task's `Inputs:` files plus the persona's own context bundle — not the full bean folder, not the orchestrator's transcript.

## Scope

### In Scope

- New library skill at `ai-team-library/claude/skills/spawn-task/SKILL.md` — the canonical execution spec. Per BEAN-249's rule, this holds the full process; the command is a thin trigger.
- New library command at `ai-team-library/claude/commands/spawn-task.md` (≤30 lines) that names the skill.
- Same pair added to `.claude/skills/spawn-task/` and `.claude/commands/spawn-task.md` for Foundry's own team via the kit sync.
- Behavior:
  - `/spawn-task <persona> <task-file-path>` — explicit form
  - `/spawn-task <task-file-path>` — infer persona from `Owner:` field
- tmux detection via `[ -n "$TMUX" ]` (presence of `TMUX` env var).
- tmux mode: reuse the spawn pattern from `/spawn-bean` (worktree from `test`, watchdog, status file at `/tmp/agentic-task-<bean>-<task>.status`).
- Agent-tool mode: emit a single `Agent(subagent_type=..., prompt=<task-context>)` call and capture the result in the task file's Telemetry row.
- Reminder banner: when `/spawn-task` runs *not* in tmux for a task tagged `priority: high` or in a bean with ≥4 remaining tasks, emit a one-line reminder that tmux + `/long-run --fast` is recommended for larger bodies of work.
- Update `ai-team-library/personas/team-lead/persona.md` and the Foundry `.claude/agents/team-lead.md` to reference `/spawn-task` as the preferred per-task dispatch mechanism.
- Update `/long-run` skill to use `/spawn-task` for individual task execution where appropriate (do not rip out current behavior — additive integration; keep the existing in-process role-switching as a fallback for tiny tasks).

### Out of Scope

- Removing `/spawn-bean` (it remains the right tool for bean-level dispatch).
- Changing the wave model itself.
- Persona-to-persona handoff format (BEAN-276).
- Task `Inputs:` validation (BEAN-272).

## Acceptance Criteria

- [ ] `ai-team-library/claude/skills/spawn-task/SKILL.md` exists with: usage, tmux-detection logic, both execution paths, telemetry capture, error conditions.
- [ ] `ai-team-library/claude/commands/spawn-task.md` exists, ≤30 lines, points to the skill.
- [ ] Foundry's own `.claude/skills/spawn-task/` and `.claude/commands/spawn-task.md` are populated via the kit sync.
- [ ] Manual test (in tmux): `/spawn-task developer ai/beans/BEAN-XXX/tasks/01-developer-foo.md` spawns a tmux window, executes the task, updates the status file, and the task file's Status flips to `Done`.
- [ ] Manual test (not in tmux): same command issues an `Agent` tool call and the task file's Status flips to `Done` after the subagent returns.
- [ ] When invoked outside tmux for a high-priority task, the reminder banner appears once.
- [ ] Team-Lead persona files (library + project) name `/spawn-task` as the preferred per-task dispatch mechanism.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | ADR — `/spawn-task` dispatch mechanism | Architect | — | Done |
| 02 | Implement skill, command, persona wiring | Developer | 01 | Done |
| 03 | Verify acceptance criteria | Tech-QA | 02 | Done |

> Skipped: BA (default — requirements are concrete and unambiguous).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Highest-leverage bean in the cluster.** The supervisor pattern is the architectural change with the largest payoff; everything else compounds from this.

**Architect required.** The dispatch mechanism deserves an ADR — it changes how every future bean executes. Document the tmux-detection rule, the Agent-tool prompt schema, and the reminder-banner heuristic in `ai/context/decisions.md`.

**Coordinate with BEAN-272.** A spawned task should fail fast if `Inputs:` is empty — this enforces context engineering at dispatch time.

**Coordinate with BEAN-273.** When BEAN-273 adds produces/consumes contracts, the spawn-task prompt should include the consumes-list as required reading.

**Per BEAN-249**: command file ≤30 lines, skill file is canonical. New code in this bean must conform.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 01 | ADR — `/spawn-task` dispatch mechanism | Architect | — | — | — | — |
| 02 | Implement skill, command, persona wiring | Developer | — | — | — | — |
| 03 | Verify acceptance criteria | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 1534h 24m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |