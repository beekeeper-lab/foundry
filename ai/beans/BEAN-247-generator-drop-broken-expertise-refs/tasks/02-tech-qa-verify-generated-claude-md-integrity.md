# Task 02: Verify Generated CLAUDE.md Reference Integrity

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 17:43 |
| **Completed** | 2026-04-17 17:44 |
| **Duration** | 1m |

## Goal

Verify that the compiler change in Task 01 holds end-to-end: a generated
project's `CLAUDE.md` contains zero references to
`ai/generated/expertise/<id>.md` files that were not actually emitted.
Extend the self-consistency integration test so the same class of defect
cannot regress.

## Inputs

- `tests/test_generator.py` — `TestGenerationSelfConsistency` (BEAN-242)
- `foundry_app/services/compiler.py` — updated in Task 01
- `examples/small-python-team.yml` — the example that currently lists `clean-code`

## Changes Required

1. Add a test to `TestGenerationSelfConsistency` (or a peer class in
   `test_generator.py`) that scans the generated `CLAUDE.md` for
   `ai/generated/expertise/<id>.md` path references and asserts each
   corresponds to a file that exists on disk.
2. Run the full test suite and confirm `uv run pytest` is green.
3. Regenerate `examples/small-python-team.yml` manually; confirm the
   resulting `CLAUDE.md` does not list `ai/generated/expertise/clean-code.md`
   in its Tech Stack table while still surfacing the missing-conventions
   warning in the pipeline result.

## Acceptance Criteria

- [ ] New self-consistency test covers the "no broken expertise reference"
      invariant.
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check foundry_app/` passes.
- [ ] Manual regeneration of `small-python-team.yml` confirms the fix.

## Definition of Done

- Self-consistency test extended.
- All tests pass, lint clean.
- Manual verification recorded in `ai/outputs/tech-qa/`.
