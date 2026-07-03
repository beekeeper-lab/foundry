# /validate-repo Command

Runs a comprehensive health check on a Foundry project — verifies structure, files, internal links, and stack-specific tooling. Catches missing files, broken references, secrets exposure, and configuration drift.

## Usage

```
/validate-repo [project-dir] [--check-level <structure|content|full>] [--output <path>] [--strict] [--fix]
```

- `project-dir` -- Path to the project root. Defaults to the current working directory.
- `--check-level <level>` -- `structure`, `content`, or `full` (default).
- `--output <path>` -- Write the report to a file instead of stdout.
- `--strict` -- Treat warnings as errors.
- `--fix` -- Attempt to auto-fix simple issues (create missing directories, add missing READMEs).

## See Also

- Skill: `claude/skills/validate-repo/SKILL.md` — canonical execution spec.
