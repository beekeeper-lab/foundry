# /test Command

Run the project's Python test suite.

## Usage

```
/test [path] [--fast] [-k <expr>]
```

- `path` -- Optional file or directory to scope the run (default: full suite).
- `--fast` -- Stop on first failure (`-x`).
- `-k <expr>` -- pytest keyword filter forwarded to the runner.

## Process

1. **Detect runner** — `pytest` is assumed (`uv run pytest` if `uv` is in use; otherwise `pytest`).
2. **Run** — Execute the test command at the repo root.
3. **Report** — Surface failures with file path, line number, and the assertion message.

## Examples

```
/test
/test tests/test_foo.py
/test --fast
/test -k auth
```

## Notes

This command **invokes** the user-configured test runner — it does not install or configure it. If `pytest` is not yet set up, configure `pyproject.toml` first.
