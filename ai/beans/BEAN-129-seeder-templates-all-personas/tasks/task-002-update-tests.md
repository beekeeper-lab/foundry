# Task 002: Update Seeder Tests for All 13 Personas

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-129-T002 |
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | T001 |

## Description

Update `tests/test_seeder.py` to verify all 13 personas produce seed tasks. Add tests for each of the 8 new personas in both detailed and kickoff modes. Update the `TestAllPersonas` tests to include all 13 personas and verify correct task counts.

## Acceptance Criteria

- [ ] Tests for each of the 8 new personas in detailed mode
- [ ] Updated full-team tests include all 13 personas
- [ ] All tests pass (`uv run pytest tests/test_seeder.py`)
- [ ] No "No seed task templates" warnings for any library persona
