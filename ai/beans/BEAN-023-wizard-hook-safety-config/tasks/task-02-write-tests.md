# Task 2: Write Comprehensive Tests

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Pending |
| **Depends On** | Task 1 |

## Description

Write `tests/test_hook_safety_page.py` with 50+ tests covering the hook & safety config page.

## Test Areas

### HookPackCard Tests
- Construction, initial state, object name
- Enable/disable toggle, signal emission
- Mode selector get/set
- to_hook_pack_selection() output
- load_from_selection() round-trip

### HookSafetyPage Tests
- Construction (empty, with library)
- load_hook_packs() populates cards
- Posture selector get/set
- get_hooks_config() returns correct HooksConfig
- set_hooks_config() restores state
- Safety preset buttons apply correct SafetyConfig
- get_safety_config() returns correct SafetyConfig
- set_safety_config() restores state
- Round-trip get/set/get for both hooks and safety
- is_valid() always returns True
- selection_changed signal emitted on changes

## Acceptance Criteria
- All tests pass with `uv run pytest`
- >=50 test cases
- Full coverage of public API
