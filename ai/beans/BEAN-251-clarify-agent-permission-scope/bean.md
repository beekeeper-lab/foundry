# BEAN-251: Clarify Agent Permission Scope in Generated Projects

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-251 |
| **Status** | Unapproved |
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

A generated project's permission model matches its documented intent. The user can tell, from a single authoritative source (generated `CLAUDE.md` and `settings.local.json`), exactly what the agents are permitted to touch and why.

## Scope

### In Scope
- Decide the intent for the default composition:
  - **Option A — planning-only**: keep `Edit(ai/**)`, state explicitly in generated `CLAUDE.md` that the agents manage planning artifacts and a human implements app code.
  - **Option B — full-development**: expand the default Edit permission to cover source directories (e.g., `src/**`, or no path restriction), keep `ai-team-library`-style read-only carve-outs, and state explicitly that agents will modify app code.
  - **Option C — both, selectable**: add a wizard/CLI flag that picks the permission profile; default to one and document the other.
- Implement the chosen direction in the generator: update `foundry_app/services/safety_writer.py` (or wherever `settings.local.json` is emitted), the default composition options, and the generated `CLAUDE.md`'s "Scope" section.
- Ensure the chosen default is consistent across every example YAML.
- Tests: assert the emitted `settings.local.json` matches the documented posture.

### Out of Scope
- Redesigning the permission system itself.
- Changing hook posture (BEAN-250).
- Adding new permission categories beyond Edit/Read/Bash.

## Acceptance Criteria

- [ ] Decision recorded in `ai/context/decisions.md` (new ADR) or in the bean's Notes before implementation begins.
- [ ] Generated project's `CLAUDE.md` has a "Scope" section (1–3 sentences) stating what the agents are authorized to modify and what remains in human hands.
- [ ] `settings.local.json` matches the scope statement. If planning-only: `Edit(ai/**)` remains, CLAUDE.md says so. If full-dev: broader Edit permission, and CLAUDE.md says the agents will modify source code.
- [ ] If option C (selectable) is chosen: a new composition field controls the profile; both profiles covered by a test.
- [ ] At least one test asserts the emitted `settings.local.json` permission list matches the scope declared in CLAUDE.md (structurally — same set of directories mentioned in both places).
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
