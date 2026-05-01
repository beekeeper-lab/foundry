# Task 01: Validator — `library_consumers` map + orphan-produces filter

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-289 / 01 |
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 13:42 |
| **Completed** | 2026-05-01 13:43 |
| **Duration** | 1m |

## Goal

Make `validate_contract_graph` distinguish two cases that were previously
collapsed into the same yellow `orphan-produces` warning:

1. **Actionable orphan** — at least one library persona declares
   `consumes` on the artifact, but is not on the team. Adding that
   persona would close the graph. Continue to warn.
2. **Library-wide terminal output** — no persona in the entire library
   declares `consumes` on the artifact. There is no team composition
   that closes the graph. Suppress the warning entirely.

## Inputs

- `foundry_app/services/validator.py` (lines 290–406, the
  `validate_contract_graph` function — the only file that changes for
  the implementation half).
- `ai/beans/BEAN-289-suppress-library-level-orphan-produces/bean.md`
  (Problem Statement, Goal, Scope — the contract you are implementing).

## Acceptance Criteria

- [ ] In `validate_contract_graph`, build `library_consumers:
      dict[str, list[str]]` alongside the existing `library_producers`
      map (same iteration over `registry.personas`, same
      `_CONTRACT_GRAPH_IGNORED_TYPES` skip).
- [ ] In the orphan-produces loop, suppress the warning for any
      `(artifact, producer_id)` where `library_consumers.get(artifact)`
      is empty (i.e., no library persona consumes the artifact).
- [ ] The missing-producer error path is unchanged.
- [ ] The `handoff-packet` exclusion is preserved.
- [ ] Message wording for orphan-produces is unchanged (BEAN-286's
      verbatim-message rendering keeps working).
- [ ] No new public API; the `ValidationResult` shape is unchanged.

## Definition of Done

- [ ] Implementation lands in `foundry_app/services/validator.py`.
- [ ] Local manual sanity check: index the real `ai-team-library/`,
      compose a team of `architect, ba, developer, team-lead, tech-qa`,
      run `validate_contract_graph` — zero `orphan-produces` warnings.
- [ ] Code is the minimum diff to achieve the behavior; no incidental
      refactors.
- [ ] Lint clean: `uv run ruff check foundry_app/services/validator.py`.
- [ ] Hand off to Tech-QA with the list of pre-existing tests that
      need fixture updates (the previous "no library consumer" tests
      relied on the old all-or-nothing behavior).
