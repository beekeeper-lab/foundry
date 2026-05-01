# Task 01: ADR — `/spawn-task` Dispatch Mechanism

| Field | Value |
|-------|-------|
| **Owner** | Architect |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-28 17:58 |
| **Completed** | 2026-04-28 17:59 |
| **Duration** | 1m |

## Goal

Document the architectural decision for `/spawn-task`'s dispatch mechanism in
`ai/context/decisions.md`. The ADR fixes the contract that the implementing
task (Task 02) must follow.

The decision needs to nail three things:

1. **Runtime detection rule** — `[ -n "$TMUX" ]` to choose between in-process
   `Agent` tool dispatch (no tmux) and tmux-spawn-in-worktree dispatch (in
   tmux). Why this rule, what its failure modes are, and what fallback to use
   if the detection is ambiguous.
2. **Agent-tool prompt schema** — what the orchestrator passes to the
   `Agent` tool (subagent_type = persona, prompt content = task file path
   + task body + persona context bundle pointer + completion contract). The
   ADR specifies the prompt's required sections so callers and reviewers can
   audit whether dispatch is correct.
3. **Reminder-banner heuristic** — when `/spawn-task` runs *not* in tmux, it
   emits a one-line "consider tmux + `/long-run --fast`" reminder if either:
   the task is `priority: high`, OR the bean has ≥4 remaining unfinished
   tasks. The ADR records the threshold and the rationale.

## Inputs

- `ai/beans/BEAN-270-spawn-task-command/bean.md` — full requirements
- `ai/context/decisions.md` — ADR registry (append to it)
- `ai-team-library/claude/commands/spawn-bean.md` — pattern reference for tmux dispatch
- `.claude/skills/long-run/SKILL.md` — pattern reference for parallel-mode worker spawning

## Acceptance Criteria

- [ ] A new ADR section in `ai/context/decisions.md` titled
      `BEAN-270 — /spawn-task Dispatch Mechanism` (or equivalent), dated
      2026-04-28.
- [ ] ADR covers the three decision points above (detection rule, prompt
      schema, reminder heuristic).
- [ ] ADR names what is intentionally **out of scope** (no agent retry
      logic, no cross-task state, no replacement for `/spawn-bean`).
- [ ] ADR is concise — ≤ ~60 lines of body content.

## Definition of Done

- ADR appended to `ai/context/decisions.md`.
- The ADR is concrete enough that Task 02 can implement against it without
  re-deciding any of the three points.
