---
name: scaffold-project
description: "Creates a new project folder structure from a composition spec — directory tree, CLAUDE.md, agent wrappers, context documents, and output folders. Run this before /compile-team and /seed-tasks."
---

# /scaffold-project Command

Creates a new project folder structure from a composition spec — directory tree, CLAUDE.md, agent wrappers, context documents, and output folders. Run this before `/compile-team` and `/seed-tasks`.

## Usage

```
/scaffold-project [composition-file] [--output <path>] [--force] [--dry-run]
```

- `composition-file` -- Path to a `composition.yml` file. Defaults to `./ai/team/composition.yml`.
- `--output <path>` -- Override the output directory (otherwise read from the composition spec).
- `--force` -- Overwrite existing files in the output directory.
- `--dry-run` -- Show what would be created without writing files.

## See Also

- Skill: `claude/skills/scaffold-project/SKILL.md` — canonical execution spec.
