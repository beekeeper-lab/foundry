# Task 01: Author the Scope Boundaries Policy Text

| Field | Value |
|-------|-------|
| **Owner** | BA |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-30 11:09 |
| **Completed** | 2026-04-30 11:12 |
| **Duration** | 3m |

## Goal

Produce the canonical prose text for two policy rules:

1. **Acceptance-criteria ownership** —
   - BA owns `acceptance-criteria` when activated on the wave.
   - Team-Lead owns `acceptance-criteria` by default (BA not on wave).
   - Developer, Architect, and Tech-QA *verify against* AC; they never
     author them. Edits to AC mid-bean require Team-Lead approval and a
     short note in the bean's Notes section.

2. **ADR vs dev-decision (blast-radius rule)** —
   - **ADR** (Architect via `/internal:new-adr`): decision affects ≥3
     modules, an external interface, a cross-cutting concern, or a
     future-irreversible commitment.
   - **dev-decision** (Developer via `/internal:new-dev-decision`):
     decision is local to one module, has no external surface, and is
     reversible.
   - When a Developer encounters a decision crossing the ADR threshold,
     they pause and request Architect activation rather than write a
     dev-decision unilaterally.

For each of the five core personas (BA, Architect, Developer, Tech-QA,
Team-Lead), produce the **exact text** of a `## Scope Boundaries`
subsection that role should carry. Mirror the BEAN-258 pattern (CQR vs
Tech-QA partition). Each persona's section names:
- the artifact(s) it owns within these two rules,
- the artifact(s) it explicitly does *not* author,
- the escalation path when it encounters something outside its lane.

Also produce:
- The Team-Lead orchestration update — short prose to add to Team-Lead's
  persona.md (and `.claude/shared/agents/team-lead.md`) naming the AC
  owner per wave configuration and the ADR-threshold escalation path.
- The bean template AC-section heading update — exact replacement text:
  `## Acceptance Criteria` becomes `## Acceptance Criteria` *with a
  one-line subnote* `> Authored by: BA (when activated) | Team-Lead
  (default)`.

Write the deliverable to `ai/outputs/ba/BEAN-275-policy.md` with the
following sections (in order):

1. `## Rule 1 — Acceptance-Criteria Ownership` — the canonical rule
   statement (3-6 sentences).
2. `## Rule 2 — ADR vs dev-decision` — the blast-radius rule statement
   (3-6 sentences).
3. `## Scope Boundaries Sections` — five subsections (`### BA`,
   `### Architect`, `### Developer`, `### Tech-QA`, `### Team-Lead`),
   each containing the *exact* markdown that Developer will paste into
   that persona's `persona.md` (and the kit's agent file).
4. `## Team-Lead Orchestration Update` — the exact prose addition.
5. `## Bean Template Heading Update` — the exact diff (before/after).

Constraints:
- The five Scope Boundaries sections must **partition cleanly** — no
  overlap, no gap, no contradiction. Tech-QA's "Scope Boundaries" must
  not say it authors AC; BA's must not say Architect authors AC. Etc.
- Cross-reference BEAN-273's contract graph: when BA is on the wave, the
  contract `produces: acceptance-criteria` is BA's; when not, it's
  Team-Lead's. Note this alignment in the BA and Team-Lead subsections.
- Keep each subsection concise (≤ 12 lines of markdown). The pattern is
  policy reference, not a tutorial.

## Inputs

- `ai/beans/BEAN-275-acceptance-criteria-adr-ownership/bean.md` — bean spec
- `ai-team-library/personas/ba/persona.md` — current BA scope text
- `ai-team-library/personas/architect/persona.md` — current Architect scope text
- `ai-team-library/personas/developer/persona.md` — current Developer scope text
- `ai-team-library/personas/tech-qa/persona.md` — current Tech-QA scope text
- `ai-team-library/personas/team-lead/persona.md` — current Team-Lead scope + orchestration text
- `ai/beans/_bean-template.md` — current bean template's AC heading
- `ai/context/decisions.md` — ADR-013 (BEAN-273) for the contract-graph cross-reference

## Acceptance Criteria

- [ ] `ai/outputs/ba/BEAN-275-policy.md` exists with all five sections.
- [ ] Five Scope Boundaries subsections (one per core persona) are
      partition-clean: no overlap, no gap, no contradiction.
- [ ] Team-Lead orchestration update names the AC owner per wave config
      and the ADR-threshold escalation path.
- [ ] Bean template heading update is given as exact before/after text.
- [ ] BA-vs-Team-Lead AC ownership is cross-referenced to BEAN-273's
      contract graph (the `produces:` declaration alignment).

## Definition of Done

- The deliverable is committed at `ai/outputs/ba/BEAN-275-policy.md`.
- Developer should be able to paste the five Scope Boundaries
  subsections into the relevant persona files (library + kit) without
  any rewriting.
