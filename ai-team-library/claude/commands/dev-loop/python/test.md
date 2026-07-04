---
name: test
description: "Run the project's Python test suite."
---

# /test Command

Run the project's Python test suite.

## Usage

```
/test [path] [--fast] [-k <expr>]
```

- `path` -- Optional file or directory to scope the run (default: full suite).
- `--fast` -- Stop on first failure (`-x`).
- `-k <expr>` -- pytest keyword filter forwarded to the runner.

## Examples

```
/test
/test tests/test_foo.py
/test --fast
/test -k auth
```

## Notes

This command **invokes** the user-configured test runner (`uv run pytest` if `uv` is in use; otherwise `pytest`). It surfaces failures with file path, line number, and assertion message. No paired skill — the runtime detail lives in `pyproject.toml`.
