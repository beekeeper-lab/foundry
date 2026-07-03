---
name: spawn-task
description: "- Invoked by the /spawn-task slash command. - Should typically be called by Team-Lead during wave execution. Can be called manually for ad-hoc per-task dispatch."
---

# Skill: Spawn Task

## Description

Dispatches a single specialist persona to execute a single task with only that
task's context. Auto-detects the runtime environment and chooses one of two
execution paths:

- **In tmux** (`$TMUX` set): spawn a worker in a git worktree using a child
  tmux window. Process-isolated, parallelizable, durable across the calling
  session's lifetime. Same pattern as `/spawn-bean` but at task granularity.
- **Not in tmux**: invoke the `Agent` tool with `subagent_type=<persona>` from
  the calling Claude session. Fresh subagent context, in-process, single
  return value captured into the task's Telemetry row.

Either path passes the same prompt schema. The supervisor pattern becomes
structural rather than aspirational: each task runs in its own context, not
in the orchestrator's accumulated transcript.

The decision contract is fixed by ADR-008 in `ai/context/decisions.md`. This
skill implements that contract.

## Trigger

- Invoked by the `/spawn-task` slash command.
- Should typically be called by Team-Lead during wave execution. Can be
  called manually for ad-hoc per-task dispatch.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| persona | String | Optional | Persona name (e.g. `developer`, `tech-qa`). When omitted, inferred from the task file's `Owner:` field. |
| task_file | Path | Yes | Absolute or repo-relative path to the task file at `ai/beans/BEAN-NNN-<slug>/tasks/NN-<owner>-<slug>.md`. |
| tmux_session | Environment | No | `$TMUX` — presence selects the tmux execution path. |

## Usage

```
/spawn-task <persona> <task-file>     # explicit persona
/spawn-task <task-file>               # infer persona from Owner: field
```

Examples:

```
/spawn-task developer ai/beans/BEAN-270-spawn-task-command/tasks/02-developer-spawn-task-implementation.md
/spawn-task ai/beans/BEAN-270-spawn-task-command/tasks/03-tech-qa-verify-spawn-task.md
```

## Process

### Phase 1: Argument Resolution

1. **Locate task file** — Resolve the path. If it does not exist, fail with
   a one-line error naming the missing path.
2. **Resolve persona** — If the persona was given explicitly, use it. Else
   parse the task file's metadata table for `| **Owner** | <persona> |` and
   normalize (lowercase, replace spaces with `-`). If neither yields a
   persona, fail with a remediation message.
3. **Validate persona exists** — Confirm a persona file exists at
   `ai-team-library/personas/<persona>/persona.md` (library) or the
   project-local equivalent. If missing, fail with the search paths tried.

### Phase 2: Inputs Validation (BEAN-272 hook integration point)

4. **Parse the task's `Inputs:` section** — Extract the bullet list under
   the `## Inputs` heading. If the validate-task-inputs hook
   (`hooks/validate-task-inputs.py` from BEAN-272) is registered, invoke it.
   On failure, the hook's remediation message is the user-facing error and
   dispatch is aborted.
5. **Escape hatch** — If the task declares `Inputs: NONE (justified: <reason>)`
   with a non-empty reason ≥10 characters, dispatch proceeds.

### Phase 3: Mode Detection

6. **Detect runtime** — Test `[ -n "$TMUX" ]`.
   - **Set** → continue to Phase 4 (tmux path).
   - **Unset** → continue to Phase 5 (Agent-tool path).
7. **Reminder banner** — Only when in the Agent-tool path: emit a one-line
   reminder iff (the task is `priority: high` case-insensitive) OR (the bean
   has ≥4 unfinished tasks). Banner text:

   ```
   Tip: tmux + /long-run --fast gives this task an isolated worker context. Consider relaunching there for high-priority or multi-task work.
   ```

### Phase 4: tmux Execution Path

8. **Compute names** — From the task file path, derive:
   - `BEAN_ID=BEAN-NNN`
   - `TASK_SLUG=<NN>-<owner>-<slug>` (filename minus `.md`)
   - `WORKTREE_DIR=/tmp/agentic-task-${BEAN_ID}-${TASK_SLUG}`
   - `STATUS_FILE=/tmp/agentic-task-${BEAN_ID}-${TASK_SLUG}.status`
   - `WINDOW_NAME=task-${BEAN_ID#BEAN-}-${TASK_SLUG}` (truncate to 40 chars)
9. **Verify branch** — The bean's feature branch (`bean/BEAN-NNN-<slug>`)
   must already exist (the orchestrator creates it before dispatching tasks).
   If missing, fail loudly — `/spawn-task` is not a bean-bootstrap command.
10. **Create or refresh the worktree** —
    ```bash
    git worktree remove --force "$WORKTREE_DIR" 2>/dev/null
    git worktree add "$WORKTREE_DIR" "bean/${BEAN_ID}-${BEAN_SLUG}"
    ```
