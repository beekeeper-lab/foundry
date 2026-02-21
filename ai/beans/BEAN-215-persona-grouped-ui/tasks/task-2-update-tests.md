# Task 2: Update Tests for Grouped Layout

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Status** | Done |
| **Depends On** | Task 1 |
| **Started** | 2026-02-20 21:03 |
| **Completed** | 2026-02-20 21:03 |
| **Duration** | < 1m |

## Description

Update `tests/test_persona_page.py` to:

1. Update `_make_persona()` to accept a `category` parameter
2. Update `_make_full_library()` to create 24 personas with categories
3. Add tests for grouped layout:
   - Categories create QGroupBox sections
   - Category headers show correct count
   - "Other" group for personas with no category
   - All groups expanded by default
4. Ensure existing tests still pass (adapt for 24 personas)
5. Test get_team_config/set_team_config across groups
6. Test PERSONA_DESCRIPTIONS has 24 entries

## Inputs
- Modified `persona_page.py` from Task 1
- `tests/test_persona_page.py`

## Outputs
- Updated test file with grouped layout coverage

## Acceptance Criteria
- All tests pass (`uv run pytest tests/test_persona_page.py`)
- Coverage for grouped layout, category headers, collapsibility
- get_team_config/set_team_config tested across groups