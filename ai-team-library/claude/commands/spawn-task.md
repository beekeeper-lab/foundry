---
name: spawn-task
description: "Dispatches a single specialist persona to execute a single task with only that task's context. Auto-detects tmux and chooses between a tmux+worktree worker (process-isolated, parallelizable) and an in-process Agent-tool subagent (fresh context). The full process lives in the skill."
---

# /spawn-task

This command is a thin entry point; the canonical process lives in the
`spawn-task` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/spawn-task/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
