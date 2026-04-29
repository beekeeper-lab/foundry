# BEAN-271: Tier Library Personas — `core/` vs `extended/`

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-271 |
| **Status** | Deferred |
| **Priority** | High |
| **Created** | 2026-04-28 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

`ai-team-library/personas/` ships 24 personas. Foundry's own team uses 5 (team-lead, ba, architect, developer, tech-qa). The other 19 (mobile-developer, sales-engineer, financial-operations, etc.) have no orchestration wiring in any command or skill — they sit on the bench but the bench has no rules.

Anthropic guidance: "stable pool of specialist workers." 24 ungrounded personas is a costume rack, not a stable pool. Generated projects inherit all 24 as available bench whether the workflow needs them or not, which dilutes the "narrow specialist boundaries" principle.

BEAN-269 made the available-bench model explicit in CLAUDE.md, but the library still presents all 24 personas with no tiering signal.

## Goal

Library personas are split into two tiers on disk:

- **`ai-team-library/personas/core/`** — the 5 personas that participate in every team's orchestration: team-lead, ba, architect, developer, tech-qa.
- **`ai-team-library/personas/extended/`** — the 19 specialist personas, opt-in per composition.

The compiler emits the core 5 by default. Extended personas appear in generated projects only if explicitly named in `composition.yml`. The wizard UI groups them visibly into the same two tiers.

Clean break: existing compositions that name an extended persona without a `tier:` indicator must be updated by the user (or the compiler errors with a clear message naming the persona's new path). ClaudeKit submodule consumers re-pull and adapt — this is the agreed approach.

## Scope

### In Scope

- File reorg: move 5 persona dirs into `ai-team-library/personas/core/`; move 19 into `ai-team-library/personas/extended/`.
- Update `foundry_app/services/library_indexer.py` to scan both subdirectories and tag each `PersonaInfo` with `tier: "core" | "extended"`.
- Update `PersonaInfo` Pydantic model in `foundry_app/core/models.py` to carry the tier field.
- Update `foundry_app/services/compiler.py` so the default composition includes only `tier=core`; extended personas require explicit naming in `composition.yml`.
- Update wizard's persona selection page (`foundry_app/ui/screens/builder/wizard_pages/`) to render two collapsible groups labeled "Core team" and "Extended specialists" with a brief explainer.
- Update `ai-team-library/README.md`'s persona table to mark the tier of each.
- Update `ai-team-library/workflows/foundry-pipeline.md` and `task-taxonomy.md` to reflect the tiering.
- Update example compositions in `examples/*.yml` — verify each still selects the personas it intends.
- Tests: indexer reports tier; compiler defaults to core only; explicit extended-persona selection still works; clear error message when an extended persona is referenced but the move is not done.

### Out of Scope

- Renaming, merging, or removing personas (no content edits to persona files themselves).
- Backwards-compatibility shim (clean break per agreed plan).
- Activation rules for extended personas (BEAN-257 is Done; this bean preserves those).
- Per-persona expertise filtering (BEAN-259 is the right home for that).

## Acceptance Criteria

- [ ] `ai-team-library/personas/core/` contains exactly: team-lead, ba, architect, developer, tech-qa.
- [ ] `ai-team-library/personas/extended/` contains the remaining 19 personas.
- [ ] `PersonaInfo.tier` is set correctly by the indexer for every persona.
- [ ] Default composition (no `personas:` block) generates a project containing only the core 5.
- [ ] Composition with `personas: [extended/security-engineer, ...]` (or whatever final ref-syntax we pick) generates the right project.
- [ ] Wizard UI groups personas into two clearly-labeled tiers.
- [ ] Library README reflects the tiering.
- [ ] All tests pass (`uv run pytest`); existing tests updated where they reference old paths.
- [ ] Lint clean (`uv run ruff check foundry_app/`).
- [ ] At least one example composition exercises the extended tier end-to-end.

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks populated by Team-Lead during decomposition. Likely wave: Architect (decide composition.yml ref-syntax for extended personas, ADR), Developer (file moves + indexer + model + compiler + wizard), Tech-QA (regression tests, example regen).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Clean break decision.** Confirmed 2026-04-28: ClaudeKit submodule consumers will re-pull and adapt. No backwards-compatibility shim. The compiler should error loudly with a remediation hint when it sees an old-style persona reference.

**Architect required.** `composition.yml` ref-syntax for extended personas is a small contract decision — should it be `extended/security-engineer` or `security-engineer` with the loader scanning both? ADR before implementation.

**Coordinate with BEAN-259.** That bean filters expertise per persona; this bean tiers personas. Both contribute to "narrow specialist boundaries." Land in either order; BEAN-259 may want this bean's tier metadata.

**Coordinate with BEAN-273/274.** Contract graph validator must understand tiering — extended personas may produce/consume types that core personas don't.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
