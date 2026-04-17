# Task 02 — Tech-QA: Verify Scope Boundary Partition + Regression Gates

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Confirm the two new `## Scope Boundaries` sections form a clean partition (no overlap, no gap) and that the documentation change has not broken the test suite or lint.

## Inputs

- `ai-team-library/personas/code-quality-reviewer/persona.md` (post task 01 edit)
- `ai-team-library/personas/tech-qa/persona.md` (post task 01 edit)
- `ai/beans/BEAN-258-code-quality-reviewer-vs-tech-qa-scope/bean.md`

## Verification Steps

1. Read both `## Scope Boundaries` sections.
2. Build a two-column table (mentally or scratch): for every item in either "Owns" list, confirm it does not also appear in the other "Owns" list.
3. For every item in either "Defers" list, confirm it is present (by meaning, not exact wording) in the other persona's "Owns" list.
4. Flag any ambiguous item — a word that could be read as belonging to either persona — and propose a disambiguating rewording.
5. Run `uv run pytest`. Must pass with no new failures.
6. Run `uv run ruff check foundry_app/`. Must be clean.

## Acceptance Criteria

- [ ] Partition verified: no overlap between the two "Owns" lists, no gap between "Defers" and the sibling "Owns" list.
- [ ] Any ambiguity identified is either rephrased in the persona files or documented here with rationale.
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check foundry_app/` passes.

## Notes

This is a documentation change — no new test coverage is expected. The gates (pytest + ruff) are regression protection, not feature validation.
