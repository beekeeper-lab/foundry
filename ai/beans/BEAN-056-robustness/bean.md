# BEAN-056: Robustness Improvements

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-056 |
| **Status** | Done |
| **Priority** | Low |
| **Created** | 2026-02-08 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Code review identified four robustness issues: `resources.py` silently returns paths to non-existent files, the scaffold service has a redundant `exists()` check that creates a TOCTOU window, the library manager's file write has no error handling (raw tracebacks shown to users), and the CLI never initializes logging (all CLI-driven generation is unlogged).

## Goal

Improve error handling and reliability so failures produce clear messages and all operations are logged.

## Scope

### In Scope
- Add warning log when `get_resource_path()` returns a non-existent path
- Remove redundant `exists()` check in `scaffold.py` (rely on `exist_ok=True`)
- Wrap `write_text()` in library manager with try/except and show `QMessageBox`
- Add `setup_logging()` call in CLI `_run_generate()`
- Remove or annotate unused `StackOverrides` model

### Out of Scope
- Atomic writes / temp+rename pattern (over-engineering for this use case)
- Structured JSON logging
- Thread-safety in logging init (single-threaded init path)

## Acceptance Criteria

- [x] `get_resource_path()` logs a warning when neither dev nor bundled path exists
- [x] `scaffold_project()` no longer has the redundant `if dir_path.exists()` check
- [x] Library manager `_on_new_asset()` catches `OSError` and shows a user-friendly error dialog
- [x] CLI calls `setup_logging()` before generation so logs are written to disk
- [x] `StackOverrides` is removed or marked with a TODO comment
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add warning log in resources.py get_resource_path() | Developer | | Done |
| 2 | Simplify scaffold.py directory creation (remove exists check) | Developer | | Done |
| 3 | Add try/except around write_text in library_manager._on_new_asset() | Developer | | Done |
| 4 | Add setup_logging() call in cli.py _run_generate() | Developer | | Done |
| 5 | Clean up StackOverrides in models.py | Developer | | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

### resources.py change
```python
import logging
logger = logging.getLogger(__name__)

def get_resource_path(relative: str) -> Path:
    dev_path = _PROJECT_ROOT / relative
    if dev_path.is_file():
        return dev_path
    parts = Path(relative).parts
    if parts and parts[0] == "resources":
        bundled = _BUNDLED_RESOURCES / Path(*parts[1:])
        if bundled.is_file():
            return bundled
    logger.warning("Resource not found: %s", relative)
    return dev_path
```

### scaffold.py simplification
```python
# Remove this:
if dir_path.exists():
    logger.debug("Directory already exists, skipping: %s", dir_path)
else:
    dir_path.mkdir(parents=True, exist_ok=True)

# Replace with:
dir_path.mkdir(parents=True, exist_ok=True)
```
Note: The `created` list tracking needs adjustment — count based on whether `mkdir` was a no-op or not. Simplest approach: always call `mkdir`, then check `dir_path` against a pre-computed set of existing dirs.

### CLI logging
```python
def _run_generate(args: argparse.Namespace) -> int:
    from foundry_app.core.logging_config import setup_logging
    setup_logging()
    # ... rest of function
```
