# /validate-config Command

Checks configuration hygiene and detects exposed secrets — hardcoded credentials, missing config variables, untracked .env files, and cross-environment inconsistencies.

## Usage

```
/validate-config [project-dir] [--schema <path>] [--patterns <path>] [--environments <list>] [--output <path>] [--severity <level>] [--fix-gitignore]
```

- `project-dir` -- Project root. Defaults to current working directory.
- `--schema <path>` -- Config schema file for validation.
- `--patterns <path>` -- Custom secret detection patterns.
- `--environments <list>` -- Comma-separated environments (e.g., `dev,staging,prod`).
- `--output <path>` -- Write the report to a file (default: stdout).
- `--severity <level>` -- Minimum severity: `critical`, `error`, `warning`, `info`, `all` (default).
- `--fix-gitignore` -- Auto-add .env to .gitignore if missing.

## See Also

- Skill: `claude/skills/validate-config/SKILL.md` — canonical execution spec.
