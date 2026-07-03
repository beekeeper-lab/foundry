# ADR-008: `/spawn-task` Per-Task Dispatch Mechanism

| Field | Value |
|-------|-------|
| **Date** | 2026-04-28 |
| **Status** | Accepted |
| **Bean** | BEAN-270 |
| **Deciders** | Architect |

> **Practice note (2026-07 audit, SPEC-029):** the tmux-worker dispatch path this ADR specifies was never exercised — every bean that recorded a dispatch mode used in-process execution. SPEC-010 proposes rebuilding dispatch on the native Claude Code task system; until that lands, treat the tmux path as unvalidated design.

## Context

Today, "delegation" inside a bean is convention only: the Team-Lead writes
task files to `tasks/NN-<owner>-<slug>.md`, and the same Claude session
plays Developer, then plays Tech-QA. There is no `Agent` tool boundary
between roles. The orchestrator supervises itself, and role baggage,
prior-task context, and unrelated reads accumulate in one window. The
Anthropic supervisor pattern's main benefit — context isolation per
specialist — is forfeited.

`/spawn-bean` already exists, but it dispatches Team-Lead for a *full bean
lifecycle*. There is no command that dispatches a single specialist for a
single task. This ADR fixes the contract for that command — `/spawn-task`
— so the Implementing task (BEAN-270 task 02) can build against a stable
spec.

The decision must answer three questions: (1) how does `/spawn-task` choose
between two execution paths, (2) what does it pass to the chosen path, and
(3) when should it warn the user that they should be using a stronger form
of dispatch.

## Decision

**1. Runtime detection rule.** `/spawn-task` chooses its execution path
from a single environment check:

```
[ -n "$TMUX" ]
```

When `$TMUX` is non-empty, the command runs the **tmux path**: create a
git worktree on the task's bean branch, write a status file at
`/tmp/agentic-task-BEAN-NNN-<task-slug>.status`, open a child tmux window
named `task-NNN-<slug>`, and launch a `claude --dangerously-skip-permissions`
process whose positional argument is the task prompt. This mirrors the
`/spawn-bean` pattern and inherits its watchdog/auto-close behavior.

When `$TMUX` is empty, the command runs the **Agent-tool path**: the
calling Claude session emits a single `Agent(subagent_type=<persona>,
description=..., prompt=<task prompt>)` call. The subagent gets a fresh
context, returns one summary message, and the calling session captures
that summary into the task's Telemetry row. No tmux, no worktree, no
status file.

The detection rule is intentionally one-shot. There is no
`--force-tmux` / `--force-agent` flag. If the user wants the other path,
they enter or exit tmux. Two flags would invite "wrong path because I
forgot the flag" failures; one rule produces deterministic dispatch.

**2. Agent-tool prompt schema.** Whichever path runs, the prompt has the
same five required sections, in this order:

| Section | Content |
|---------|---------|
| **Role** | One line: `You are the <persona> persona. Your job: <one-sentence task goal>.` |
| **Task file** | Absolute path to the task's `NN-<owner>-<slug>.md` file. Worker reads this first. |
| **Inputs** | Verbatim the task's `Inputs:` list (paths, anchors). The worker reads only these. |
| **Acceptance** | Verbatim the task's `Acceptance Criteria` block. |
| **Completion contract** | Three sentences max: (a) flip task Status to `Done` when criteria met, (b) commit on the current branch, (c) exit. |

The persona's own context bundle (`ai-team-library/personas/<persona>/persona.md`)
is referenced by name, not inlined — the worker reads it once on startup.
This keeps the prompt small (no copy-pasted persona body) and lets persona
edits propagate without re-issuing in-flight prompts.

The schema is identical for both paths so reviewers and tooling can audit
dispatch correctness from one rubric, regardless of execution mode.

**3. Reminder-banner heuristic.** When `/spawn-task` runs in the
Agent-tool path (i.e., not in tmux), it prints a one-line reminder iff
either condition holds:

- The task's metadata table has `priority: high` (case-insensitive).
- The task's bean has **≥4 remaining tasks** with status not in `{Done, Skipped}`.

The reminder reads:

```
Tip: tmux + /long-run --fast gives this task an isolated worker context. Consider relaunching there for high-priority or multi-task work.
```

Below either threshold, no banner is emitted — the Agent-tool path is the
right tool for one-off small dispatches and the warning would be noise.
The threshold is intentionally additive (either trigger fires it) and
intentionally generous on the bean side: 4 remaining tasks is the rough
breakpoint where in-process role-switching starts mixing meaningfully
unrelated context for the calling session.

## Out of Scope

- **No agent retry logic.** If the Agent-tool path returns failure, the
  caller (Team-Lead) decides what to do. `/spawn-task` does not loop.
- **No cross-task state.** Each `/spawn-task` invocation is independent.
  Tasks coordinate through committed files, not through `/spawn-task` itself.
- **No replacement for `/spawn-bean`.** `/spawn-bean` keeps its place for
  bean-level dispatch. `/spawn-task` is strictly for individual tasks
  inside an already-claimed bean.
- **No `Inputs:` validation.** That is BEAN-272's responsibility — a
  separate hook integrated into the dispatch path. `/spawn-task` calls
  the validator if it exists; absence is not an error in this bean.
- **No `produces:`/`consumes:` enforcement.** That is BEAN-273's. When
  it lands, it adds a "consumed types as required reading" line under
  the prompt's Inputs section.

## Consequences

**Positive:**

- The supervisor pattern becomes structural rather than aspirational: one
  command produces real isolation (tmux process or fresh subagent context)
  per task.
- Identical prompt schema across paths eliminates dispatch-correctness
  drift. A reviewer can audit one rubric.
- The detection rule is one line of bash and one line of docs. No flag
  surface to keep coherent.

**Negative:**

- Detection is binary — there is no in-between for users who run inside
  `screen`/`zellij`/etc. The reminder banner partially mitigates by
  surfacing the recommended setup; affected users can opt into tmux.
- Two execution paths means two test surfaces. The verification task
  (BEAN-270 task 03) flags the in-tmux path as a manual test until a
  durable harness exists.

## Alternatives Rejected

1. **Single execution path via Agent tool only.** Rejected. The
   Agent-tool path is in-process: subagents share the calling session's
   process and quota. Long-running parallel work (`/long-run --fast N`)
   needs OS-level isolation, which only the tmux path provides.
2. **Single execution path via tmux only.** Rejected. Tmux is a
   prerequisite many invocations don't have (one-off task dispatch from
   an IDE-embedded Claude). Forcing tmux for every dispatch raises the
   activation cost for the simple case.
3. **`--mode=tmux|agent` flag instead of `$TMUX` detection.** Rejected.
   A flag commits the user to remembering it; `$TMUX` is observable
   ground truth and matches "the runtime you are actually in."
4. **Inlined persona context in the prompt.** Rejected. Inlining bloats
   every prompt and stales when the persona file changes. Reference by
   path lets each spawn read the current source.
5. **Always emit the reminder banner outside tmux.** Rejected. For a
   one-task one-bean dispatch, the Agent-tool path is exactly right; a
   blanket reminder trains users to ignore it.

## Reversibility

The schema (sections + order) is the load-bearing piece. Adding sections
later (e.g., a `Consumes:` line when BEAN-273 lands) is additive and
backwards-compatible — workers tolerate trailing content. Reordering or
renaming existing sections would invalidate every cached worker prompt
template; that is the only edit that requires a follow-up bean.

