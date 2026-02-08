# BEAN-057: Test Coverage Gaps

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-057 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-08 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Code review identified three test coverage gaps: `resources.py` has zero test coverage despite containing path resolution logic with fallback behavior, CLI tests mock both `load_composition` and `generate_project` so they only test argparse wiring (not real integration), and overlay mode tests are missing edge cases for symlinks, non-existent targets, and content preservation.

## Goal

Add targeted tests that verify real behavior rather than mocked wiring, covering the gaps identified in code review.

## Scope

### In Scope
- Create `tests/test_resources.py` with tests for dev path, bundled path, and missing resource cases
- Add at least one CLI integration test that calls through to real `load_composition` (using a fixture YAML)
- Fix the tautological overlay assertion (BEAN-053 item 1, if not already done)
- Add overlay edge case tests: target doesn't exist yet, files differ only in content

### Out of Scope
- UI/PySide6 tests (broken in this environment due to missing libGL)
- Exhaustive negative testing for all services (diminishing returns)
- Coverage metrics tooling

## Acceptance Criteria

- [ ] `tests/test_resources.py` exists with at least 3 test cases (dev path found, bundled fallback, neither found)
- [ ] At least one CLI test loads a real composition YAML (not mocked) and verifies it parses correctly
- [ ] At least one overlay test asserts that user files are preserved with correct content after overlay
- [ ] At least one overlay test verifies behavior when target directory doesn't exist yet
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create tests/test_resources.py | | | Pending |
| 2 | Add CLI integration test with real composition loading | | | Pending |
| 3 | Add overlay content preservation test | | | Pending |
| 4 | Add overlay test for non-existent target directory | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

### test_resources.py sketch
```python
def test_dev_path_found(tmp_path, monkeypatch):
    """get_resource_path returns dev path when file exists."""
    ...

def test_bundled_fallback(tmp_path, monkeypatch):
    """get_resource_path falls back to bundled path."""
    ...

def test_neither_found_returns_dev_path(tmp_path, monkeypatch):
    """get_resource_path returns dev path even when missing (with warning)."""
    ...
```

### CLI integration test sketch
```python
def test_real_composition_loading(tmp_path):
    """CLI loads a real YAML file and passes it to the generator."""
    comp = tmp_path / "comp.yml"
    comp.write_text(MINIMAL_COMPOSITION_YAML)
    lib = _make_library(tmp_path)

    # Only mock generate_project, not load_composition
    with patch("foundry_app.services.generator.generate_project") as mock_gen:
        mock_gen.return_value = _mock_result()
        result = main(["generate", str(comp), "--library", str(lib)])

    assert result == EXIT_SUCCESS
    # Verify the real composition was parsed correctly
    call_args = mock_gen.call_args
    assert call_args.kwargs["composition"].project.name == "Test"
```

### Overlay content preservation test
```python
def test_overlay_preserves_user_file_content(tmp_path):
    lib_root = _make_library_dir(tmp_path)
    output_dir = tmp_path / "output" / "test-project"
    output_dir.mkdir(parents=True)
    (output_dir / "user-file.txt").write_text("keep me")

    generate_project(spec, lib_root, output_root=output_dir, overlay=True)

    assert (output_dir / "user-file.txt").read_text() == "keep me"
```

### Non-UI test list update
Remember to add `tests/test_resources.py` to the non-UI test list in MEMORY.md.
