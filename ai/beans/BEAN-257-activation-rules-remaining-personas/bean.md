# BEAN-257: Activation Rules for Remaining Personas

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-257 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 19:26 |
| **Completed** | 2026-04-17 20:00 |
| **Duration** | 34m |
| **Owner** | team-lead |
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

- [x] Every persona file in `ai-team-library/personas/*/persona.md` has an "Activated When" section.
- [x] The section format matches BEAN-228/229's convention (bullet list with concrete triggers, plus a fallback rule).
- [x] Team Lead agent's decomposition guidance references these sections as authoritative.
- [x] A short audit note added to `ai/context/persona-activation-audit.md` confirming every persona is now covered.
- [x] All tests pass (`uv run pytest`) — 1903 passed.
- [x] Lint clean (`uv run ruff check foundry_app/`) — All checks passed.

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add "Activated When" sections to all library personas + update team-lead agent | developer | — | Done |
| 2 | Verify activation rules coverage and audit note | tech-qa | 1 | Done |

> Skipped: BA (default — process/library-content work, not user-facing requirements), Architect (default — content additions, no system design or new module)

## Changes

| File | Lines |
|------|-------|
| ai-team-library/personas/architect/persona.md | +30 |
| ai-team-library/personas/ba/persona.md | +28 |
| ai-team-library/personas/team-lead/persona.md | +20 |
| ai-team-library/personas/developer/persona.md | +21 |
| ai-team-library/personas/tech-qa/persona.md | +19 |
| ai-team-library/personas/code-quality-reviewer/persona.md | +29 |
| ai-team-library/personas/ux-ui-designer/persona.md | +27 |
| ai-team-library/personas/devops-release/persona.md | +27 |
| ai-team-library/personas/integrator-merge-captain/persona.md | +27 |
| ai-team-library/personas/security-engineer/persona.md | +28 |
| ai-team-library/personas/compliance-risk/persona.md | +28 |
| ai-team-library/personas/researcher-librarian/persona.md | +27 |
| ai-team-library/personas/technical-writer/persona.md | +27 |
| ai-team-library/personas/data-analyst/persona.md | +27 |
| ai-team-library/personas/data-engineer/persona.md | +27 |
| ai-team-library/personas/database-administrator/persona.md | +27 |
| ai-team-library/personas/legal-counsel/persona.md | +27 |
| ai-team-library/personas/mobile-developer/persona.md | +27 |
| ai-team-library/personas/platform-sre-engineer/persona.md | +27 |
| ai-team-library/personas/product-owner/persona.md | +27 |
| ai-team-library/personas/customer-success/persona.md | +27 |
| ai-team-library/personas/financial-operations/persona.md | +27 |
| ai-team-library/personas/change-management/persona.md | +27 |
| ai-team-library/personas/sales-engineer/persona.md | +27 |
| .claude/agents/team-lead.md | +18 |
| ai/context/persona-activation-audit.md | +90 (new) |
| ai/beans/BEAN-257-activation-rules-remaining-personas/bean.md | edits |
| ai/beans/BEAN-257-activation-rules-remaining-personas/tasks/01-developer-activation-rules.md | new |
| ai/beans/BEAN-257-activation-rules-remaining-personas/tasks/02-tech-qa-verify-activation-rules.md | new |

## Notes

**Precedent.** BEAN-228 (Architect Engagement Rules) and BEAN-229 (BA Engagement Rules) already set the pattern. Copy its shape.

**Interaction with BEAN-258.** The CQR and Tech-QA activation rules should partition clearly — each bean's activation criteria references the scope split documented in BEAN-258.

**Interaction with BEAN-269 (orchestration clarity).** BEAN-269 states the project-level policy — *team is an available bench; Developer + Tech-QA mandatory; others opt-in*. This bean provides the per-persona activation triggers that make that bench model operational. Word the "Activated When" sections so they read as selection criteria *from a bench*, not as scheduled participation on every wave. External reviewer (2026-04-17, second pass) flagged that the bench model must be unmistakable in the generated artifacts.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add "Activated When" sections to all library personas + update team-lead agent | developer | — | — | — | — |
| 2 | Verify activation rules coverage and audit note | tech-qa | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1270h 41m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |