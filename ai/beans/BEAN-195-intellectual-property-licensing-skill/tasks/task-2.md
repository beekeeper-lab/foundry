# Task 2: Verify Skill Quality and Acceptance Criteria

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-195-T2 |
| **Owner** | Tech-QA |
| **Status** | Pending |
| **Depends On** | BEAN-195-T1 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Description

Verify the IP & Licensing skill file meets all acceptance criteria:

1. Follows library skill conventions (section structure, table format, naming)
2. Covers all key topics: open source license compatibility, software patents, trade secrets, copyright ownership, CLAs
3. All tests pass (`uv run pytest`)
4. Lint clean (`uv run ruff check foundry_app/`)

## Acceptance Criteria

- [ ] Skill file structure matches library conventions
- [ ] All five topics are covered with actionable guidance
- [ ] Tests pass
- [ ] Lint clean