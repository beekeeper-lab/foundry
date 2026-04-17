# BEAN-250: Rebalance Hook Posture Taxonomy

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-250 |
| **Status** | In Progress |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 19:02 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

External review (2026-04-17): "Hook posture is still conceptually muddy. Your composition says posture is `baseline`, but the enabled packs are still quite broad and strongly enforcing. If this is baseline, what does hardened mean? If baseline already includes multiple Git, Azure, compliance, QA, lint, and secret-oriented controls, then your posture taxonomy needs sharpening."

Reviewer's two proposed resolutions:
1. **Reduce what `baseline` enables** so the word matches the posture.
2. **Rename the posture levels** so the taxonomy is honest about what each level turns on.

Today's `Posture` enum in `foundry_app/core/models.py` and the hook-pack defaults in the library don't yet answer this question in a way the generated project makes obvious.

## Goal

A user can read the posture level (`baseline`, or whatever we rename it to) and predict, within a reasonable range, how many packs will be enabled and at what strictness. The posture level, the pack list, and the enforcement mode match in intent.

## Scope

### In Scope
- Inventory the current posture levels (`Posture` enum), what each one enables in the default hook-pack set, and what the real distribution of packs looks like for `baseline`.
- Pick a direction — either (a) keep the names and slim `baseline`'s pack list to a minimum, or (b) keep the pack list and rename the levels (e.g., `minimal` / `standard` / `hardened`, or `permissive` / `enforcing` / `strict`).
- Update `foundry_app/core/models.py`, any consumers, and the default library compositions to match the chosen direction.
- Update `ai-team-library/claude/hooks/` and any example YAMLs as needed.
- Update or add tests asserting the posture level's actual pack list matches its label.

### Out of Scope
- Designing new hook packs (that's content work, separate bean if needed).
- Making posture selection dynamic per-project beyond the current enum choice.
- Modifying enforcement mode semantics (`enforcing` / `permissive` / `disabled`).

## Acceptance Criteria

- [ ] A one-page `ai/context/hook-posture.md` (new, or an update to an existing doc) documents the final posture taxonomy: each level's intent, pack list, and default enforcement mode.
- [ ] The chosen direction (rename or slim) is applied to code, library, examples, and tests consistently — no mixed terminology.
- [ ] The generated project's `CLAUDE.md` (or hook-posture-related section) accurately reflects which packs are enabled at the chosen level.
- [ ] Existing hook-related tests updated to match; at least one test asserts that `Posture.BASELINE` (or its successor name) matches the documented pack list.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | ADR — posture taxonomy direction | Architect | — | Pending |
| 2 | Author `ai/context/hook-posture.md` + expose posture base-pack API | Developer | 1 | Pending |
| 3 | Lock-in test asserting posture → base pack list | Tech-QA | 2 | Pending |

> Skipped: BA (default — no ambiguous requirements). Architect included because this is a taxonomy decision worth recording in an ADR.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**Architect likely.** This is a rename-vs-reshape decision with cross-cutting impact (enum, library YAMLs, generated docs). Add Architect to the wave per the Architect Engagement Rules.

**ADR candidate.** If the direction is "rename" the rationale belongs in `ai/context/decisions.md`.

**Risk.** Renaming is visible in every composition YAML. Include a migration note so users of older YAMLs know which new level matches their old one (or provide a best-effort alias during loading).

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | ADR — posture taxonomy direction | Architect | — | — | — | — |
| 2 | Author `ai/context/hook-posture.md` + expose posture base-pack API | Developer | — | — | — | — |
| 3 | Lock-in test asserting posture → base pack list | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |