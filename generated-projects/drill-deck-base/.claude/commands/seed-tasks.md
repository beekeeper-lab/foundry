# /seed-tasks Command

Generates an initial set of tasks from project objectives and assigns them to team personas. Decomposes high-level objectives into discrete, assignable tasks with dependencies, priorities, and a dependency graph.

## Usage

```
/seed-tasks [objectives-file] [--max-tasks <n>] [--cycle-scope <label>] [--format <md|yaml>] [--persona-filter <ids>] [--dry-run] [--verbose]
```

- `objectives-file` -- Path to a markdown or YAML file. Defaults to `./ai/objectives.md`.
- `--max-tasks <n>` -- Cap the total number of generated tasks.
- `--cycle-scope <label>` -- Cycle label (default: `cycle-1`).
- `--format <md|yaml>` -- Output format. Default `md`.
- `--persona-filter <ids>` -- Only generate tasks for specific personas.
- `--dry-run` -- Show what would be generated without writing files.
- `--verbose` -- Print decomposition reasoning for each objective.

## See Also

- Skill: `claude/skills/seed-tasks/SKILL.md` — canonical execution spec.
