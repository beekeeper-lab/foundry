---
name: build
description: "Build the Python project distributable (wheel + sdist)."
---

# /build Command

Build the Python project distributable (wheel + sdist).

## Usage

```
/build [--wheel-only] [--sdist-only]
```

- `--wheel-only` -- Skip the source distribution.
- `--sdist-only` -- Skip the wheel.

## Examples

```
/build
/build --wheel-only
```

## Notes

This command **invokes** the user-configured build backend (declared in `pyproject.toml`) — `uv build` if `uv` is in use, otherwise `python -m build`. Artifacts go to `dist/`. No paired skill.
