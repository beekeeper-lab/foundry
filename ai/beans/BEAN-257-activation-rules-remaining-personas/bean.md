# BEAN-257: Activation Rules for Remaining Personas

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-257 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

External audit (2026-04-17): "Persona activation is undefined. Agent files are 3K-char stubs, full prompts are 24-31K but none say 'you are activated when X.' With 9 agents and no activation rules, ownership is ambiguous."

BEAN-228 and BEAN-229 introduced explicit "Activated When" sections for **Architect** and **BA**. The other personas — **Developer**, **Tech-QA**, **Code-Quality-Reviewer**, **UX/UI Designer**, **DevOps-Release**, **Integrator-Merge-Captain**, plus any persona in the library not yet covered — still lack activation rules. When the Team Lead decomposes a bean, there's no documented signal for whether these personas are on the wave.

## Goal

Every persona shipped in the default library has an explicit "Activated When" (or equivalent-named) section that states the conditions under which the persona joins a bean wave. Team Lead decomposition can apply consistent rules instead of ad-hoc judgment.

## Scope

### In Scope
- Follow the pattern established by BEAN-228/229 for Architect and BA.
- Add "Activated When" sections to every remaining persona in `ai-team-library/personas/*/persona.md`:
  - Developer (mandatory for implementation tasks — codify it)
  - Tech-QA (mandatory for all beans — codify the rule already in the workflow)
  - Code-Quality-Reviewer (activation criteria: PR review, code-quality-specific concerns — disambiguates vs. Tech-QA, see BEAN-258)
  - UX/UI Designer (activation criteria: new UI surface, visual redesign, a11y work)
  - DevOps-Release (activation criteria: release, deploy, CI/CD changes)
  - Integrator-Merge-Captain (activation criteria: multi-branch merges, conflict resolution)
  - Any other persona not yet covered (audit the library)
- Update `.claude/agents/team-lead.md` decomposition guidance to reference the activation rules as the authoritative source.
- No functional code changes — this is library-content + agent-doc work.

### Out of Scope
- Programmatic enforcement of activation rules (team-lead-agent follows them by convention).
- Changing the default wave (Developer → Tech-QA) — that already holds.
- Persona scope/boundary between CQR and Tech-QA (BEAN-258).

## Acceptance Criteria

- [ ] Every persona file in `ai-team-library/personas/*/persona.md` has an "Activated When" section.
- [ ] The section format matches BEAN-228/229's convention (bullet list with concrete triggers, plus a fallback rule).
- [ ] Team Lead agent's decomposition guidance references these sections as authoritative.
- [ ] A short audit note added to `ai/context/team-lead.md` or similar confirming every persona is now covered.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Precedent.** BEAN-228 (Architect Engagement Rules) and BEAN-229 (BA Engagement Rules) already set the pattern. Copy its shape.

**Interaction with BEAN-258.** The CQR and Tech-QA activation rules should partition clearly — each bean's activation criteria references the scope split documented in BEAN-258.

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
