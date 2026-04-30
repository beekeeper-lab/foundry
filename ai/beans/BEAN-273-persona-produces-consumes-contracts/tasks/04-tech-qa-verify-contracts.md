# Task 04: Verify Contracts — Tests, Lint, and AC Sweep

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 03 |
| **Status** | Done |
| **Started** | 2026-04-30 10:59 |
| **Completed** | 2026-04-30 11:03 |
| **Duration** | 4m |

## Goal

Add focused pytest coverage for the registry / persona-contract pipeline and
verify every BEAN-273 acceptance criterion is met. Fail loudly on any gap.

Test coverage to add (location: `tests/`, follow existing module/class
naming conventions):

1. **Registry parses.** Loading `ai-team-library/contracts/artifact-types.yml`
   returns the expected number of entries (12-15) with all required fields
   populated.
2. **Registry rejects malformed entries.** A synthetic malformed registry
   (in a temp dir) raises with a message that names the offending type.
3. **Persona frontmatter parses.** For each of the five core persona files,
   the loader returns non-empty `produces:` and `consumes:` lists.
4. **Type resolution.** Every type referenced by a persona contract exists
   in the registry. A synthetic persona with an unknown type triggers a
   clear error naming the persona + missing type.
5. **Cross-persona pairing.** At least one BA-produced type is consumed by
   Developer; at least one Developer-produced type is consumed by Tech-QA.
   Make this assertion explicit so a future edit that breaks the chain
   fails fast.
6. **Compiler round-trip.** Run the compiler against a small representative
   composition and assert the resulting `composition.yml` contains a
   `contracts:` block with the per-persona `produces:` / `consumes:` lists
   and the flat `artifact-types:` reference list.

Run the full suite: `uv run pytest`. Run the lint gate:
`uv run ruff check foundry_app/`. Both must pass.

Sweep BEAN-273's eight Acceptance Criteria one-by-one. For each, capture
the concrete evidence (test name, file path, or command output) that
proves it. Report back as a structured pass/fail table in
`ai/outputs/tech-qa/BEAN-273-vdd.md`.

If any criterion lacks evidence, list it under a "Gaps" heading at the top
of the report and stop (do not mark the bean Done — Team-Lead will route
the gap back to the right persona).

## Inputs

- `ai/outputs/ba/BEAN-273-artifact-types.md` — BA registry + contracts
- `ai/outputs/architect/BEAN-273-design.md` — design / shape references
- `ai-team-library/contracts/artifact-types.yml` — registry to validate
- `ai-team-library/personas/ba/persona.md` — frontmatter present
- `ai-team-library/personas/architect/persona.md` — frontmatter present
- `ai-team-library/personas/developer/persona.md` — frontmatter present
- `ai-team-library/personas/tech-qa/persona.md` — frontmatter present
- `ai-team-library/personas/team-lead/persona.md` — frontmatter present
- `foundry_app/services/library_indexer.py` — loader under test
- `foundry_app/services/compiler.py` — compiler under test
- `tests/` — directory for new tests (match existing naming patterns)

## Acceptance Criteria

- [ ] All six new tests added under `tests/` and pass.
- [ ] `uv run pytest` is green (no regressions in the existing 1811 tests).
- [ ] `uv run ruff check foundry_app/` is clean.
- [ ] `ai/outputs/tech-qa/BEAN-273-vdd.md` exists with a row per BEAN-273
      AC, marked Pass with concrete evidence (or Gap with a remediation
      note).
- [ ] Cross-persona assertion fails on a synthetic persona that drops the
      `user-story` consume edge (regression guard).

## Definition of Done

- Tests + VDD report committed.
- The bean can be safely marked Done by Team-Lead solely from the VDD
  report's evidence (no need to re-derive any AC verification).
