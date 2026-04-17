# Task 01 — Developer: Add Scope Boundaries Subsections to CQR and Tech-QA

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 19:27 |
| **Completed** | 2026-04-17 19:27 |
| **Duration** | < 1m |

## Goal

Add complementary `## Scope Boundaries` subsections to `code-quality-reviewer/persona.md` and `tech-qa/persona.md` so the Team Lead can assign review-adjacent tasks without re-negotiating the boundary each bean.

## Inputs

- `ai/beans/BEAN-258-code-quality-reviewer-vs-tech-qa-scope/bean.md` (this bean)
- `ai-team-library/personas/code-quality-reviewer/persona.md`
- `ai-team-library/personas/tech-qa/persona.md`

## Required Changes

1. **`ai-team-library/personas/code-quality-reviewer/persona.md`** — add `## Scope Boundaries` section after `## Scope` and before `## Operating Principles`. Structure:
   - `### Owns (CQR)` — bullet list. Include: readability and clarity, idiomatic use of the language/framework, architectural consistency with ADRs, refactor risk, style/convention conformance, structural quality of test code (naming, independence, assertions vs. implementation coupling).
   - `### Defers to Tech-QA` — bullet list. Include: test strategy adequacy for the bean's acceptance criteria, coverage gap analysis, regression risk, E2E / integration behaviour, flakiness, test data/environment isolation.

2. **`ai-team-library/personas/tech-qa/persona.md`** — add `## Scope Boundaries` section in the same structural position (after `## Scope`, before `## Operating Principles`). Structure:
   - `### Owns (Tech-QA)` — mirror items deferred from CQR: test strategy adequacy, coverage gap analysis, regression risk, E2E / integration behaviour, flakiness / environment isolation, fix validation.
   - `### Defers to Code-Quality-Reviewer` — mirror items owned by CQR: readability of production code, idiomatic use of the stack, architectural consistency, refactor risk, style, structural quality of test code.

3. Both new sections open with a one-sentence lead referencing the complementary partition and pointing to the sibling persona.

## Acceptance Criteria

- [ ] `code-quality-reviewer/persona.md` has `## Scope Boundaries` with `### Owns (CQR)` and `### Defers to Tech-QA`.
- [ ] `tech-qa/persona.md` has `## Scope Boundaries` with `### Owns (Tech-QA)` and `### Defers to Code-Quality-Reviewer`.
- [ ] The two "Owns" lists concatenated cover every item in the two "Defers" lists — no item is deferred by one persona without being owned by the other.
- [ ] Neither "Owns" list contains an item that also appears in the other persona's "Owns" list.
- [ ] Ruff clean: `uv run ruff check foundry_app/` (no Python changes, but sanity check).

## Notes

BEAN-257 is Approved but not Done. Cross-referencing the boundary from the "Activated When" section is optional per the bean and will be picked up when BEAN-257 lands.
