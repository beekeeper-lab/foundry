# Task 2: Verify skill and run tests

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Status** | Done |
| **Depends On** | Task 1 |
| **Started** | 2026-02-20 19:39 |
| **Completed** | 2026-02-20 19:39 |
| **Duration** | < 1m |

## Description

Verify the legal-drafting skill file follows library conventions, covers all required topics, and ensure the overall test suite and linter still pass.

## Acceptance Criteria

- [ ] Skill file follows standard SKILL.md format (all sections present)
- [ ] All five document types covered (ToS, Privacy Policy, EULA, DPA, Cookie Consent)
- [ ] Plain-language compliance is addressed
- [ ] `uv run pytest` passes
- [ ] `uv run ruff check foundry_app/` passes