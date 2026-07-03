---
name: dev
description: "Launch the project's main entry point in development mode."
---

# /dev Command

Launch the project's main entry point in development mode.

## Usage

```
/dev [args...]
```

- `args` -- Forwarded to the application.

## Examples

```
/dev
/dev --help
```

## Notes

This command **invokes** the user-configured entry point — read from the `[project.scripts]` table in `pyproject.toml`, or fall back to `python -m <package>`. Uses `uv run` if `uv` is in use; otherwise `python` directly. No paired skill.