11. **Write initial status file** — Key-value pairs: `bean`, `task`,
    `persona`, `status: starting`, `worktree`, `updated`.
12. **Build the launcher** — Write a temp shell script that `cd`s into the
    worktree and execs `claude --dangerously-skip-permissions --agent
    <persona> "<prompt>"` with the prompt assembled per the schema in
    Phase 6. The script self-deletes after the claude process exits.
13. **Open the tmux window** —
    ```bash
    tmux new-window -n "$WINDOW_NAME" "bash $LAUNCHER; rm -f $LAUNCHER"
    ```
14. **Return** — Print the window name, the worktree path, and the status
    file path. The calling session does not block on the worker.

### Phase 5: Agent-tool Execution Path

15. **Build the prompt** — Per the Phase 6 schema below.
16. **Issue one Agent call** — Single tool invocation:
    `Agent(subagent_type=<persona>, description="<one-line goal>",
    prompt="<schema-assembled prompt>")`.
17. **Capture the result** — When the Agent returns, parse its summary
    message and write the captured tokens / summary into the task's
    Telemetry row. Update the task's `Status` to `Done` only if the
    subagent reported acceptance criteria as met.
18. **Surface failures** — If the subagent reports failure or partial
    completion, leave Status as `In Progress` (or set it to `!! Failed`)
    and propagate the subagent's message to the calling session.

### Phase 6: Prompt Schema (both paths)

The prompt has five required sections, in this order. Identical across
paths. Workers tolerate trailing content (additive sections from future
beans like BEAN-273 are backwards-compatible).

| Section | Content |
|---------|---------|
| **Role** | One line: `You are the <persona> persona. Your job: <task goal>.` |
| **Task file** | Absolute path. Worker reads this first. |
| **Inputs** | Verbatim copy of the task's `Inputs:` list (paths and anchors). |
| **Acceptance** | Verbatim copy of the task's `Acceptance Criteria` block. |
| **Completion contract** | (a) Flip task Status to `Done` when criteria met; (b) commit on the current branch with message `BEAN-NNN task NN: <summary>`; (c) exit. |

The persona's own context bundle
(`ai-team-library/personas/<persona>/persona.md`) is referenced by name,
not inlined. The worker reads it once on startup.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| status_file | Plain text (tmux path only) | `/tmp/agentic-task-BEAN-NNN-<slug>.status` |
| worktree | Directory (tmux path only) | `/tmp/agentic-task-BEAN-NNN-<slug>` |
| task_status | Markdown edit | The task file's `Status` advances to `Done` (or `!! Failed`). |
| telemetry | Markdown edit | Bean's Telemetry per-task row updated by the worker on completion. |

## Quality Criteria

- The prompt schema is identical for both execution paths.
- A failed `Inputs:` validation aborts dispatch with a clear remediation.
- The reminder banner emits only when the heuristic fires (high-priority
  task OR ≥4 remaining tasks); no blanket warning.
- tmux windows auto-close when the worker process exits — no bare shell
  is left in the tmux window.
- Worktrees are removed by the orchestrator after merge (not by
  `/spawn-task` itself).

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `TaskFileMissing` | The task file path does not exist | Print path; exit 1 |
| `PersonaUnresolvable` | No `Owner:` field and no explicit persona arg | Ask the user to supply the persona; exit 1 |
| `PersonaNotFound` | Persona file missing in library/project | List the search paths tried; exit 1 |
| `InputsValidationFailed` | BEAN-272 hook rejected the dispatch | Show the hook's remediation; exit 1 |
| `BranchMissing` (tmux) | Feature branch does not exist | Fail loudly — `/spawn-task` does not bootstrap branches |
| `WorktreeCreateFailed` (tmux) | `git worktree add` failed | Show the git error; exit 1 |
| `AgentToolUnavailable` | Calling environment has no Agent tool (rare) | Fall back to direct user execution; exit 1 |

## Dependencies

- Task file at the supplied path with a `## Inputs`, `## Acceptance Criteria`,
  and `Owner:` field in the metadata table.
- Persona file at `ai-team-library/personas/<persona>/persona.md` (or the
  project-local mirror).
- For the tmux path: an active tmux session (`$TMUX` set), `git worktree`
  available, and the bean's feature branch already created.
- For the Agent-tool path: the calling session has access to the `Agent`
  tool with `subagent_type=<persona>` configured.
- ADR-008 in `ai/context/decisions.md` for the design rationale and the
  load-bearing decisions this skill must conform to.

## See Also

- `/spawn-bean` — bean-level dispatch (full lifecycle). `/spawn-task` is
  the per-task counterpart.
- `/long-run` — autonomous backlog processing; uses `/spawn-task` as the
  preferred per-task dispatch mechanism in Phase 4.
- BEAN-272 — `Inputs:` validation hook integrated at Phase 2.
- BEAN-273 — `produces:`/`consumes:` contracts; will add a "Consumes"
  line to the prompt schema when it lands.
