# Task 01: Author `clean-code/conventions.md`

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-17 19:03 |
| **Completed** | 2026-04-17 19:03 |
| **Duration** | < 1m |

## Goal

Create `ai-team-library/expertise/clean-code/conventions.md` so the generator
stops warning `Expertise 'clean-code' missing conventions.md` and consumers
of the `small-python-team` composition receive real clean-code guidance.

## Inputs

- `ai-team-library/expertise/python/conventions.md` — shape/length reference.
- `ai-team-library/expertise/clean-code/principles.md` — existing clean-code
  material; keep `conventions.md` complementary, not duplicative.
- Bean scope: naming, comments/docs, function size/responsibility, error
  handling, testing, refactoring cadence. Language-agnostic.

## Files to Create

1. `ai-team-library/expertise/clean-code/conventions.md`

## Structure Requirements

Follow the standardized expertise template:

- `# Clean Code Conventions` + `## Category` (Practices)
- `## Defaults` table (Concern → Default → Alternatives)
- Numbered sections covering: naming, comments/docstrings, function size &
  responsibility, error handling, testing, refactoring cadence.
- `## Do / Don't` section.
- `## Common Pitfalls` — named + described.
- `## Checklist` — actionable `- [ ]` items.

Keep it language-agnostic; complement (don't repeat) `principles.md`.

## Definition of Done

- [ ] File exists at `ai-team-library/expertise/clean-code/conventions.md` and
      is non-empty.
- [ ] Matches the standardized expertise template used elsewhere in the
      library.
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check foundry_app/` is clean.
