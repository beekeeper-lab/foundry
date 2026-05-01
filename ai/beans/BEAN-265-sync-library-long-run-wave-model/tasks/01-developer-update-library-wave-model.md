# Task 01 — Developer: Update Library Wave-Model References

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-265/01 |
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 19:03 |
| **Completed** | 2026-04-17 19:04 |
| **Duration** | 1m |

## Goal

Sync `ai-team-library/claude/` with Foundry's current wave model: Developer → Tech-QA default, with BA and Architect opt-in per documented activation criteria. Remove references to the old mandatory 4-persona wave ("BA → Architect → Developer → Tech-QA") and replace them with language matching `.claude/shared/skills/long-run/SKILL.md` and the team-lead persona's Orchestration Rules.

## Inputs

- `ai-team-library/claude/skills/long-run/SKILL.md` (primary target)
- `ai-team-library/claude/commands/long-run.md` (paired command summary)
- `ai-team-library/claude/commands/new-work.md` (routing examples)
- `ai-team-library/claude/skills/new-work/SKILL.md` (routing logic)
- `.claude/shared/skills/long-run/SKILL.md` — reference for canonical wave-model phrasing
- `ai-team-library/personas/team-lead/persona.md` — source of truth for Orchestration Rules

## Changes

1. **`ai-team-library/claude/skills/long-run/SKILL.md`**
   - Line 68: replace `Follow the wave: BA → Architect → Developer → Tech-QA.` with Developer/Tech-QA default + BA/Architect opt-in wording.
   - Line 69: rewrite skip guidance to reflect that BA/Architect are opt-in (not a wave-role skip); Tech-QA is mandatory.
   - Line 175 (parallel-mode launcher): update the embedded prompt line to match the new wave.

2. **`ai-team-library/claude/commands/long-run.md`**
   - Line 39: replace wave wording in the decomposition step.
   - Line 135 (parallel-mode launcher): update the embedded prompt wave reference.

3. **`ai-team-library/claude/skills/new-work/SKILL.md`**
   - Line 50 (feature route): soften from mandatory `BA → Architect → Developer → Tech-QA` to `Developer → Tech-QA; include BA and Architect per activation criteria`.

4. **`ai-team-library/claude/commands/new-work.md`**
   - Line 69 (feature example): update the example narrative to match the new routing.

## Acceptance Criteria

- [ ] Grep `rg "BA → Architect → Developer → Tech-QA" ai-team-library/claude/` returns no matches.
- [ ] `ai-team-library/claude/skills/long-run/SKILL.md` describes Developer → Tech-QA default with BA/Architect opt-in (matching `.claude/shared/skills/long-run/SKILL.md` semantics, not the test-branch/`/internal:` specifics).
- [ ] Wording is consistent across the two long-run files and the two new-work files.

## Definition of Done

- Library files updated and committed.
- No remaining "mandatory 4-persona wave" language in `ai-team-library/claude/`.
- Tech-QA task can verify regeneration.
