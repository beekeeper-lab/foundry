# Task 02: Verify None exclusion test and acceptance criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | Task 01 |
| **Status** | Done |
| **Started** | 2026-02-20 20:19 |
| **Completed** | 2026-02-20 20:19 |
| **Duration** | < 1m |

## Goal

Verify the developer's test is correct, all tests pass, lint is clean, and all bean acceptance criteria are met.

## Inputs

- `tests/test_composition_io.py` — developer's changes
- Bean acceptance criteria (from bean.md)

## Definition of Done

- [ ] New test correctly saves a spec with `safety=None`
- [ ] New test reads raw YAML (not round-tripped model) and asserts `"safety"` key absent
- [ ] `uv run pytest` — full suite passes
- [ ] `uv run ruff check foundry_app/` — clean
- [ ] All bean acceptance criteria verified
