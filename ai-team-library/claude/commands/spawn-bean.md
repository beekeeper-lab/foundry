---
name: spawn-bean
description: "Spawns one or more tmux workers, each running a Team Lead Claude Code agent that picks and executes a bean autonomously. Workers report progress via status files; the main window displays a live dashboard. Workers auto-submit and auto-close when done."
---

# /spawn-bean Command

Spawns one or more tmux workers, each running a Team Lead Claude Code agent that picks and executes a bean autonomously. Workers report progress via status files; the main window displays a live dashboard. Workers auto-submit and auto-close when done.

## Usage

```
/spawn-bean              # 1 worker — team lead picks the best bean
/spawn-bean 16           # 1 worker on BEAN-016
/spawn-bean --count 3    # 3 workers — each auto-picks its own bean
/spawn-bean 16 17 18     # 3 workers — one per specified bean
/spawn-bean 16 17 18 --wide   # all 3 in one window as tiled panes
/spawn-bean --count 4 --wide  # 4 auto-pick workers in a tiled grid
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<bean-ids...>` | Optional. One or more bean IDs (`16`, `BEAN-016`). Each gets its own worker. |
| `--count N` / `-n N` | Spawn N workers. Each team lead auto-picks the highest-priority available bean. |
| `--wide` | Put all workers in a single window as tiled panes (wide monitor mode). |
| *(no args)* | Spawn 1 worker. Team lead auto-picks the best available bean. |

## See Also

- No standalone skill — `/spawn-bean` reuses the worker, worktree, and dashboard machinery owned by the `long-run` skill. See `claude/skills/long-run/SKILL.md` for the canonical Worker Spawning, Status File Protocol, dashboard loop, and tiled-mode (`--wide`) details.
- `/long-run` — autonomous backlog processing that wraps the same workers.
- `/spawn-task` — per-task counterpart at task granularity.
