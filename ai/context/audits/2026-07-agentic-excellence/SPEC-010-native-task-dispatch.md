# SPEC-010: Rebuild task dispatch on the native Claude Code task system

- **Priority:** P1
- **Effort:** L
- **Area:** process
- **Depends on:** SPEC-001 / SPEC-002 (agents need valid frontmatter before any `--agent` / subagent dispatch can resolve); SPEC-005 (telemetry must survive the dispatch change)
- **Status:** Proposed

## Problem

ADR-008's dispatch design — tmux windows + git worktrees + `/tmp` status files + hand-rolled markdown lock protocols — was built before the harness had native primitives for exactly this, and field data shows it was never actually used: every bean that records a dispatch mode records `in-process`; zero recorded `tmux-worker` or `mixed` runs. The supervisor pattern, the headline principle of the orchestration cluster, effectively doesn't run. Meanwhile Claude Code now provides native subagent dispatch (the Agent tool with typed subagents), background execution with completion notifications, task tracking (TaskCreate/TaskList/TaskUpdate), continuation of a running agent by ID, and worktree isolation as a dispatch option. The bespoke scheme is both unused and outclassed.

## Evidence

- `ai/context/decisions.md` ADR-008 (`:340` onward) — specifies the `/spawn-task` tmux+worktree+status-file scheme; `$TMUX` detection at `:379-391`.
- `.claude/local/commands/spawn-task.md:4` — "Auto-detects tmux and chooses between a tmux+worktree" path — the branch that field data shows never fires.
- Dispatch telemetry: 9/9 beans that record `Dispatch` record `in-process` (Orchestration Telemetry blocks, beans 278, 286–294); zero `tmux-worker`.
- `ai/context/bean-workflow.md:31-42` — hand-rolled multi-agent file-locking protocol (markdown lock lines), needed only because dispatch isn't isolation-aware.
- `ai-team-library/claude/skills/spawn-task/SKILL.md:107-122` — dispatch instructions invoke `claude --dangerously-skip-permissions --agent <persona>` and `Agent(subagent_type=<persona>)`; the former bypasses every safety hook the kit ships (a standing contradiction with the kit's own safety posture).

## Proposed change

1. **Make native subagent dispatch the primary path.** Rewrite `/spawn-task` (skill + local command) so a task is dispatched as a subagent invocation of the persona's registered agent (`.claude/agents/<persona>.md`, valid after SPEC-001/002), with the task file, bean id, and `Inputs:` list injected into the dispatch prompt. Remove the `--dangerously-skip-permissions` instruction entirely — subagents inherit the session's hook enforcement, which is the point.
2. **Parallel waves via isolation, not locks.** For waves the Team Lead marks parallel-safe, instruct dispatch with worktree isolation (the harness supports isolated-worktree agent runs; `EnterWorktree`-style flows also exist interactively). Each worker gets its own checkout; merge conflicts surface at integration instead of via the markdown lock protocol. Retire `bean-workflow.md:31-42` locking rules for dispatched work (keep a minimal rule for humans/in-process edits).
3. **Track with the native task list.** The Team Lead mirrors each dispatched task into the harness task tracker (create on dispatch, update on completion) so progress is observable without polling `/tmp` status files. The bean's task table in `bean.md` remains the durable record; the harness list is the live view. Delete the `/tmp/.foundry-spawn-*` status-file protocol.
4. **Continuation instead of re-spawn.** When a task bounces (QA rejects), the Team Lead re-engages the same worker agent with the rejection packet rather than spawning a fresh one, preserving worker context. Document this in the team-lead persona and spawn-task skill.
5. **Keep in-process as the explicit fallback**, not the silent default: `in-process` requires a one-line justification in the task file (mirroring the `Inputs: NONE` convention), so telemetry can distinguish choice from drift.
6. **Amend ADR-008** with a superseding ADR: tmux path retired (or demoted to "no-harness environments only"), native dispatch is the supervisor mechanism; record the safety rationale for dropping `--dangerously-skip-permissions`.
7. **Telemetry under native dispatch** (with SPEC-005): the Orchestration Telemetry block's `Dispatch` field gains values `subagent`, `subagent-worktree`, `in-process (justified)`; the telemetry hook keys checkpoints per bean/branch so parallel workers don't clobber each other.
8. **Generated projects get the same model**: the spawn-task skill ships via the kit, so this change propagates through both distribution modes (coordinate with SPEC-027).

## Out of scope

- Building any orchestration binary — this is skill/persona/process text plus deletions; the harness provides the machinery.
- Multi-bean parallelism policy (which beans may run concurrently) — separate process decision.
- The VDD/handoff gate enforcement (SPEC-008).

## Acceptance criteria

- [ ] (file-contains:.claude/local/commands/spawn-task.md::subagent) Spawn-task documents native dispatch as primary; no `--dangerously-skip-permissions` anywhere in it
- [ ] (file-contains:ai/context/decisions.md::ADR-016) Superseding/amending ADR recorded for ADR-008
- [ ] (file-contains:ai/context/bean-workflow.md::worktree) Locking protocol replaced by isolation guidance for dispatched work
- [ ] manual: Dispatch a real 2-task wave (Developer → Tech-QA) via the new path on a test bean; both tasks complete, telemetry records `subagent`, no status files under /tmp
- [ ] manual: A parallel-safe wave runs two workers in isolated worktrees concurrently and merges cleanly
- [ ] (file-contains:ai/beans/_bean-template.md::Dispatch) Telemetry block documents the new dispatch values

## Files to touch

- `ai-team-library/claude/skills/spawn-task/SKILL.md` (maintainer path), `.claude/local/commands/spawn-task.md`
- `ai-team-library/personas/core/team-lead/persona.md` (dispatch + continuation guidance)
- `ai/context/bean-workflow.md`, `ai/context/orchestration-architecture.md`, `ai/context/decisions.md`
- `ai/beans/_bean-template.md` (telemetry field values)
- `.claude/shared/hooks/telemetry-stamp.py` (dispatch values; per-bean checkpoint with SPEC-005)
