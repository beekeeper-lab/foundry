# BEAN-290: User-Friendly Validator Error and Warning Messages

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-290 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-05-01 |
| **Started** | 2026-05-01 16:31 |
| **Completed** | 2026-05-01 16:48 |
| **Duration** | 1603h 40m |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | BEAN-286, BEAN-289 |

## Problem Statement

After BEAN-286 surfaced validator messages verbatim in the wizard's
team-coherence indicator (and BEAN-289 filtered out the unactionable
ones), what's left is *visible*, *actionable*, and *unreadable*. The
messages are written in the validator's internal vocabulary, not the
user's:

Observed 2026-05-01 — example A, persona-page coherence indicator
with `developer + ba + tech-qa` selected:

```
🔴 Team coherence: 2 missing producers — add producers or remove consumers.
• Missing producer for type 'adr'. Consumed by: developer, team-lead.
  Producers in library: architect. Add one to your team.
• Missing producer for type 'design-spec'. Consumed by: developer,
  team-lead, tech-qa. Producers in library: architect. Add one to
  your team.
```

Observed 2026-05-01 — example B, generation-failure banner with a
posture-incompatible hook pack selected:

```
Generation failed: Validation failed: Hook pack 'compliance-gate'
declares posture 'baseline' as incompatible (Posture Compatibility
table says Included: No). Remove the pack, lower enforcement, or
raise the composition's posture.
```

Both surfaces have the same disease, expressed differently:

- The persona-page version leaks **graph vocabulary** ("producer",
  "consumer", "type 'adr'").
