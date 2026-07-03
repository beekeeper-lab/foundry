# ADR-017: Native Subagent Dispatch Replaces the tmux Worker Scheme

| Field | Value |
|-------|-------|
| **Date** | 2026-07-03 |
| **Status** | Accepted (supersedes ADR-008's tmux path) |
| **Bean** | SPEC-010 (2026-07 agentic excellence audit) |
| **Deciders** | Gregg (direction), Claude (analysis) |

## Context

ADR-008 specified per-task dispatch through a bespoke tmux + git-worktree +
`/tmp` status-file scheme, with the Agent tool as the non-tmux fallback. The
2026-07 audit found the tmux path was never exercised in practice (every
bean that recorded a dispatch mode used in-process execution), its status
files raced, and its launcher ran workers with
`--dangerously-skip-permissions` — defeating every safety hook the kit
installs. Meanwhile the Claude Code harness natively provides what the
scheme reimplemented: background subagent dispatch with completion
notifications, worktree isolation per agent, and inter-agent messaging.

## Decision

`/spawn-task` dispatches workers as **native background Agent calls**
(`subagent_type=<persona-leaf>`, resolving against the frontmattered
`.claude/agents/` files from SPEC-001), with **worktree isolation** for
parallel waves. Workers inherit the standard permission mode and hook
regime — no bypass flags, ever. In-process role-switching remains the
documented fallback for tiny tasks. Telemetry `Dispatch mode` values:
`agent-subagent`, `agent-worktree`, `in-process` (the `tmux-worker` value
is retired).

## Consequences

- Real parallelism becomes available without hand-rolled locking: a wave's
  independent tasks dispatch in one batch and run concurrently in isolated
  worktrees.
- The safety hole closes: workers can no longer bypass branch protection,
  the VDD gate, or the bash/write safety hooks.
- The `/tmp` status-file protocol, launcher scripts, and `$TMUX` detection
  are retired; `/spawn-task` shrinks to validate → prompt → dispatch →
  collect.
- ADR-008 remains as history; its supervisor-pattern rationale carries
  forward unchanged — only the transport changed.
