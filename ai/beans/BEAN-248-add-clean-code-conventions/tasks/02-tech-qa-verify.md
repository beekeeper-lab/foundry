# Task 02: Verify Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Verify BEAN-248 acceptance criteria are met end-to-end.

## Inputs

- `ai-team-library/expertise/clean-code/conventions.md` (created in task 01)
- `examples/small-python-team.yml`
- `foundry-cli generate` command

## Verification Steps

1. Regenerate the sample composition:
   ```bash
   uv run foundry-cli generate examples/small-python-team.yml --library ai-team-library
   ```
   Capture stdout+stderr; assert no warning mentions `clean-code`.
2. Confirm the generated project contains `ai/generated/expertise/clean-code.md`
   on disk and that the generated `CLAUDE.md` references it.
3. Run `uv run pytest` — all tests must pass.
4. Run `uv run ruff check foundry_app/` — clean exit.

## Definition of Done

- [ ] Regeneration emits zero `clean-code` warnings.
- [ ] `ai/generated/expertise/clean-code.md` exists in the output tree and is
      referenced from generated `CLAUDE.md`.
- [ ] `uv run pytest` passes (baseline 1811 tests).
- [ ] `uv run ruff check foundry_app/` passes.
