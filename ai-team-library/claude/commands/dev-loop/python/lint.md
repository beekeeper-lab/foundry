---
name: lint
description: "Run the Python linter against the project."
---

# /lint Command

Run the Python linter against the project.

## Usage

```
/lint [path] [--fix]
```

- `path` -- Optional file or directory (default: project package root).
- `--fix` -- Apply safe autofixes.

## Examples

```
/lint
/lint foundry_app/
/lint --fix
```

## Notes

This command **invokes** the user-configured linter — `ruff check` (`uv run ruff check` if `uv` is in use). Settings come from `[tool.ruff]` in `pyproject.toml`. Violations are grouped by rule code; non-zero exit on errors. No paired skill — there is no project-spanning execution logic to abstract.
