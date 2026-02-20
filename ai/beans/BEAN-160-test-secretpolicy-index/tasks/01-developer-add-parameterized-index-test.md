# Task 01: Add Parameterized Test for SecretPolicy Index Reporting

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-20 20:12 |
| **Completed** | 2026-02-20 20:12 |
| **Duration** | < 1m |

## Goal

Add a parameterized pytest test to `tests/test_models.py` inside `TestSecretPolicy` that places an invalid regex at different positions in `secret_patterns` and asserts the error message contains `secret_patterns[N]` with the correct zero-based index N.

## Inputs

- `foundry_app/core/models.py` lines 268-287 (SecretPolicy class + validator)
- `tests/test_models.py` lines 196-201 (existing TestSecretPolicy class)

## Example Output

```python
@pytest.mark.parametrize("position", [0, 1, 2])
def test_validate_secret_patterns_reports_correct_index(self, position):
    valid = r"(?i)api_key"
    invalid = "[invalid"
    patterns = [valid] * position + [invalid] + [valid] * (2 - position)
    with pytest.raises(ValidationError, match=rf"secret_patterns\[{position}\]"):
        SecretPolicy(secret_patterns=patterns)
```

## Definition of Done

- [ ] Parameterized test added to `TestSecretPolicy` class in `tests/test_models.py`
- [ ] Test covers positions 0, 1, and 2
- [ ] Each case asserts error message contains `secret_patterns[N]` with correct index
- [ ] `uv run pytest tests/test_models.py -v` passes
- [ ] `uv run ruff check foundry_app/` is clean
