# BEAN-289: Suppress Library-Level Orphan-Produces Warnings the User Cannot Fix

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-289 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-05-01 |
| **Started** | 2026-05-01 13:40 |
| **Completed** | 2026-05-01 13:46 |
| **Duration** | 1600h 38m |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | BEAN-286 |

## Problem Statement

BEAN-286 made the team-coherence indicator surface the validator's verbatim
messages. That immediately exposed a UX flaw in the validator itself: it
treats two very different conditions as the same yellow warning.

1. **Fixable orphan** — a team member produces an artifact, and *some other
   library persona* declares `consumes: <that-artifact>`. Adding that
   persona to the team would close the graph. The warning is actionable.
2. **Library-wide terminal output** — a team member produces an artifact
   that **no persona in the entire library** consumes. There is no team
   composition that would silence the warning. The user is told to fix
   something they cannot fix.

Observed 2026-05-01 with the 5-core-personas team:

```
🟡 Team coherence: 3 orphan produces — produced types with no consumer on the team.
• Persona 'developer' produces type 'dev-decision' but no persona on the team consumes it.
• Persona 'team-lead' produces type 'merge-summary' but no persona on the team consumes it.
• Persona 'tech-qa' produces type 'test-suite' but no persona on the team consumes it.
```

User reported these are "warnings that don't make sense" — and they are
correct. `dev-decision`, `merge-summary`, and `test-suite` are produced
**only** by `developer`, `team-lead`, and `tech-qa` respectively. Grep
across the library shows no persona declares `consumes` on any of the
three. They are terminal outputs (consumed by humans, git history, the
test runner, downstream tooling), not by another persona's prompt.

The validator already has the data to distinguish the two cases — it
builds a `library_producers` map per artifact during
`validate_contract_graph()`. It does **not** build a `library_consumers`
map. Adding that, and using it to filter the orphan-produces output, is
the fix.

## Goal

The team-coherence indicator only shows the user warnings they can act
on. Library-wide terminal outputs are recognized as such and either
suppressed entirely or rendered as informational, not as a yellow
warning that implies the user must do something.

## Scope

### In Scope

- **Validator (`foundry_app/services/validator.py:validate_contract_graph`)**:
  - Build a `library_consumers: dict[str, list[str]]` map alongside the
    existing `library_producers` map.
  - For each candidate orphan-produces pair `(artifact, producer_id)`,
    check whether `library_consumers[artifact]` is non-empty.
    - **Empty** (no library persona consumes it) → suppress the warning.
      This is a library-level terminal output; the user cannot fix it.
    - **Non-empty** but missing on the current team → keep the warning.
      Adding one of those personas would close the graph; the warning
      is actionable.
  - The change is additive to the existing logic; the **missing-producer**
    error path is unchanged.
- **Tests**:
  - Library-fixture test: a team produces an artifact with at least one
    library-side consumer that's not on the team → orphan-produces
    warning fires (regression — preserve current behavior).
  - Library-fixture test: a team produces an artifact with **no library
    consumer anywhere** → no orphan-produces warning emitted.
  - Real-library regression: with the 5 core personas, no orphan-produces
    warnings remain (because `dev-decision`, `merge-summary`, `test-suite`
    are all library-wide orphans).

### Out of Scope

- Adding `consumes:` declarations to any persona to "fix" the orphans
  inside the library. (Some of these may be legitimately terminal; the
  decision belongs to a separate library-design bean if needed.)
- Changing the persona-page rendering shape — BEAN-286's verbatim-message
  display stays as-is. With this change, the user simply sees fewer
  noisy lines.
- Rewording the orphan-produces message itself.

## Acceptance Criteria

- [x] (test:tests/test_validator.py) `validate_contract_graph` does NOT
      emit an orphan-produces warning for an artifact whose library-wide
      consumer set is empty.
- [x] (test:tests/test_validator.py) `validate_contract_graph` DOES emit
      an orphan-produces warning for an artifact whose library-wide
      consumer set is non-empty but the consumer is not on the team
      (regression — current actionable behavior preserved).
- [x] (test:tests/test_validator.py) With the real `ai-team-library/`
      indexed and the 5 core personas (architect, ba, developer,
      team-lead, tech-qa), `validate_contract_graph` emits zero
      orphan-produces warnings.
- [x] (test:tests/test_persona_page.py) The team-coherence indicator
      shows 🟢 ("all consumes satisfied") for the 5 core personas
      against the real library — i.e., the user-visible payoff lands.
- [x] (test:tests/) All tests pass (`uv run pytest`).
- [x] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Validator — `library_consumers` map + orphan-produces filter | developer | — | Done |
| 2 | Orphan-produces filter coverage + real-library regression | tech-qa | 01 | Done |

> Skipped: BA (default), Architect (default). Pure validator-correctness
> fix; no user-facing wording, no new abstractions, no cross-module
> design.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| `ai/beans/BEAN-289-.../bean.md` | 58 |
| `.../tasks/01-developer-validator-library-consumers-filter.md` | 59 |
| `.../tasks/02-tech-qa-orphan-produces-filter-coverage.md` | 78 |
| `ai/beans/_index.md` | 2 |
| `foundry_app/services/validator.py` | 20 |
| `tests/test_persona_page.py` | 38 |
| `tests/test_validator.py` | 93 |

## Notes

**The validator already has half the data.** `validate_contract_graph`
builds `library_producers` for the missing-producer error path's
"Producers in library: …" suggestion. The mirror map for consumers is
absent. Adding it is a few lines.

**Reported by user 2026-05-01.** "These warnings don't make any sense
to me … if I choose Developer, it means I want a developer on the
team. I'm not sure why that warning is there and how to mitigate it."
The complaint is correct: there is no mitigation available at the user
level for these three artifact types.

**Companion to BEAN-286.** That bean made the messages visible; this
bean filters out the ones that aren't actionable. Together they finish
the work of making the indicator useful.

**No library-side fix.** Three artifact types (`dev-decision`,
`merge-summary`, `test-suite`) are designed to be terminal — they go
to humans, git, or test runners, not to another persona. Adding a
synthetic consumer just to silence the warning would be cargo-culting.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Validator — `library_consumers` map + orphan-produces filter | developer | 1m | 899,431 | 5,321 | $1.90 |
| 2 | Orphan-produces filter coverage + real-library regression | tech-qa | 2m | 1,937,413 | 9,891 | $4.06 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 3m |
| **Total Tokens In** | 2,836,844 |
| **Total Tokens Out** | 15,212 |
| **Total Cost** | $5.96 |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | developer, tech-qa |
| **Bounces** | 0 (Tech-QA → Developer kicks) |
| **Scope changes** | 0 (in-flight scope edits) |
| **Contract violations** | 0 (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
| **Dispatch mode** | in-process |