# BEAN-275: Resolve Acceptance Criteria & ADR Boundary Ownership

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-275 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-04-28 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |
| **Depends On** | — |

## Problem Statement

The architectural review found two unresolved role boundaries:

**1. Acceptance criteria — five roles touch them.**
- BA "writes user stories with clear acceptance criteria" (`ba.md:76`)
- Team-Lead "defines acceptance criteria" (`team-lead.md:59`)
- Developer "verifies your outputs against the task's acceptance criteria" (`developer.md:19, 43`)
- Architect "self-verifies your outputs against the task's acceptance criteria" (`architect.md:39, 60`)
- Tech-QA "ensures every deliverable meets its acceptance criteria" (`tech-qa.md:3`)

When BA's intent and Team-Lead's decomposition conflict, no tie-breaker.

**2. ADR vs dev-decision — fuzzy boundary.**
- Architect writes ADRs via `/internal:new-adr` (`architect.md:49`)
- Developer writes "decisions" via `/internal:new-dev-decision` (`developer.md:16`)
- But `developer.md:71`: "propose changes through `/internal:new-adr`, don't deviate unilaterally"

When does an implementation choice become an architecture decision? No rule. BEAN-258 resolved the symmetric question for code-quality-reviewer vs tech-qa; this bean does the equivalent for these two pairs.

## Goal

Each ambiguous artifact has exactly one owner. Other roles' interactions with the artifact are explicitly framed as *consume* / *verify*, never *author*. The boundary between ADR and dev-decision is rule-based and testable.

## Scope

### In Scope

- **Acceptance-criteria ownership rule** (codify in `ai-team-library/personas/core/*/persona.md` and Foundry's `.claude/agents/*.md`):
  - BA owns `acceptance-criteria` when on the wave.
  - Team-Lead owns `acceptance-criteria` by default (when BA is not activated).
  - Developer, Architect, and Tech-QA *verify against* AC; they never author them. Edits to AC mid-bean require Team-Lead approval and a brief note in the bean's Notes section.
- **ADR vs dev-decision rule** (blast-radius based):
  - **ADR** (Architect via `/internal:new-adr`): decision affects ≥3 modules, an external interface, a cross-cutting concern, or a future-irreversible commitment.
  - **dev-decision** (Developer via `/internal:new-dev-decision`): decision is local to one module, has no external surface, and is reversible.
  - When a Developer encounters a decision that crosses the ADR threshold, they pause and request Architect activation rather than write a dev-decision.
- Add a "Scope Boundaries" subsection to BA, Team-Lead, Developer, Architect, Tech-QA personas (mirror BEAN-258's pattern for CQR/Tech-QA) covering both rules.
- Update `ai-team-library/personas/core/team-lead/persona.md` orchestration rules to name the AC owner per wave configuration and the escalation path for ADR-threshold decisions.
- Update bean template (`ai/beans/_bean-template.md`) to note in the Acceptance Criteria section heading: "Authored by: BA (when activated) | Team-Lead (default)."
- Tests: persona files contain the new subsections; tests parse the Scope Boundaries sections and verify they reference the correct counterparts.

### Out of Scope

- Renaming `dev-decision` or `ADR`.
- Merging the two artifact types.
- Changing `/internal:new-adr` or `/internal:new-dev-decision` command behavior.
- Re-litigating BEAN-258's CQR/Tech-QA split.

## Acceptance Criteria

- [ ] All 5 core persona files (library + Foundry kit copies) have a "Scope Boundaries" subsection covering both AC ownership and the ADR/dev-decision rule as relevant to that role.
- [ ] Team-Lead orchestration rules name the AC owner per wave configuration.
- [ ] Bean template AC section heading names the author.
- [ ] A grep of all 5 persona files for "acceptance criteria" finds no language that contradicts the ownership rule.
- [ ] Tests verify the Scope Boundaries subsections exist and partition cleanly (no overlap, no gap).
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks populated by Team-Lead. Likely wave: BA (wording — these are policy statements, BA's bread and butter), Developer (the doc edits), Tech-QA (partition cleanliness verification, mirrors BEAN-258).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Pattern from BEAN-258.** That bean partitioned CQR vs Tech-QA cleanly with symmetric "Scope Boundaries" subsections. Use the same pattern here for AC ownership and the ADR boundary.

**Coordinate with BEAN-273.** That bean's `produces:` declaration on personas should align with the AC ownership rule (BA produces `acceptance-criteria` when activated; Team-Lead produces by default — or codify as both produce, with composition determining which is active). Architect should think this through.

**No code change.** This is a pure documentation/policy bean. Small wave (BA + Developer + Tech-QA), maybe Architect-light for the cross-reference with BEAN-273.

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
