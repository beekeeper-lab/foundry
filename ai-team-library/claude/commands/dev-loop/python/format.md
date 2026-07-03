---
name: format
description: "Format Python source files according to the project's style."
---

# /format Command

Format Python source files according to the project's style.

## Usage

```
/format [path] [--check]
```

- `path` -- Optional file or directory (default: project package root).
- `--check` -- Report formatting drift without writing changes.

## Examples

```
/format
/format foundry_app/
/format --check
```

## Notes

This command **invokes** the user-configured formatter — `ruff format` (`uv run ruff format` if `uv` is in use). Black is a valid alternative — swap if your project uses it. Reports the list of files changed (or that would change in `--check` mode). No paired skill.
