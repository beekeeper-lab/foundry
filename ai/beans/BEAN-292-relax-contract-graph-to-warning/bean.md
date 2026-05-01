# BEAN-292: Relax Contract-Graph "Missing Producer" from Error to Warning

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-292 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-05-01 |
| **Started** | 2026-05-01 17:54 |
| **Completed** | 2026-05-01 18:11 |
| **Duration** | 1605h 4m |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | BEAN-290 |

## Problem Statement

The contract-graph validator currently emits `missing-producer` as an
**ERROR**, which fails `ValidationResult.is_valid` and blocks generation.
This forces every team composition to include the full set of "core"
personas (BA, Architect, Team Lead) any time `developer` or `tech-qa` is
selected, because those personas declare `consumes: [user-story,
acceptance-criteria, adr, design-spec]`.

Reported 2026-05-01: the user wants to compose a generalist team of just
`developer + tech-qa` (the "small startup" pattern: a coder and a tester
who absorb the BA / Architect roles informally). The wizard refuses,
surfacing four red errors of the form *"Your Developer needs Architecture
Decision Records (ADRs), but no one on your team can supply it. Add the
Architect to your team."* The user has to add every core persona to even
attempt generation.

User feedback verbatim: *"I should be able to go with just a developer
and a tester, and then they would handle all the other tasks. That would
be like saying that I don't need a specialist, I just need a generalist
in those areas. So these error messages that we've tightly coupled these
together using one of them requires all of the others, we need to remove
that."*

The conceptual error in the current model is treating `consumes` as a
**hard prerequisite**. `consumes` should describe *what this persona
collaborates on when those teammates are present*, not *what the team
must include for this persona to function*. When a producer is absent,
the consumer absorbs that responsibility (or skips it) — it does not
become unable to operate.

