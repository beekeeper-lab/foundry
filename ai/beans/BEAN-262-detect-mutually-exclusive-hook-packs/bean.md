# BEAN-262: Detect Mutually-Exclusive Hook Pack Pairs at Generation Time

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-262 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 18:44 |
| **Completed** | 2026-04-17 18:48 |
| **Duration** | 1269h 41m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

External review (2026-04-17): "Azure hooks cancel each other.
`az-limited-ops` and `az-read-only` are both enforcing. `settings.json`
blocks all `create|delete|update|start|stop|restart|purge|set` — which
neutralizes every deploy op `az-limited-ops` is supposed to allow. The
two packs are mutually exclusive; enabling both = read-only."

The generator today composes hook packs from whatever the user selected
without checking whether any pair is contradictory. The result is silent
misconfiguration that only shows up when the hook starts blocking
everything.

## Goal

The generator rejects (or warns loudly about) compositions that enable
mutually-exclusive hook pack pairs. Hook packs that semantically conflict
are annotated with a `conflicts_with:` declaration, and the safety
writer verifies no conflict is active at emit time.

## Scope

### In Scope
- Add a `conflicts_with:` or similar machine-readable declaration to
  affected hook packs in `ai-team-library/claude/hooks/<pack>.md`.
- Start with the known pair: `az-read-only` ⇄ `az-limited-ops`. Audit
  other packs for similar conflicts.
- Update `foundry_app/services/safety_writer.py` (or equivalent) to
  read declared conflicts and reject compositions that include both
  sides of any conflict pair — or, at minimum, surface a validation
  error.
- Tests: a composition that includes both conflicting packs fails
  validation (or produces a clear warning, depending on policy).

### Out of Scope
- Dynamic runtime conflict detection.
- Rewriting hook pack semantics.
- General N-way conflict graphs (pair-level is sufficient for now).

## Acceptance Criteria

- [ ] Mutually-exclusive hook pack pairs are declared in the hook pack
      metadata.
- [ ] The generator surfaces a validation error when a composition
      enables both sides of a declared conflict.
- [ ] A composition including `az-read-only` + `az-limited-ops` fails
      validation with a clear message.
- [ ] Tests cover the conflict-detection path.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design `conflicts_with` schema + ADR | architect | — | Done |
| 2 | Declare conflicts on az/aws pairs + detect in validator | developer | 1 | Done |
| 3 | Tests, lint, acceptance-criteria verification | tech-qa | 2 | Done |

> Skipped: BA (default — no user-facing behavior, no stakeholder trade-off)

## Changes

| File | Lines |
|------|-------|
| `ai/context/decisions.md` | +ADR-004 |
| `ai-team-library/claude/hooks/az-read-only.md` | +4 |
| `ai-team-library/claude/hooks/az-limited-ops.md` | +4 |
| `ai-team-library/claude/hooks/aws-read-only.md` | +4 |
| `ai-team-library/claude/hooks/aws-limited-ops.md` | +4 |
| `foundry_app/core/models.py` | +4 |
| `foundry_app/services/library_indexer.py` | +33 |
| `foundry_app/services/validator.py` | +47 |
| `tests/test_validator.py` | +119 |
| `tests/test_library_indexer.py` | +64 |

## Notes

**Source.** External review (2026-04-17).

**Architect warranted.** Conflict declaration is a schema change to the
hook pack metadata — ADR-worthy.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Design `conflicts_with` schema + ADR | architect | — | — | — | — |
| 2 | Declare conflicts on az/aws pairs + detect in validator | developer | — | — | — | — |
| 3 | Tests, lint, acceptance-criteria verification | tech-qa | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 1269h 41m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |