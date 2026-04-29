# BEAN-251: Clarify Agent Permission Scope in Generated Projects

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-251 |
| **Status** | Deferred |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

External review (2026-04-17): generated `settings.local.json` allows `Read(**)`, `Edit(ai/**)`, and `Bash(git push *)`. The `Edit(ai/**)` scope limits the agents to AI-artifact folders, while many skill and agent docs imply the agents *orchestrate full development* — including app code. The mismatch makes the framework's intent ambiguous:

> "If the intention is 'this framework manages planning artifacts, not app code', then say that clearly. If the intention is 'agents will also implement app code', then this permission model is too narrow."

Today neither is explicit. A new user sees docs that sound like end-to-end agent orchestration and a permission set that blocks editing any code outside `ai/`.

## Goal

A generated project states clearly that the AI team manages planning and design artifacts and that a human implements application code. The `settings.local.json` permission model (narrow `Edit(ai/**)`) matches that statement rather than contradicting it.

**Decision (2026-04-17): Stance 1 — Planning-only.** Keep `Edit(ai/**)` as-is; do not expand permissions. Instead, make the intent explicit in the generated CLAUDE.md so there is no mismatch between what the docs imply and what the permissions allow. Paired with BEAN-253.

## Scope

### In Scope
- Add a **Scope** section (1–3 sentences) to the generated `CLAUDE.md` template stating: the AI team produces plans, designs, reviews, docs, and other artifacts under `ai/`; the human initializes and implements the application code.
- Ensure the existing `Edit(ai/**)` permission in `settings.local.json` stays and is cross-referenced from the Scope section.
- Tests: assert the generated CLAUDE.md contains the Scope statement and that its wording is consistent with the `settings.local.json` `Edit` list (same set of directories referenced).
- Update every example YAML's generated output to match.

### Out of Scope
- Expanding `Edit` permissions (explicitly rejected under Stance 1).
- Adding a composition switch for full-development mode (explicitly rejected under Stance 1).
- Redesigning the permission system itself.
- Changing hook posture (BEAN-250).

## Acceptance Criteria

- [ ] Stance 1 recorded in `ai/context/decisions.md` as an ADR with the rationale.
- [ ] Generated CLAUDE.md template has a visible Scope section in the first third of the document stating the planning-only intent.
- [ ] The Scope section names `ai/` as the agent-editable tree and explicitly notes that application source code is the human's responsibility.
- [ ] `settings.local.json` remains `Edit(ai/**)`; a test asserts the directories named in the Scope section match the `Edit` allow list.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition. This is a policy decision — BA and Architect likely both belong on the wave.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**BA + Architect likely.** Requires a clear scope statement (BA) and a coherent permission model (Architect). Document the rationale in `ai/context/decisions.md` regardless of which option is chosen.

**Precedent.** The Foundry repo's own `.claude/settings.local.json` allows broader edits because the humans working in this repo *are* implementing code. The question is whether every generated downstream project should inherit that assumption.

**Safety posture interaction.** Check alignment with BEAN-250 (hook posture rebalance) before landing — they touch overlapping concepts and should agree on terminology.

**Second-pass reviewer confirmation (2026-04-17).** The external review re-flagged the permission model as "conceptually confusing" — specifically the mismatch between docs that imply the agentic team builds software and a permission set that only allows `Edit(ai/**)`. Stance 1's resolution (explain the scope explicitly in CLAUDE.md) is still the right answer; this reinforces the Scope-section deliverable. Coordinate with BEAN-269's CLAUDE.md orchestration section so the scope statement and the orchestration policy read as one coherent policy, not two disconnected paragraphs.

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
