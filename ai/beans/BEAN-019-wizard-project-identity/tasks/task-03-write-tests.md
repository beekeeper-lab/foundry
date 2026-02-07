# Task 03: Write tests for project identity page

| Field | Value |
|-------|-------|
| Owner | tech-qa |
| Status | Pending |
| Depends On | task-02 |

## Description

Create `tests/test_project_page.py` with comprehensive tests for the ProjectPage widget including:
- Construction and widget presence
- Slug auto-generation from name
- Validation behavior (empty name → incomplete)
- Data extraction to ProjectIdentity model
- Edge cases (special chars in name, empty tagline)

## Acceptance Criteria

- [ ] All tests pass
- [ ] Coverage includes happy path and edge cases
- [ ] Tests follow existing test patterns (see test_main_window.py)
