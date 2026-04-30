# BEAN-259 / Task 01: Architect — Mechanism Choice ADR

| Field | Value |
|-------|-------|
| **Owner** | architect |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-30 09:19 |
| **Completed** | 2026-04-30 09:22 |
| **Duration** | 3m |

## Goal

Decide between the two candidate mechanisms for filtering expertise per
persona at compile time, and record the decision as an ADR in
`ai/context/decisions.md`. The ADR must be specific enough that the
developer can implement it without re-litigating the design.

## Inputs

- ai/beans/BEAN-259-persona-scoped-expertise-inclusion/bean.md — full scope, both candidate mechanisms (A vs B), and acceptance criteria
- foundry_app/services/compiler.py — `_build_lean_claude_md` and the place where expertise is currently joined to per-persona member prompts
- foundry_app/services/agent_writer.py — generates the per-persona agent files
- foundry_app/core/models.py — `PersonaInfo`, `ExpertiseInfo`, `CompositionSpec`, `ExpertiseSelection`, `PersonaSelection`
- ai-team-library/personas/ — sample persona files (look at developer, devops-release, ux-ui-designer to see what categories of expertise each actually needs)
- ai-team-library/expertise/ — sample expertise files (look at python, typescript, accessibility-compliance to see categories)
- ai/context/decisions.md — existing ADR style; ADR-007 (line 285) is a good recent reference for tone and structure
- ai-team-library/personas/_index.yml or front-matter on persona.md (check whichever exists for current metadata format)

## Decision Required

Choose one mechanism:

- **(A) Per-expertise persona relevance** — Each expertise file declares a list of persona IDs it applies to. Compiler filters expertise per persona based on that list.
- **(B) Per-persona expertise filter** — Each persona file declares which expertise *categories* it wants (e.g., `design`, `deploy`, `language`). Compiler filters by category.

## Acceptance Criteria

- [ ] New ADR written to `ai/context/decisions.md` (next sequential ADR-NNN number) with: Date, Status: Accepted, Bean: BEAN-259, Deciders: Architect, Context, Decision, Consequences (Positive / Negative), Reversibility, Alternatives Rejected.
- [ ] ADR explicitly chooses mechanism A or B with a one-line rationale that the developer can quote.
- [ ] ADR specifies the metadata schema: where it lives (front-matter? separate YAML?), what the keys are, what the value types are, and what the default is when metadata is absent (must default to today's behavior — all expertise to all personas — for backward compat).
- [ ] ADR specifies the compiler-side filter behavior: what is filtered (full expertise content, just headers, etc.) and what is preserved.
- [ ] ADR names the test cases that prove the filter works: at minimum, "DevOps-Release member prompt for a React/TS composition contains no `tsconfig` detail" and "Developer member prompt for the same composition still contains language and infra expertise".
- [ ] ADR is short (≤ 120 lines including all sections) and uses the existing ADR template structure.

## Definition of Done

- ADR landed in `ai/context/decisions.md`.
- Architect's mechanism choice is unambiguous.
- Developer can implement directly from the ADR without further design questions.

## Notes

The bean's "Backward compatibility" note is binding: a composition with
no metadata must continue to receive all expertise on all personas.
Don't break BEAN-261 / BEAN-216 (Stack→Expertise rename) or any
previously-generated project's expectations.
