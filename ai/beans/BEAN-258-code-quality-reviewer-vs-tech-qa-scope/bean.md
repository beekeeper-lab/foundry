# BEAN-258: Code-Quality-Reviewer vs Tech-QA Scope Split

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-258 |
| **Status** | In Progress |
| **Priority** | Low |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 19:26 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

External audit (2026-04-17): "Code-Quality-Reviewer vs Tech-QA overlap. Who owns unit-test review? Regression coverage? Neither persona's scope explicitly partitions this. Two reviewers without a boundary will either collide or both defer."

Today both personas have generic review-style scopes. When the Team Lead decomposes a bean with both on the wave, the split is unclear: does CQR review test code structure? Does Tech-QA own regression coverage on refactors? In practice, each bean resolves this ad-hoc.

## Goal

Each persona's scope explicitly names what it owns and what it defers to the other. A Team Lead decomposing a bean with both on the wave can assign tasks without negotiating boundaries every time.

## Scope

### In Scope
- Small edit to `ai-team-library/personas/code-quality-reviewer/persona.md`: add a "Scope Boundaries" subsection that names what CQR owns (e.g., readability, idiomatic use of the stack, architectural consistency, refactor risk, style) and what it defers to Tech-QA (test strategy, coverage gaps, regression risk, E2E behaviour).
- Symmetric edit to `ai-team-library/personas/tech-qa/persona.md`: same subsection stating what Tech-QA owns and what it defers to CQR.
- Ensure the two descriptions are complementary (no overlap, no gap).
- If BEAN-257 is already in flight or complete, the "Activated When" sections for both personas cross-reference this boundary.

### Out of Scope
- Renaming either persona.
- Adding new personas to cover gaps.
- Changing the bean wave (Tech-QA stays mandatory; CQR stays opt-in under BEAN-257's rules).

## Acceptance Criteria

- [ ] `code-quality-reviewer/persona.md` has a "Scope Boundaries" (or equivalent) subsection listing what it owns vs. defers.
- [ ] `tech-qa/persona.md` has a symmetric "Scope Boundaries" subsection.
- [ ] A quick readability check confirms the two lists partition the review space — no overlap, no gap.
- [ ] If BEAN-257 is complete: both personas' "Activated When" sections cross-reference this bean's boundary.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add Scope Boundaries subsections to both personas | Developer | — | Pending |
| 2 | Verify partition cleanliness + run tests and lint | Tech-QA | 1 | Pending |

> Skipped: BA (default — wording is straightforward and the bean itself specifies ownership categories), Architect (default — no new subsystem, no cross-cutting API change).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Small bean.** This is primarily a documentation edit in two files. BA could land the wording; no Architect needed.

**Pairs with BEAN-257.** Activation rules for both personas should reflect the partition.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add Scope Boundaries subsections to both personas | Developer | < 1m | N/A (suspect) | N/A (suspect) | — |
| 2 | Verify partition cleanliness + run tests and lint | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |