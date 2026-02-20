# Task 01: Add test for None field exclusion in save_composition YAML output

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-20 20:17 |
| **Completed** | 2026-02-20 20:17 |
| **Duration** | < 1m |

## Goal

Add a test to `tests/test_composition_io.py` that verifies `save_composition` excludes `None`-valued fields from the raw YAML file on disk. The test must check the raw YAML dict (not a round-tripped model) to confirm keys like `"safety"` are absent when the field is `None`.

## Inputs

- `foundry_app/io/composition_io.py` — `save_composition` implementation (line 36: `exclude_none=True`)
- `tests/test_composition_io.py` — existing test patterns, `_make_spec` helper, `TestSaveComposition` class

## Example Output

```python
def test_save_excludes_none_fields_from_yaml(self, tmp_path):
    """save_composition with safety=None must not write a 'safety' key."""
    spec = CompositionSpec(
        project=ProjectIdentity(name="NoSafety", slug="no-safety"),
        safety=None,
    )
    out = tmp_path / "none-check.yml"
    save_composition(spec, out)
    raw = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert "safety" not in raw
```

## Definition of Done

- [ ] Test added to `TestSaveComposition` class in `tests/test_composition_io.py`
- [ ] Test creates a `CompositionSpec` with `safety=None`
- [ ] Test saves via `save_composition`, reads raw YAML from disk, asserts `"safety"` key is absent
- [ ] `uv run pytest tests/test_composition_io.py` passes
- [ ] `uv run ruff check foundry_app/` is clean
