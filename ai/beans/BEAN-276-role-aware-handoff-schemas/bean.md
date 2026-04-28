# BEAN-276: Role-Aware Handoff Schemas

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-276 |
| **Status** | Unapproved |
| **Priority** | Medium |
| **Created** | 2026-04-28 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

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
| 1 | | | | Pending |

> Tasks populated by Team-Lead. Likely wave: Architect (registry pair-fields design), Developer (skill update + index file + example handoff), Tech-QA (validation paths).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Depends on BEAN-273.** Cannot land before persona contracts and the artifact-type registry exist.

**Empty `ai/handoffs/` is a real signal.** If the directory is still empty after this bean lands, the typed format is too heavyweight or the dispatch flow doesn't actually require handoffs. Revisit the requirement — maybe `/spawn-task` (BEAN-270) should auto-invoke `/handoff` at task completion when a downstream consumer exists.

**Per BEAN-249**: command file ≤30 lines, skill file is canonical. Comply from day one.

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
