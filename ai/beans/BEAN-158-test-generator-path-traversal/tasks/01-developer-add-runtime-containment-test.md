# Task 01: Add Runtime Containment Traversal Test

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-20 20:13 |
| **Completed** | 2026-02-20 20:14 |
| **Duration** | 1m |

## Goal

Add a test to `tests/test_path_traversal.py` that verifies the runtime containment check in `generate_project()` raises `ValueError("Refusing to generate")` when the resolved output path escapes its root — independently of Pydantic model validation.

## Inputs

- `foundry_app/services/generator.py` lines 250-261 (containment check)
- `tests/test_path_traversal.py` (existing test patterns)

## Approach

Use `model_construct()` to bypass Pydantic validators and create a `ProjectIdentity` with a traversal path in `output_folder` (e.g., `../../escape`). Wrap it in a `CompositionSpec` and call `generate_project()` without the `output_root` parameter. The runtime check fires before library indexing, so no valid library is needed.

## Example Output

```python
def test_runtime_containment_rejects_traversal_bypassing_model(self, tmp_path):
    """Runtime ValueError fires even if model validation was bypassed."""
    safe_root = tmp_path / "safe"
    safe_root.mkdir()

    project = ProjectIdentity.model_construct(
        name="evil", slug="evil",
        output_root=str(safe_root),
        output_folder="../../escape",
    )
    spec = CompositionSpec.model_construct(
        project=project, stacks=[], team=TeamConfig(),
        generation=GenerationOptions(),
        # ... remaining defaults
    )

    with pytest.raises(ValueError, match="Refusing to generate"):
        generate_project(spec, library_root=tmp_path / "lib")
```

## Definition of Done

- [ ] Test added to `TestGeneratorContainment` class in `tests/test_path_traversal.py`
- [ ] Test uses `model_construct()` to bypass Pydantic validators
- [ ] Test asserts `ValueError` with "Refusing to generate" message
- [ ] `uv run pytest tests/test_path_traversal.py` passes
- [ ] `uv run ruff check foundry_app/` is clean
