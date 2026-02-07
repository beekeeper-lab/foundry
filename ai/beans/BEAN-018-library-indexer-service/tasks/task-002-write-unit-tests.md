# Task 002: Write Unit Tests

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-018-T002 |
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | T001 |

## Description

Create `tests/test_library_indexer.py` with comprehensive tests:

1. **Integration test against real library** — call `build_library_index()` against `ai-team-library/` and verify:
   - 13 personas discovered
   - 11 stacks discovered
   - 5 hook packs discovered
   - Each persona has correct file flags
   - Templates are non-empty for personas that have them

2. **Graceful degradation tests** — using tmp_path:
   - Missing personas directory → empty list, no crash
   - Missing stacks directory → empty list, no crash
   - Missing hooks directory → empty list, no crash
   - Completely empty library root → empty LibraryIndex

3. **Lookup helper tests** — verify `persona_by_id()`, `stack_by_id()`, `hook_pack_by_id()` work

## Acceptance Criteria

- [ ] All tests pass with `uv run pytest tests/test_library_indexer.py -v`
- [ ] Full test suite passes with `uv run pytest`
- [ ] Lint clean with `uv run ruff check foundry_app/ tests/`
