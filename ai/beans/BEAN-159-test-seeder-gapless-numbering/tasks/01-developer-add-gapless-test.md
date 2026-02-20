# Task 01: Add Gapless Numbering Test with Mixed Personas

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-20 20:12 |
| **Completed** | 2026-02-20 20:12 |
| **Duration** | < 1m |

## Goal

Add a new test to `tests/test_seeder.py` in the `TestEdgeCases` class that verifies gapless sequential task numbering when the team includes both known and unknown personas.

## Inputs

- `tests/test_seeder.py` — existing test patterns
- `foundry_app/services/seeder.py` lines 174-185 — numbering logic

## Comprehension Note

The seeder iterates over persona IDs, skipping unknown ones (no templates → `continue`). The counter only increments when a task row is actually emitted (line 185). The existing `test_task_numbers_are_sequential` tests with two known personas only. The new test must mix in an unknown persona to confirm no gaps.

## Example Output

```python
def test_gapless_numbering_with_mixed_personas(self, tmp_path: Path):
    """Task numbers are contiguous 1..N even when unknown personas are in the team."""
    spec = _make_spec(
        team=TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(id="unknown-role"),
            PersonaSelection(id="architect"),
        ]),
        generation=GenerationOptions(seed_mode=SeedMode.DETAILED),
    )
    seed_tasks(spec, tmp_path)
    content = _read_index(tmp_path)
    task_lines = [
        l for l in content.splitlines()
        if l.startswith("| ") and not l.startswith("| #") and not l.startswith("|---")
    ]
    numbers = [int(l.split("|")[1].strip()) for l in task_lines]
    assert numbers == list(range(1, len(numbers) + 1))
```

## Definition of Done

- [ ] Test added to `TestEdgeCases` class in `tests/test_seeder.py`
- [ ] Test uses `["developer", "unknown-role", "architect"]` team list
- [ ] Test extracts row numbers and asserts contiguous 1..N
- [ ] `uv run pytest tests/test_seeder.py` passes
- [ ] `uv run ruff check foundry_app/` is clean
