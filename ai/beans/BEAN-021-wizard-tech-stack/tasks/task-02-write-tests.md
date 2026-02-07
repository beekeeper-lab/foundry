# Task 02: Write Comprehensive Tests

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-021-T02 |
| **Owner** | tech-qa |
| **Status** | Pending |
| **Depends On** | T01 |

## Description

Write thorough tests for the technology stack page in `tests/test_stack_page.py`. Follow the same test structure as `tests/test_persona_page.py` (45 tests). Cover StackCard and StackSelectionPage construction, selection, data binding, reordering, validation, and round-trips.

## Deliverables

1. **Test file** at `tests/test_stack_page.py` with 40+ tests covering:
   - StackCard construction (creates, id, initial state)
   - StackCard selection (select, deselect, signal emission)
   - StackCard to_stack_selection (default values, order)
   - StackCard load_from_selection (restore state)
   - StackCard unknown stack fallback
   - StackSelectionPage construction (empty, no cards)
   - StackSelectionPage load_stacks (all stacks, replace, empty)
   - StackSelectionPage selection and validation (select one, multiple, deselect all, warning)
   - StackSelectionPage get_stack_selections (empty, populated, ordering)
   - StackSelectionPage set_stack_selections (restore, clear, round-trip)
   - StackSelectionPage ordering (move up, move down, boundary conditions)
   - File count badge display

## Acceptance Criteria

- All tests pass with `uv run pytest tests/test_stack_page.py -v`
- At least 40 test cases
- No test depends on real library files (use mock LibraryIndex)
- Tests follow the same pattern as test_persona_page.py
