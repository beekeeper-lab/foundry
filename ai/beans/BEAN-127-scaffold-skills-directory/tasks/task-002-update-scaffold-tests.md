# Task 002: Update scaffold tests for skills directory

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-127-T002 |
| **Owner** | tech-qa |
| **Depends On** | T001 |
| **Status** | Pending |

## Description

Update `tests/test_scaffold.py`:
1. Add a dedicated test `test_creates_claude_skills_dir`
2. Add `.claude/skills` to the `test_creates_all_standard_dirs` expected list
3. Update `test_result_wrote_count_matches_dirs_created` count from 9 to 10

## Acceptance Criteria

- [ ] New test verifies `.claude/skills` directory is created
- [ ] All standard dirs test includes `.claude/skills`
- [ ] Count test reflects the new directory
- [ ] All tests pass
