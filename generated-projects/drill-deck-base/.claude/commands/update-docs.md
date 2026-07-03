# /update-docs Command

Detects documentation drift and proposes updates. Compares docs against recent code, config, and dependency changes to identify stale sections, then proposes specific updates.

## Usage

```
/update-docs [project-dir] [--since <ref-or-date>] [--docs <paths>] [--output <path>] [--fix] [--check-completeness]
```

- `project-dir` -- Project root. Defaults to current working directory.
- `--since <ref>` -- Scope changes to a git ref or date (e.g., `v1.0.0`, `2025-01-01`).
- `--docs <paths>` -- Comma-separated list of specific doc files to check.
- `--output <path>` -- Write the drift report to a file (default: stdout).
- `--fix` -- Apply proposed updates directly instead of just reporting.
- `--check-completeness` -- Verify standard docs exist (default: true).

## See Also

- Skill: `claude/skills/update-docs/SKILL.md` — canonical execution spec.
