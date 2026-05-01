# Task 01: Define Artifact-Type Registry Content

| Field | Value |
|-------|-------|
| **Owner** | BA |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-30 10:44 |
| **Completed** | 2026-04-30 10:47 |
| **Duration** | 3m |

## Goal

Produce the canonical content for the artifact-type registry that Developer
will write into `ai-team-library/contracts/artifact-types.yml`. The registry
names every artifact the five core personas (BA, Architect, Developer,
Tech-QA, Team-Lead) produce or consume, along with `description`, `format`
(markdown / yaml / json), `required-fields`, and `template-path` (where a
template exists in the library; `null` if none).

Aim for ~12-15 types covering the full bean lifecycle. Reference list from
the bean's Scope: `bean-spec`, `task-spec`, `user-story`,
`acceptance-criteria`, `scope-definition`, `risk-register`, `adr`,
`design-spec`, `dev-decision`, `code-change`, `test-suite`,
`traceability-matrix`, `vdd-report`, `handoff-packet`, `merge-summary`.
Add or merge types only if the persona-output evidence warrants it.

For each of the five core personas, propose the `produces:` and `consumes:`
lists using only artifact-type names from the registry. Constraints:

- No persona may have an empty `produces:` or `consumes:`.
- At least one cross-persona pair must connect (e.g., BA produces
  `user-story`, Developer consumes it).
- Acceptance-criteria ownership: BA produces `acceptance-criteria` when
  activated; Team-Lead produces it as default. Note this in the writeup so
  Architect can record the rule in the ADR (BEAN-275 will codify the policy
  text — out of scope here).

Write the deliverable to
`ai/outputs/ba/BEAN-273-artifact-types.md` as two sections:

1. **Registry** — a YAML block ready for Developer to drop into
   `artifact-types.yml`.
2. **Persona contracts** — for each of the five core personas, a small YAML
   block giving its `produces:` and `consumes:` lists.

## Inputs

- `ai/beans/BEAN-273-persona-produces-consumes-contracts/bean.md` — full bean spec, scope, AC
- `ai-team-library/personas/ba/persona.md` — BA scope and outputs
- `ai-team-library/personas/ba/outputs.md` — BA artifact catalog
- `ai-team-library/personas/architect/persona.md` — Architect scope and outputs
- `ai-team-library/personas/architect/outputs.md` — Architect artifact catalog
- `ai-team-library/personas/developer/persona.md` — Developer scope and outputs
- `ai-team-library/personas/developer/outputs.md` — Developer artifact catalog
- `ai-team-library/personas/tech-qa/persona.md` — Tech-QA scope and outputs
- `ai-team-library/personas/tech-qa/outputs.md` — Tech-QA artifact catalog
- `ai-team-library/personas/team-lead/persona.md` — Team-Lead scope and outputs
- `ai-team-library/personas/team-lead/outputs.md` — Team-Lead artifact catalog

## Acceptance Criteria

- [ ] `ai/outputs/ba/BEAN-273-artifact-types.md` exists and contains both
      sections (Registry, Persona contracts).
- [ ] Registry covers 12-15 artifact types with all required fields
      (`name`, `description`, `format`, `required-fields`, `template-path`).
- [ ] Every persona has non-empty `produces:` and `consumes:` lists.
- [ ] Every type referenced in a persona contract appears in the registry.
- [ ] At least one BA-produced type is consumed by Developer (and at
      least one Developer-produced type is consumed by Tech-QA).
- [ ] Writeup notes the BA-vs-Team-Lead `acceptance-criteria` rule (default
      ownership) so Architect can ADR it.

## Definition of Done

- The deliverable is committed at `ai/outputs/ba/BEAN-273-artifact-types.md`.
- The content is a self-contained spec — Developer should be able to
  produce `artifact-types.yml` and edit persona files without needing to
  rederive any of the lists.
