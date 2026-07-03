---
name: spawn-task
description: "Dispatches a single specialist persona to execute a single task with only that task's context, using native Claude Code subagent dispatch (background Agent call, optional worktree isolation for parallel waves). Supervisor pattern: the orchestrator never plays the role inline by default."
---

# Skill: spawn-task

## Description

Dispatch one task to one specialist persona as a **native Claude Code
subagent** (ADR-017, superseding ADR-008's tmux scheme). The worker gets a
fresh context containing only the task's `Inputs:` plus its persona
definition — the supervisor pattern's context-isolation guarantee — and
runs under the SAME permission and hook regime as the orchestrator. The
retired tmux path ran workers with `--dangerously-skip-permissions`,
which defeated every safety hook; native dispatch closes that hole.

## Trigger

Use when the Team Lead assigns a decomposed task from a bean's `tasks/`
directory. Not for bean bootstrap, backlog work, or multi-task batches —
one invocation per task.

## Inputs

| Input | Source | Required | Notes |
|-------|--------|----------|-------|
| task_file | `ai/beans/BEAN-NNN-<slug>/tasks/NN-<owner>-<slug>.md` | Yes | Must contain an `Inputs:` section (validate-task-inputs enforces at edit time). |
| persona | Task's `Owner` field | Yes | Any team persona: `.claude/agents/<leaf>.md` must exist (generated with frontmatter; SPEC-001). |
| parallel | Orchestrator judgment | No | When dispatching several tasks concurrently, use worktree isolation so workers don't collide on files. |

## Process

### Phase 1: Validate

1. **Read the task file.** Confirm `Status` is ready for execution and the
   `Inputs:` section exists (or carries a justified `NONE`).
2. **Resolve the persona.** The task's `Owner` maps to a generated agent at
   `.claude/agents/<leaf>.md` (leaf name, no `extended/` prefix). If the
   agent file is missing, fail loudly — do not improvise the role inline.
3. **Verify the bean branch** (`bean/BEAN-NNN-<slug>`) exists. `/spawn-task`
   is not a bean-bootstrap command.

### Phase 2: Build the worker prompt

Assemble ONLY (Context Diet, bean-workflow §6a):

- The task file's full contents (objective, inputs, acceptance criteria).
- The bean id, branch name, and the one-paragraph bean goal.
- The instruction block: work only from the listed Inputs; commit after
  completing the task; update the task file's Status and Telemetry row;
  emit a `/handoff` packet if the task's outputs feed another persona;
  report a structured summary (what changed, files touched, test results)
  as the final message.

Never include: the full backlog, other beans, other personas' files, or
the whole workflow spec.

### Phase 3: Dispatch (native)

4. **Single task:** issue one background `Agent` call with
   `subagent_type=<persona-leaf>` and the Phase-2 prompt. The orchestrator
   continues its own work and is notified when the worker finishes.
5. **Parallel wave:** dispatch each task the same way with **worktree
   isolation** so concurrent workers get their own checkout; merge results
   back through the normal branch flow. Dispatch independent tasks in one
   batch so they run concurrently.
6. **Tiny tasks** (single mechanical edit, dispatch overhead unjustified):
   in-process role-switching remains the documented fallback — record
   `Dispatch mode: in-process` in telemetry when used.

### Phase 4: Collect

7. When a worker completes, read its structured summary, verify the task
   file's Status/Telemetry were updated (telemetry-stamp fills gaps), and
   record the dispatch mode in the bean's Orchestration Telemetry:
   `agent-subagent`, `agent-worktree`, or `in-process`.
8. On worker failure or an unusable summary, re-dispatch once with the
   failure appended to the prompt; after a second failure, escalate to the
   user rather than silently absorbing the work inline.

## Outputs

| Output | Description |
|--------|-------------|
| Executed task | Task file Status updated by the worker; commits on the bean branch |
| Dispatch record | `Dispatch mode` value in the bean's Orchestration Telemetry |
| Worker summary | Structured final message captured by the orchestrator |

## Quality Criteria

- The worker prompt contains nothing outside the task's Inputs and the
  persona bundle (spot-check: no `_index.md`, no other beans).
- Workers run under the standard permission mode — NEVER pass
  `--dangerously-skip-permissions` or equivalent bypasses.
- Parallel waves use worktree isolation; two workers never edit the same
  checkout concurrently.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `AgentFileMissing` | Persona has no `.claude/agents/<leaf>.md` | Regenerate the project or add the persona to the composition |
| `InputsMissing` | Task lacks an `Inputs:` section | Fix the task spec (validate-task-inputs blocks the status transition anyway) |
| `BranchMissing` | Bean branch not created | Orchestrator creates `bean/BEAN-NNN-<slug>` first |
| `WorkerFailedTwice` | Two consecutive worker failures | Escalate to the user with both failure summaries |

## Dependencies

- Generated agents with frontmatter (SPEC-001) so `subagent_type` resolves.
- Persona file at `ai-team-library/personas/<tier>/<persona>/persona.md`
  (or the generated project's compiled member prompt) for role depth.
- ADR-017 (native dispatch), superseding ADR-008's tmux + status-file
  scheme.