The current wording (post-BEAN-290) reads as a friendly suggestion ("Add
the Architect to your team") but the underlying severity is still ERROR,
which is why the wizard blocks. The fix is to align the severity with
the message's *advisory* tone.

## Goal

A team of any subset of personas — including `developer + tech-qa`
alone — validates as `is_valid=True` in standard mode and proceeds to
generation. The persona-page coherence indicator still surfaces "your
team would benefit from..." messages so the user sees what specialists
*would* contribute, but those messages are advisory (yellow), not
blocking (red). Users who want the hard gate can opt into `strict`
strictness, where the existing `_apply_strictness` promotion lifts
warnings back to errors.

## Scope

### In Scope

- **Demote `missing-producer` severity** in
  `foundry_app/services/validator.py::validate_contract_graph` from
  `Severity.ERROR` to `Severity.WARNING`.
- **Document the rationale** in the validator docstring so future
  refactors don't regress this. Add a one-paragraph "Why warning, not
  error" note explaining the generalist-team principle.
- **Update existing tests** in `tests/test_validator.py` that assert
  ERROR severity for `missing-producer` to expect WARNING. Strictness
  tests should already pass — `_apply_strictness` STRICT mode promotes
  warnings to errors, so users who opt in still get the hard gate.
- **Update the persona-page coherence indicator** in
  `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` so that
  a team with only missing-producer messages renders as 🟡 (yellow,
  advisory), not 🔴 (red, blocking). The headline copy should adapt:
  the existing yellow headline talks about "unused outputs"; we likely
  need a third headline state OR a unified "team check" copy that works
  for both missing-supplier and unused-output messages.
- **Update the green/yellow/red precedence rule** so red is reserved
  for genuine ERRORs (currently only `hook-pack-conflict`,
  `hook-pack-posture-incompatible`, `missing-persona`,
  `missing-expertise`, `missing-hook-pack`, `duplicate-persona`,
  `duplicate-expertise` after this change).
- **Verify generation succeeds end-to-end** for `developer + tech-qa`
  with no other team members. The generator pipeline already calls
  `validate_contract_graph` and gates on `is_valid` (see BEAN-274's
  pipeline integration); demoting the severity should let the pipeline
  proceed.

### Out of Scope

- Rewording the message text — BEAN-290 already friendlified it; the
  current text reads correctly as an advisory.
- Changing severities for other codes (`orphan-produces` stays WARNING;
  `hook-pack-*` errors stay ERROR; `missing-persona/expertise/hook-pack`
  stay ERROR — those are genuine unrecoverable errors, not collaboration
  gaps).
- Removing `consumes` declarations from any persona's `contracts.yml`.
  The data model stays the same; only the validator's enforcement
  posture changes.
- Reworking the contract-graph data model (e.g., adding a
  `requires_vs_collaborates` distinction per artifact). If we ever need
  hard requirements, we can introduce them in a separate, narrower
  bean.
- Adding a per-composition opt-in to "treat missing-producer as error
  again." `strict` strictness already provides that lever.

## Acceptance Criteria

- [ ] (test:tests/test_validator.py) `missing-producer` messages have
      `severity == Severity.WARNING` in standard mode (update the
      existing `test_missing_producer_severity_is_error` test — likely
      rename to `_is_warning`).
- [ ] (test:tests/test_validator.py) `missing-producer` messages have
      `severity == Severity.ERROR` after `_apply_strictness` is applied
      with `Strictness.STRICT` (the existing strict-mode test should
      already cover this; update assertions if needed).
- [ ] (test:tests/test_validator.py) A `validate_contract_graph` result
      whose only messages are `missing-producer` warnings has
      `result.is_valid == True`.
- [ ] (test:tests/) End-to-end: a generation pipeline run with team
      `developer + tech-qa` only, in standard mode, completes
      successfully (no `is_valid` gate trip).
- [ ] (test:tests/test_persona_page.py) The persona-page coherence
      indicator renders 🟡 (not 🔴) when the only validator output is
      missing-producer messages.
- [ ] (test:tests/test_persona_page.py) The 🔴 state is still reachable
      for genuine ERRORs (e.g., a team that triggers
      `hook-pack-conflict`).
- [ ] (file-contains:foundry_app/services/validator.py::generalist) The
      `validate_contract_graph` docstring documents the
      "warning-not-error" rationale (search for "generalist" or similar
      keyword).
- [ ] (test:tests/) All tests pass (`uv run pytest`).
- [ ] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`).
- [ ] (manual) Launch the wizard, select only `developer + tech-qa`,
      navigate through all wizard pages, click Generate, and confirm
      generation completes without an "is_valid" block. The persona
      page should show a yellow coherence indicator with the friendly
      missing-supplier messages, but Next is enabled and Generate
      succeeds.

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Demote missing-producer to WARNING and update persona-page indicator | developer | — | Done |
| 2 | Regression sweep + end-to-end developer+tech-qa generation | tech-qa | 01 | Done |

> Skipped: BA (default), Architect (default)
> Wave: **Developer → Tech-QA**. Architect not required — this is a
> data-flow severity change, not a model change. BA not required — the
> wording is already settled by BEAN-290.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**Why High priority.** The current behavior makes the wizard unusable
for the generalist composition pattern, which is the natural starting
point for small projects and prototypes. The user discovered this on
the first realistic compose attempt after BEAN-290 shipped.

**Strictness lever preserves the hard gate.** Users who genuinely want
to require the full team can set `strictness: strict` in the
composition (or via the wizard's strictness selector). The existing
`_apply_strictness` function lifts WARNING → ERROR in strict mode, so
nothing is taken away — the default just shifts from "block" to
"advise."

**Relationship to BEAN-290.** BEAN-290 fixed the *wording* of these
messages. This bean fixes the *severity*. Together they implement the
intended UX: friendly, actionable suggestions that don't gate
generation by default.

**Relationship to BEAN-289.** BEAN-289 suppressed unactionable
orphan-produces warnings (artifacts no library persona consumes). The
present bean's relaxation is a different axis — those messages were
unactionable; missing-producer messages *are* actionable, but the
action is optional, not mandatory.

**Coherence-indicator state model after this change.**

| State | Trigger |
|-------|---------|
| 🟢 green | No errors, no warnings |
| 🟡 yellow | Any warnings (missing-producer, orphan-produces, duplicate, etc.) and no errors |
| 🔴 red | Any of: `hook-pack-conflict`, `hook-pack-posture-incompatible`, `missing-persona`, `missing-expertise`, `missing-hook-pack` |

The Developer needs to confirm this precedence model with the team
before implementing the indicator update.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Demote missing-producer to WARNING and update persona-page indicator | developer | 7m | 1,264,254 | 10,446 | $2.92 |
| 2 | Regression sweep + end-to-end developer+tech-qa generation | tech-qa | 5m | 514,930 | 6,826 | $1.32 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 12m |
| **Total Tokens In** | 1,779,184 |
| **Total Tokens Out** | 17,272 |
| **Total Cost** | $4.24 |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | developer, tech-qa |
| **Bounces** | 0 (Tech-QA → Developer kicks) |
| **Scope changes** | 0 (in-flight scope edits) |
| **Contract violations** | 0 (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
| **Dispatch mode** | in-process |