- The generation-banner version **double-wraps the prefix**
  ("Generation failed: Validation failed:") and **leaks an internal
  data-structure name** ("Posture Compatibility table says Included:
  No"). The user has no idea what a Posture Compatibility table is
  — it's a section heading inside a hook pack's metadata file, not
  a concept the wizard ever exposes.

User feedback: *"They're not human readable. We don't want to say
things like 'missing producer of type ADR consumed by developer,
team-lead.' I want a good, friendly error message in English that
tells them what the issue is and what they can do to mitigate it."*

The validator vocabulary leaking through:

- **"producer"** / **"consumer"** — these are graph-theory terms.
  The user thinks in personas, not graph nodes.
- **"type 'adr'"** — internal artifact identifier; the user knows
  this concept as "Architecture Decision Records".
- **"orphan-produces"** — internal code; the message form
  ("Persona 'X' produces type 'Y' but no persona on the team
  consumes it") leaks the internal model.

The validator's `ValidationMessage` is the right boundary to fix
this at — the messages are constructed once, then surfaced verbatim
by every UI that renders them (currently the persona-page coherence
indicator; in the future, hook-safety page, review page, generation
errors).

## Goal

Every validator message that reaches the UI reads as something a
non-developer would write. Each message answers two questions in
plain English:

1. **What is wrong?** — described in the user's vocabulary
   (persona names, recognizable artifact labels, observable
   symptoms — not "producer", "type", "graph").
2. **What can I do?** — a concrete action the user can take from
   inside the wizard (add a persona, remove a persona, switch
   strictness, etc.). If no action is available, the message must
   say *that* clearly rather than leaving the user to infer it.

The message **code** is unchanged (downstream tests and telemetry
key on it). Only the **message text** changes.

## Scope

### In Scope

- **Validator messages with UI surface area** in
  `foundry_app/services/validator.py`. At minimum:
  - `missing-producer` (ERROR) — currently visible, primary
    complaint.
  - `orphan-produces` (WARNING) — currently visible, secondary.
  - `no-personas` (WARNING)
  - `no-expertise` (WARNING)
  - `duplicate-persona`, `duplicate-expertise` (ERROR)
  - `missing-persona`, `persona-no-persona-md`,
    `missing-expertise`, `expertise-no-files`,
    `missing-hook-pack` (ERROR — library-data integrity)
  - `hook-pack-conflict` (ERROR)
  - `hook-pack-posture-incompatible` (ERROR)
- **Artifact-type display labels** — translate internal artifact
  identifiers into recognizable names where they appear in
  messages. (`adr` → "Architecture Decision Records (ADRs)",
  `user-story` → "user stories", `test-suite` → "test suite", etc.)
  - The mapping lives next to the validator (or in
    `foundry_app/core/`) so the same labels are reused across
    surfaces. Source of truth: artifact-type metadata in
    `ai-team-library/contracts/`. If a description / human-name
    field exists there, prefer it over a hand-coded map.
- **Persona display names** — use the persona's display name (e.g.,
  "Software Architect") rather than the id ("architect") in user-
  facing prose, where the `PersonaInfo` carries one.
- **Tone & shape guidance** captured as a docstring or short
  reference doc:
  - Speak to the user, not about them.
  - Lead with the symptom, follow with the fix.
  - One sentence preferred; two if the fix needs detail.
  - No internal jargon (no "producer", "consumer", "graph",
    "type", "orphan", "node").
  - Name the actionable persona by display name.
- **Tests** that bind tone / vocabulary by **negative assertions**
  on the message text (e.g., `"producer" not in msg.message`),
  plus positive assertions that the user-facing nouns appear
  (e.g., `"Architecture Decision" in msg.message`).
- **`_coherence_label` summary line** in
  `foundry_app/ui/screens/builder/wizard_pages/persona_page.py`
  — the headline ("2 missing producers — add producers or remove
  consumers.") inherits the same vocabulary cleanup.
- **Generation-failure banner wrapping** — the BEAN-287 sticky
  banner currently double-prefixes validator messages with
  `"Generation failed: Validation failed: …"`. Drop the inner
  `"Validation failed:"` (the banner already conveys *that
  something failed*) and let the cleaned validator message read
  on its own. Find the wrapping site (likely the generator
  service or the progress screen) and stop adding the redundant
  prefix.
- **Data-structure leakage in messages** — `"(Posture
  Compatibility table says Included: No)"` and similar
  parentheticals reference internal hook-pack-metadata sections
  the user never sees. Strip those clauses from the user-facing
  text. The same information can land in the log line for
  developers; the banner gets a clean statement of *what is
  wrong* and *what to do*.

### Out of Scope

- Internationalization / i18n. Messages stay English-only; the
  refactor only sets up a structure that *could* be localized
  later.
- Changing message **codes** or `ValidationMessage` shape — only
  the human-readable `.message` text changes.
- Changing **severity levels** — what's an error stays an error;
  what's a warning stays a warning.
- Re-surfacing previously suppressed messages (BEAN-289's
  library-level filter is preserved).
- Adding tooltips, "learn more" links, or any new UI affordance
  — purely a message-content bean.
- Generator/runtime errors outside `validator.py` (those are a
  separate UX pass).

## Acceptance Criteria

- [x] (test:tests/test_validator.py) Every UI-surfaced validator
      message asserts:
        - the internal terms `producer`, `consumer`, `orphan`,
          `node`, `graph` do NOT appear in `.message`;
        - the persona display name (or persona id when no display
          name exists) DOES appear when a persona is named;
        - the artifact's recognizable label DOES appear when an
          artifact is named (e.g., "Architecture Decision" for
          `adr`).
- [x] (test:tests/test_validator.py) `missing-producer` includes
      a concrete action ("Add the Software Architect to your team"
      or equivalent) AND names the affected team members in plain
      English ("your developer and team-lead need …").
- [x] (test:tests/test_validator.py) `orphan-produces` reads as
      a friendly suggestion, not a graph diagnostic. The fix
      direction (add a consumer persona) is named with a display
      name, not a persona id.
- [x] (test:tests/test_persona_page.py) The coherence summary
      headline drops "producers"/"consumers" in favor of
      user-vocabulary nouns ("missing roles", "outputs no one is
      using", or similar — exact wording chosen during BA
      activation).
- [x] (test:tests/) The generation-failure banner no longer
      double-prefixes validator messages with `"Validation
      failed:"`. A test against the banner-text construction site
      asserts the banner copy starts with the cleaned validator
      message (or a single, user-vocabulary lead-in like
      `"Can't generate yet — "`), not with `"Validation failed:
      …"`.
- [x] (test:tests/test_validator.py) The
      `hook-pack-posture-incompatible` message text does NOT
      contain the substring `"Posture Compatibility table"` or
      `"Included: No"`. Equivalent assertions on any other
      data-structure section names that currently leak through.
- [x] (test:tests/test_validator.py) Existing message-code-based
      assertions still pass — codes are unchanged.
- [x] (test:tests/) All tests pass (`uv run pytest`).
- [x] (lint:foundry_app/) Lint clean (`uv run ruff check
      foundry_app/`).
- [x] (manual) Visually verify in the wizard with a deliberately-
      broken team (e.g., `developer + tech-qa` only) that every
      surfaced message reads like English a non-engineer would
      write. *(Headless environment — text-based proof recorded at
      `ai/outputs/tech-qa/BEAN-290-manual-verification.md` with
      verbatim message samples; project owner asked to confirm via
      live launch.)*

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Canonical phrasing for validator messages | ba | — | Done |
| 2 | Wire canonical messages into validator + UI | developer | 1 | Done |
| 3 | Vocabulary tests + regression sweep | tech-qa | 2 | Done |

> Skipped: Architect (default — no new abstractions; `ValidationMessage`
> shape is preserved).

## Changes

| File | Lines |
|------|-------|
| `foundry_app/services/artifact_labels.py` | +90 |
| `foundry_app/services/validator.py` | +112 |
| `foundry_app/ui/generation_worker.py` | +10 |
| `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` | +17 |
| `foundry_app/ui/screens/generation_progress.py` | +2 |
| `tests/test_validator.py` | +293 |
| `tests/test_generation_progress.py` | +86 |
| `tests/test_persona_page.py` | +60 |
| `tests/test_generator.py` | +6 |
| `ai/outputs/ba/BEAN-290-validator-message-phrasing.md` | +180 |
| `ai/outputs/tech-qa/BEAN-290-manual-verification.md` | +119 |
| `ai/beans/BEAN-290-user-friendly-validator-messages/` | +296 (bean + tasks) |

## Notes

**This is a wording bean, not an architecture bean.** The
validator already emits structured messages keyed by `code`. The
fix is content-only: replace the `.message` strings with prose a
user would understand. The `code` stays stable so downstream
tests and telemetry are unaffected.

**Why BA is on the wave.** Each message has to be rewritten with
care — the wording is the deliverable. BA owns canonical phrasing
for each code in a small reference table, then Developer wires
that table into the validator.

**Display labels for artifact types.** Investigate
`ai-team-library/contracts/` first — the artifact-type registry
may already carry human-readable names. If so, surface them via
the existing `LibraryIndex` and use them in messages. If not,
add a small mapping next to the validator (and a follow-up
backlog bean to push the labels into the library data).

**Reported by user 2026-05-01** while testing BEAN-289's payoff.
The fix landed (yellow → green for the 5 core personas), and the
next layer of UX showed up immediately: when the indicator IS
red, the messages it surfaces are unreadable. Same surface, next
quality bar.

**Two surfaces, one fix.** The user hit the same problem on a
second surface within minutes — the generation-failure banner
(BEAN-287) showed `"Generation failed: Validation failed: Hook
pack 'compliance-gate' declares posture 'baseline' as incompatible
(Posture Compatibility table says Included: No)…"`. Same root
cause (validator messages constructed in internal vocabulary,
surfaced verbatim) plus two new sins (the banner double-prefixing
and the parenthetical leaking an internal-only metadata section
name). The fix is the same — clean up the validator message text
at the source — plus drop the redundant `"Validation failed:"`
prefix at the banner-wrapping site.

**Coverage expectation.** The bean asks for vocabulary tests on
**every** UI-surfaced code, not just the two visible in the
screenshot. The bug is structural (validator vocabulary leaks
through unfiltered) and a one-off pass on the loud cases would
leave the same problem latent in the rarely-triggered ones.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Canonical phrasing for validator messages | ba | 2m | 1,717,125 | 16,323 | $4.29 |
| 2 | Wire canonical messages into validator + UI | developer | 8m | 12,515,731 | 36,592 | $22.75 |
| 3 | Vocabulary tests + regression sweep | tech-qa | 3m | 6,077,996 | 16,648 | $10.88 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 13m |
| **Total Tokens In** | 20,310,852 |
| **Total Tokens Out** | 69,563 |
| **Total Cost** | $37.92 |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | ba, developer, tech-qa |
| **Bounces** | 0 (Tech-QA → Developer kicks) |
| **Scope changes** | 0 (in-flight scope edits) |
| **Contract violations** | 0 (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
| **Dispatch mode** | in-process |