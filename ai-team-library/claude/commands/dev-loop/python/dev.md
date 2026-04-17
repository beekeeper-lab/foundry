# /dev Command

Launch the project's main entry point in development mode.

## Usage

```
/dev [args...]
```

- `args` -- Forwarded to the application.

## Process

1. **Detect entry point** — Read the `[project.scripts]` table in `pyproject.toml` for the primary entry point, or fall back to `python -m <package>`.
2. **Run** — Invoke with `uv run` if `uv` is in use; otherwise `python` directly.
3. **Report** — Stream stdout/stderr until the process exits.

## Examples

```
/dev
/dev --help
```

## Notes

This command **invokes** the user-configured entry point. If the project does not declare one, define it in `pyproject.toml` first.
