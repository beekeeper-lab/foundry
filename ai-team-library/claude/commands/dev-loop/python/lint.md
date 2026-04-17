# /lint Command

Run the Python linter against the project.

## Usage

```
/lint [path] [--fix]
```

- `path` -- Optional file or directory (default: project package root).
- `--fix` -- Apply safe autofixes.

## Process

1. **Detect tool** — `ruff check` (`uv run ruff check` if `uv` is in use).
2. **Run** — Lint the requested path.
3. **Report** — Print violations grouped by rule code; exit non-zero on errors.

## Examples

```
/lint
/lint foundry_app/
/lint --fix
```

## Notes

This command **invokes** the user-configured linter (settings in `pyproject.toml` under `[tool.ruff]`). It does not install or configure ruff.
