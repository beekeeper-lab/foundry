# /format Command

Format Python source files according to the project's style.

## Usage

```
/format [path] [--check]
```

- `path` -- Optional file or directory (default: project package root).
- `--check` -- Report formatting drift without writing changes.

## Process

1. **Detect tool** — `ruff format` (`uv run ruff format` if `uv` is in use).
2. **Run** — Reformat the requested path or check it.
3. **Report** — Print the list of files changed (or that would change in `--check` mode).

## Examples

```
/format
/format foundry_app/
/format --check
```

## Notes

This command **invokes** the user-configured formatter. Black is also a valid alternative — swap the command if your project uses it.
