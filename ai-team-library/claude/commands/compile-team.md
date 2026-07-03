---
name: compile-team
description: "Compiles selected personas, stacks, and workflows into a complete team configuration ready for use in a project workspace. Reads a composition spec, resolves all references against the AI Team Library, and produces a unified CLAUDE.md plus supporting artifacts."
---

# /compile-team Command

Compiles selected personas, stacks, and workflows into a complete team configuration ready for use in a project workspace. Reads a composition spec, resolves all references against the AI Team Library, and produces a unified `CLAUDE.md` plus supporting artifacts.

## Usage

```
/compile-team [composition-file] [--output-dir <path>] [--strict] [--dry-run] [--no-manifest] [--verbose]
```

- `composition-file` -- Path to a `composition.yml` file. Defaults to `./ai/team/composition.yml`.
- `--output-dir <path>` -- Override the output directory.
- `--strict` -- Treat all warnings as errors; abort on any validation issue.
- `--dry-run` -- Validate and report what would be generated without writing files.
- `--no-manifest` -- Skip writing the generation manifest.
- `--verbose` -- Print detailed progress for each compilation stage.

## See Also

- Skill: `claude/skills/compile-team/SKILL.md` — canonical execution spec.
