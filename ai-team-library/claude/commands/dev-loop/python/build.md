# /build Command

Build the Python project distributable (wheel + sdist).

## Usage

```
/build [--wheel-only] [--sdist-only]
```

- `--wheel-only` -- Skip the source distribution.
- `--sdist-only` -- Skip the wheel.

## Process

1. **Detect tooling** — `uv build` if `uv` is in use; otherwise `python -m build`.
2. **Run** — Build artifacts into `dist/`.
3. **Report** — List produced files and their sizes.

## Examples

```
/build
/build --wheel-only
```

## Notes

This command **invokes** the user-configured build backend (declared in `pyproject.toml`). It does not install or change the backend.
