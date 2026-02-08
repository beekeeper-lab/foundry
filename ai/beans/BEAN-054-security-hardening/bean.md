# BEAN-054: Security Hardening

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-054 |
| **Status** | New |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Code review identified four security hardening items: `FileAction.path` accepts path traversal sequences (`../`), the library manager deletes files without verifying they're within the library root, `shutil.copy2` follows symlinks in the asset copier, and `rglob("*")` follows symlinks in overlay tree comparison.

While Foundry is a local desktop tool (not a server), these are defense-in-depth issues — a malicious composition YAML or a library containing symlinks could write/delete files outside intended directories.

## Goal

Add path containment validation throughout the file operation pipeline so that all file reads, writes, copies, and deletes are provably within their expected root directories.

## Scope

### In Scope
- Add `field_validator` on `FileAction.path` to reject `..` and absolute paths
- Add path containment check before `shutil.rmtree`/`unlink` in library manager
- Skip symlinks in `asset_copier._copy_directory_files()`
- Skip symlinks in `generator._compare_trees()`

### Out of Scope
- Sandboxing or process-level isolation
- Library signature verification
- Network-level security

## Acceptance Criteria

- [ ] `FileAction(path="../../../etc/passwd", action=FileActionType.CREATE)` raises `ValidationError`
- [ ] `FileAction(path="/etc/passwd", action=FileActionType.CREATE)` raises `ValidationError`
- [ ] Library manager refuses to delete paths outside `self._library_root`
- [ ] Asset copier skips symlinks with a warning
- [ ] Overlay tree comparison skips symlinks with a warning
- [ ] Tests cover all four validation paths (positive and negative)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add field_validator to FileAction.path in models.py | | | Pending |
| 2 | Add path containment check in library_manager._on_delete_asset() | | | Pending |
| 3 | Add symlink skip in asset_copier._copy_directory_files() | | | Pending |
| 4 | Add symlink skip in generator._compare_trees() | | | Pending |
| 5 | Write tests for path traversal rejection in test_models.py | | 1 | Pending |
| 6 | Write tests for symlink skipping in test_asset_copier.py and test_generator.py | | 3, 4 | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

### FileAction path validator
```python
@field_validator("path")
@classmethod
def validate_path(cls, v: str) -> str:
    p = PurePosixPath(v)
    if p.is_absolute():
        raise ValueError(f"FileAction path must be relative, got: {v}")
    if ".." in p.parts:
        raise ValueError(f"FileAction path must not contain '..', got: {v}")
    return v
```

### Library manager containment check
```python
resolved = path.resolve()
if not resolved.is_relative_to(self._library_root.resolve()):
    logger.error("Refusing to delete path outside library root: %s", resolved)
    QMessageBox.critical(self, "Error", "Cannot delete: path is outside library root.")
    return
```

### Symlink skip pattern
```python
if src_file.is_symlink():
    warnings.append(f"Skipping symlink: {src_file.name}")
    continue
```
