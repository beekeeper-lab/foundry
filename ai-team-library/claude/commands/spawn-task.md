---
name: spawn-task
description: "Dispatches a single specialist persona to execute a single task with only that task's context. Auto-detects tmux and chooses between a tmux+worktree worker (process-isolated, parallelizable) and an in-process Agent-tool subagent (fresh context). The full process lives in the skill."
---

# /spawn-task Command

Dispatches a single specialist persona to execute a single task with only
that task's context. Auto-detects tmux and chooses between a tmux+worktree
worker (process-isolated, parallelizable) and an in-process `Agent`-tool
subagent (fresh context). The full process lives in the skill.

## Usage

```
/spawn-task <persona> <task-file>     # explicit persona
/spawn-task <task-file>               # infer persona from Owner: field
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<persona>` | Optional. Persona name (e.g. `developer`, `tech-qa`). Inferred from the task file's `Owner:` field when omitted. |
| `<task-file>` | Required. Path to `ai/beans/BEAN-NNN-<slug>/tasks/NN-<owner>-<slug>.md`. |

## See Also

- Skill: `claude/skills/spawn-task/SKILL.md` — canonical execution spec.
- ADR-008 in `ai/context/decisions.md` — design rationale.
- `/spawn-bean` — bean-level counterpart.
- `/long-run` — uses `/spawn-task` for per-task dispatch in wave execution.
