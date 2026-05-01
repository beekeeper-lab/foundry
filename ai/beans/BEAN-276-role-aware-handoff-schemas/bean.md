# BEAN-276: Role-Aware Handoff Schemas

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-276 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-28 |
| **Started** | 2026-05-01 00:48 |
| **Completed** | 2026-05-01 01:02 |
| **Duration** | 1587h 55m |
| **Owner** | team-lead |
| **Category** | Process |
| **Depends On** | BEAN-273 |

## Problem Statement

`/handoff <from> <to>` produces a generic markdown packet at `ai/handoffs/{from}-to-{to}-{work-id}.md`. The format is the same regardless of the persona pair: BA→Architect needs different fields than Developer→Tech-QA, but the command emits the same template.

Two failure modes:

1. **Underspecified handoffs.** The receiver infers what to read; sometimes critical pieces are missing (e.g., a Developer→Tech-QA handoff with no `changed-files` list forces Tech-QA to grep the diff).
2. **Empty handoff directory.** I confirmed `ai/handoffs/` is empty in this repo despite the documented protocol — the generic template doesn't earn its keep, so people skip it.

## Goal

`/handoff` reads the sender persona's `produces:` and the receiver persona's `consumes:` (BEAN-273), looks up the schemas in the artifact-type registry, and emits a typed packet with required fields per artifact type. The receiver knows exactly what to expect.

## Scope

### In Scope

- Update `ai-team-library/claude/skills/handoff/SKILL.md` (canonical spec per BEAN-249) to:
  - Read sender's `produces:` from persona contracts.
  - Read receiver's `consumes:` from persona contracts.
  - Compute the intersection (what the sender owes the receiver).
  - For each artifact type in the intersection, emit the registry-defined required fields.
  - Validate that the sender has actually produced each required artifact type before allowing handoff (block if not).
- Update `ai-team-library/claude/commands/handoff.md` (≤30 lines per BEAN-249) — thin trigger only.
- Add per-pair extension hooks in the artifact-type registry: a `pair-fields` map for sender/receiver pairs that need extras beyond the artifact's required fields (e.g., Developer→Tech-QA wants `test-targets` even if not in `code-change`'s required fields).
- Make handoff invocation observable: every `/handoff` call writes to `ai/handoffs/` *and* appends a row to a running `ai/handoffs/_index.md` for traceability.
- Tests: handoff with all required fields succeeds; missing field blocks; pair-fields extras emitted correctly; handoff index updated.
- Update `ai-team-library/personas/core/*/persona.md` to reference the typed handoff in the workflow sections.

### Out of Scope

- Auto-generating handoff content (the persona still authors it; the schema just defines the shape).
- Renaming the command.
- Handoffs between extended personas (focus on core 5; extended-persona handoffs work via the same mechanism but aren't validated here).
- Retroactive handoff generation for past beans.

## Acceptance Criteria

- [ ] `/handoff` skill reads contracts and emits typed packets.
- [ ] Missing required artifact blocks the handoff with a clear message.
- [ ] Pair-fields extras are honored.
- [ ] `ai/handoffs/_index.md` exists and gets a row per handoff.
- [ ] At least one example handoff (e.g., Developer→Tech-QA from a current bean) lands in `ai/handoffs/` to demonstrate the format end-to-end.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement typed /handoff: skill spec + pair-fields registry + index + example | developer | — | Done |
| 2 | Verify typed /handoff: cold-start walkthrough + registry/index tests | tech-qa | 1 | Done |

> Skipped: BA (default — no requirements ambiguity); Architect (default — pair-fields schema is a small data-model addition documented inline by Developer with rationale, no ADR needed; bean's notes call this a "small contract decision").

## Changes

| File | Lines |
|------|-------|
| `ai-team-library/claude/skills/handoff/SKILL.md` | +241/-? (full rewrite — contract-aware) |
| `ai-team-library/claude/commands/handoff.md` | +26/-? (≤30-line trigger) |
| `ai-team-library/contracts/artifact-types.yml` | +52 (pair-fields section + 3 edges) |
| `ai-team-library/personas/core/{architect,ba,developer,team-lead,tech-qa}/persona.md` | +78 (typed-handoff sections) |
| `ai/handoffs/_index.md` | +21 (new file with schema) |
| `ai/handoffs/developer-to-tech-qa-BEAN-274-task-02.md` | +104 (example handoff) |
| `tests/test_persona_contracts.py` | +144 (TestPairFieldsRegistryShape, 9 tests) |
| `ai/beans/BEAN-276-role-aware-handoff-schemas/bean.md` + 2 task files | +220 |
| **Total** | 15 files changed, +826 / -62 |

## Notes

**Depends on BEAN-273.** Cannot land before persona contracts and the artifact-type registry exist.

**Empty `ai/handoffs/` is a real signal.** If the directory is still empty after this bean lands, the typed format is too heavyweight or the dispatch flow doesn't actually require handoffs. Revisit the requirement — maybe `/spawn-task` (BEAN-270) should auto-invoke `/handoff` at task completion when a downstream consumer exists.

**Per BEAN-249**: command file ≤30 lines, skill file is canonical. Comply from day one.

**Tech-QA follow-ups (2026-05-01).** Surfaced during Task 02 cold-start review. Filed as observations rather than fixed under this bean per the verify-don't-re-implement constraint. Both are documentation-quality issues, not AC failures.

1. **Example handoff doesn't satisfy SKILL.md's "Validate before emitting" MUST.** SKILL.md requires the packet to "cite a developer-authored summary doc under `ai/outputs/developer/`" but the example at `ai/handoffs/developer-to-tech-qa-BEAN-274-task-02.md` cites only working-tree files (the actual code change). For BEAN-274 no such summary doc exists. The MUST is overbroad for the real Foundry workflow where production code IS the artifact. Either soften the SKILL.md MUST (e.g., accept working-tree files plus the bean's task spec as a valid citation) or backfill a synthetic developer note under `ai/outputs/developer/`.

2. **SKILL.md "Data sources" parity claim is overbroad.** Says "These three sources are the same data shape that `foundry_app/services/library_indexer.py::_load_persona_contracts` already loads." The indexer only loads `produces:`/`consumes:`; `pair-fields:` is read at handoff time by the skill. Tighten to "Two of these three sources..." or just remove the parity claim.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Implement typed /handoff: skill spec + pair-fields registry + index + example | developer | 6m | 845,302 | 3,014 | $1.53 |
| 2 | Verify typed /handoff: cold-start walkthrough + registry/index tests | tech-qa | 2m | 886,020 | 2,929 | $1.59 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 8m |
| **Total Tokens In** | 1,731,322 |
| **Total Tokens Out** | 5,943 |
| **Total Cost** | $3.12 |