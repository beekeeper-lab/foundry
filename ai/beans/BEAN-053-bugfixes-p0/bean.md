# BEAN-053: P0 Bug Fixes

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-053 |
| **Status** | New |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Code review identified four bugs in the codebase: a tautological test assertion that always passes, a CLI flag that is silently ignored, a redundant exception handler that masks error types, and timezone-naive timestamps in generation manifests.

## Goal

Fix all four P0 bugs so tests actually verify behavior, CLI flags are validated, errors are reported precisely, and timestamps are unambiguous.

## Scope

### In Scope
- Fix tautological assertion in `tests/test_generator.py:658`
- Enforce `--dry-run` requires `--overlay` in CLI (`foundry_app/cli.py`)
- Split redundant exception handler in CLI (`foundry_app/cli.py:92`)
- Use timezone-aware `datetime.now(timezone.utc)` in `GenerationManifest` (`foundry_app/core/models.py:379`)

### Out of Scope
- Other test quality improvements (covered by BEAN-057)
- CLI logging setup (covered by BEAN-056)

## Acceptance Criteria

- [ ] `test_overlay_preserves_existing_files` asserts file content is preserved (not a tautology)
- [ ] Running `foundry-cli generate comp.yml --dry-run` (without `--overlay`) prints an error and exits with code 1
- [ ] `ValidationError` is caught separately from generic `Exception` with a distinct error message
- [ ] `GenerationManifest.generated_at` produces UTC timestamps with timezone info
- [ ] Existing tests updated to handle timezone-aware datetimes
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Fix tautological assertion in test_generator.py:658 | | | Pending |
| 2 | Add --dry-run / --overlay validation in cli.py _run_generate() | | | Pending |
| 3 | Split exception handler: catch ValidationError then Exception separately | | | Pending |
| 4 | Change datetime.now() to datetime.now(timezone.utc) in models.py | | | Pending |
| 5 | Update any tests that compare generated_at values | | 4 | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

### Bug 1: Tautological assertion
```python
# Current (always True):
assert (output_dir / "user-file.txt").exists() or not (output_dir / "user-file.txt").exists()

# Should be:
assert (output_dir / "user-file.txt").read_text() == "keep me"
```

### Bug 2: --dry-run without --overlay
Add early validation in `_run_generate()`:
```python
if args.dry_run and not args.overlay:
    print("Error: --dry-run requires --overlay", file=sys.stderr)
    return EXIT_VALIDATION_ERROR
```

### Bug 3: Redundant exception handler
```python
# Current:
except (ValidationError, Exception) as exc:
    print(f"Error loading composition: {exc}", file=sys.stderr)

# Should be:
except ValidationError as exc:
    print(f"Validation error in composition: {exc}", file=sys.stderr)
    return EXIT_VALIDATION_ERROR
except Exception as exc:
    print(f"Error loading composition: {exc}", file=sys.stderr)
    return EXIT_VALIDATION_ERROR
```

### Bug 4: Timezone-naive datetime
```python
# Current:
generated_at: datetime = Field(default_factory=datetime.now)

# Should be:
from datetime import timezone
generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```
