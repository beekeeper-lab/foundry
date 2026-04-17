# BEAN-263: Enforce Pack-Declared Posture Compatibility at Generation Time

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-263 |
| **Status** | In Progress |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 19:28 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

External review (2026-04-17): "Posture vs. hook contradiction.
`posture: baseline`, but `compliance-gate` is enabled + enforcing. Its
own Posture Compatibility table (`compliance-gate.md:27-33`) says
`baseline: No` and 'only active at the regulated posture level.' The
generator ignored the pack's own compatibility matrix."

Hook packs document their posture compatibility in a declarative table,
but the generator does not consult those tables when building
`settings.json`. The result is compositions that violate the pack's
own declared contract.

## Goal

Every hook pack declares its supported posture(s) in a machine-readable
format. The safety writer rejects or downgrades packs that are active
in a posture they declared incompatible with.

## Scope

### In Scope
- Define a canonical `posture_compatibility:` schema in hook pack
  frontmatter or a structured metadata block.
- Migrate existing hook packs to that schema (read the human-readable
  Posture Compatibility table and encode it).
- Update `foundry_app/services/safety_writer.py` to read the compatibility
  metadata and refuse to emit a pack as enforcing in an incompatible
  posture. Policy: surface a validation error, or silently downgrade
  enforcement to advisory — decide in the bean.
- Tests: a baseline composition with `compliance-gate` fails validation
  (or downgrades) with a clear message.

### Out of Scope
- Rewriting pack semantics.
- Adding new posture levels (BEAN-250 handles posture taxonomy rebalance).

## Acceptance Criteria

- [ ] Hook packs declare their posture compatibility in machine-readable
      metadata.
- [ ] The generator consults that metadata when building
      `settings.json` and refuses (or downgrades) incompatible packs.
- [ ] A baseline composition with `compliance-gate` surfaces a
      validation error or downgrade warning.
- [ ] Tests cover the incompatibility path.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design posture_compatibility schema and integration | Architect | — | Done |
| 2 | Implement parser, validator check, and safety-writer filter | Developer | 1 | Pending |
| 3 | Tests: parser, validator, safety-writer filter; full suite green | Tech-QA | 2 | Pending |

> Skipped: BA (default — criteria unambiguous).

## Decisions

- **Schema location**: the existing `## Posture Compatibility` table in every
  hook pack `.md` is the canonical machine-readable source. A parser in
  `library_indexer.py` reads it into `HookPackInfo.posture_compatibility`.
  No modification of `ai-team-library/` files required — the table format is
  already deterministic (`Posture | Included | Default Mode`).
- **Policy**: surface a **validation error** (`Severity.ERROR`, code
  `hook-pack-posture-incompatible`) via `validator.py` when a pack whose
  compatibility row declares `Included: No` is active in the selected
  posture. `safety_writer.py` additionally skips the pack at emit time as a
  defensive fallback (so malformed flows surface a clear warning rather than
  producing a contradictory `settings.json`).
- **Interpretation**: `Yes`, `Optional`, and `Yes (...)` all count as
  compatible. Only a literal `No` triggers the error.

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Source.** External review (2026-04-17).

**Depends on.** Should land after or alongside BEAN-250 (posture taxonomy
rebalance) so the schema is stable before encoding per-pack data.

**Architect warranted.** Metadata schema decision is cross-cutting.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Design posture_compatibility schema and integration | Architect | < 1m | 494,391 | 0 | $0.83 |
| 2 | Implement parser, validator check, and safety-writer filter | Developer | — | — | — | — |
| 3 | Tests: parser, validator, safety-writer filter; full suite green | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |