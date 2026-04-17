# BEAN-265: Sync Library long-run Skill With New Wave Model

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-265 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 19:02 |
| **Completed** | 2026-04-17 19:05 |
| **Duration** | 1269h 58m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

External review (2026-04-17): "Team has no BA, but the long-run skill
assumes one. `.claude/skills/long-run/SKILL.md` references the 'BA →
Architect → Developer → Tech-QA' wave. The composition excluded BA."

Foundry's own default wave was updated (Developer → Tech-QA default with
BA and Architect opt-in per BEAN-228, BEAN-229, and the activation
rules in each agent file), but the `ai-team-library` copy of
`skills/long-run/SKILL.md` still prescribes the old 4-persona wave.
Any generated project inherits the stale copy.

Confirmed in a fresh `small-python-team` generation:

- `.claude/skills/long-run/SKILL.md:68`: "Follow the wave: BA → Architect → Developer → Tech-QA."
- `:175`: "Execute the wave (BA → Architect → Developer → Tech-QA)"

## Goal

The library copy of `skills/long-run/SKILL.md` describes the same wave
model the Foundry repo uses: **Developer → Tech-QA** default, with BA
and Architect opt-in per documented activation criteria. Generated
projects that exclude BA or Architect can run `/long-run` without the
skill instructing a phantom hand-off.

## Scope

### In Scope
- Review and update `ai-team-library/claude/skills/long-run/SKILL.md` to
  match the current Foundry wave model.
- Grep the entire library (`ai-team-library/claude/`) for other stale
  references to the old 4-persona wave and update those too (commands,
  hooks, other skills).
- Verify against the generated output of `small-python-team.yml`.
- No app-code changes expected — this is a library sync.

### Out of Scope
- Changing the wave model itself.
- Rewriting the long-run skill's mechanics (spawn, merge, etc.).

## Acceptance Criteria

- [x] `ai-team-library/claude/skills/long-run/SKILL.md` describes the
      Developer → Tech-QA default wave with BA/Architect opt-in.
- [x] Grep of `ai-team-library/claude/` finds no remaining references
      to "BA → Architect → Developer → Tech-QA" as a mandatory sequence.
- [x] Regenerating `small-python-team.yml` yields a long-run skill file
      that matches the updated wording.
- [x] All tests pass (`uv run pytest`) — 1886 passed.
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Update library wave-model references | developer | — | Done |
| 2 | Verify library sync + regeneration + tests/lint | tech-qa | 1 | Done |

> Skipped: BA (default — wave-model language already documented in Foundry; this is a straight library sync, no requirements ambiguity), Architect (default — no new subsystem, API change, or ADR needed; markdown-only sync).

## Changes

| File | Lines |
|------|-------|
| `ai-team-library/claude/skills/long-run/SKILL.md` | +4 / -3 |
| `ai-team-library/claude/commands/long-run.md` | +2 / -2 |
| `ai-team-library/claude/skills/new-work/SKILL.md` | +2 / -2 |
| `ai-team-library/claude/commands/new-work.md` | +1 / -1 |
| `ai/beans/BEAN-265-sync-library-long-run-wave-model/` | tasks + bean.md |
| `ai/outputs/tech-qa/BEAN-265-verification.md` | new |

## Notes

**Source.** External review (2026-04-17). Confirmed in a fresh
`small-python-team` generation.

**Related.** BEAN-228 (Architect Engagement Rules), BEAN-229 (BA
Engagement Rules), and the activation criteria in each agent file
established the new model; the library sync was missed.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Update library wave-model references | developer | 1m | 1,186,806 | 5,641 | $2.34 |
| 2 | Verify library sync + regeneration + tests/lint | tech-qa | 1m | 1,376,836 | 5,879 | $2.72 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 2m |
| **Total Tokens In** | 2,563,642 |
| **Total Tokens Out** | 11,520 |
| **Total Cost** | $5.06 |