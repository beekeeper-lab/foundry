# Task 02: ADR — Contract Format, Location, and Loader Integration

| Field | Value |
|-------|-------|
| **Owner** | Architect |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-04-30 10:47 |
| **Completed** | 2026-04-30 10:52 |
| **Duration** | 5m |

## Goal

Record an ADR in `ai/context/decisions.md` capturing the structural choices
that the rest of BEAN-273 (and BEAN-274 / BEAN-276) will depend on:

1. **Contract location on personas.** Decide between (a) YAML frontmatter
   block at the top of `persona.md` fenced with `---`, or (b) a sibling
   `contracts.yml` next to `persona.md`. Pick (a) per the bean's Notes
   recommendation unless a concrete reason rules it out. Document the
   rationale and the trade-off.
2. **Registry location.** Confirm `ai-team-library/contracts/artifact-types.yml`
   as the registry path and explain why a top-level `contracts/` directory
   in the library beats putting the registry under `personas/`,
   `templates/`, or `workflows/`.
3. **Loader integration.** Decide whether to extend
   `foundry_app/services/library_indexer.py` with a contract-aware
   indexing path or add a new `foundry_app/services/contracts_loader.py`.
   Pick the option with smaller blast radius; record the rejected option
   and why.
4. **Compiler emission.** Decide the shape of the `contracts:` block in
   the generated `ai/team/composition.yml`. At minimum: list of personas
   on the team with their `produces:` / `consumes:` arrays, plus a flat
   `artifact-types:` reference list for traceability. This is informational
   for now (BEAN-274 will validate it); freeze the shape so BEAN-274 has a
   stable target.

Also record (briefly) the BA-vs-Team-Lead `acceptance-criteria` ownership
rule the BA writeup flagged — the ADR notes the contract-graph view
(whichever persona declares `produces: acceptance-criteria` owns it for
that composition); BEAN-275 will codify the prose policy.

Write a short companion note for Developer at
`ai/outputs/architect/BEAN-273-design.md` listing:

- The four decisions above with one-line answers.
- A worked example of a persona file with the chosen frontmatter shape.
- A worked example of the `contracts:` block in `composition.yml`.
- The exact module/function entry points Developer should add or extend.

## Inputs

- `ai/beans/BEAN-273-persona-produces-consumes-contracts/bean.md` — bean spec
- `ai/outputs/ba/BEAN-273-artifact-types.md` — BA's registry + persona contracts
- `ai/context/decisions.md` — existing ADRs (append the new ADR here)
- `foundry_app/services/library_indexer.py` — current indexer
- `foundry_app/services/compiler.py` — current compiler
- `foundry_app/core/models.py` — Pydantic models the loader / compiler use
- `ai-team-library/personas/ba/persona.md` — sample persona file shape

## Acceptance Criteria

- [ ] New ADR appended to `ai/context/decisions.md` with all four
      decisions, status `Accepted`, and one-paragraph rationale per
      decision.
- [ ] `ai/outputs/architect/BEAN-273-design.md` exists with the four
      decisions, two worked examples, and the exact entry points.
- [ ] The frontmatter shape and the `composition.yml` `contracts:` block
      shape are concrete enough that Developer can implement without
      asking follow-up questions.
- [ ] No decision is left as "TBD" or "Developer will choose".

## Definition of Done

- ADR + design note committed.
- A reader of the design note can write the registry file, edit a persona
  file, and stub the loader without re-reading the bean.
