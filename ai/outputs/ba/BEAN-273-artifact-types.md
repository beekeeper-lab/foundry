# BEAN-273 — Artifact-Type Registry & Persona Contracts

**Owner:** BA
**Bean:** BEAN-273 — Persona `produces:` / `consumes:` Contracts
**Task:** 01 — Define artifact-type registry content
**Status:** Deliverable for Architect (Task 02) and Developer (Task 03).

This document is the canonical source for the artifact-type registry that
Developer will commit to `ai-team-library/contracts/artifact-types.yml`, plus
the per-persona `produces:` / `consumes:` lists that Developer will graft into
each `ai-team-library/personas/core/<persona>/persona.md` file. It is
self-contained: Developer should not have to re-derive any list from persona
outputs.md content.

The registry covers **15 artifact types** drawn from the bean's suggested list
and reconciled against what the five core persona `outputs.md` files actually
describe. Names use kebab-case to match the bean's Scope wording.

---

## Registry

```yaml
# ai-team-library/contracts/artifact-types.yml
# Registry of artifact types produced and consumed by core personas.
# Schema: each entry has name, description, format, required-fields, template-path.
# Schema enforcement on artifact bodies is out of scope for BEAN-273
# (a follow-up bean will validate that a markdown file marked `user-story`
# actually contains the listed required-fields).

types:
  - name: bean-spec
    description: >-
      The full specification of a unit of work (feature, fix, chore, epic).
      Lives at ai/beans/BEAN-NNN-<slug>/bean.md and is the entry point for
      every wave. Owns problem statement, goal, scope (in/out), acceptance
      criteria, task table, and notes.
    format: markdown
    required-fields:
      - bean-id
      - status
      - priority
      - problem-statement
      - goal
      - scope-in
      - scope-out
      - acceptance-criteria
      - tasks
    template-path: ai/beans/_bean-template.md

  - name: task-spec
    description: >-
      A single assignable task within a bean. Names the owning persona, its
      depends-on edges, the goal, the inputs the worker may read (Context
      Diet), and the per-task acceptance criteria. Lives at
      ai/beans/BEAN-NNN-<slug>/tasks/NN-<owner>-<slug>.md.
    format: markdown
    required-fields:
      - owner
      - depends-on
      - status
      - goal
      - inputs
      - acceptance-criteria
    template-path: personas/team-lead/templates/task-spec.md

  - name: user-story
    description: >-
      A vertical slice of user-visible behavior in As-a / I-want / So-that
      form, with at least two acceptance criteria written in Given/When/Then
      (or equivalent testable structure). Primary BA output when the BA is
      activated for a bean.
    format: markdown
    required-fields:
      - title
      - narrative
      - acceptance-criteria
      - dependencies
      - assumptions
    template-path: personas/ba/templates/user-story.md

  - name: acceptance-criteria
    description: >-
      An enumeration of pass/fail conditions for a story, task, or bean.
      Each criterion is independently testable with concrete values, no
      implementation detail. Default-owner ambiguity is documented in the
      prose note below the registry — BEAN-275 will codify the policy.
    format: markdown
    required-fields:
      - bean-or-story-id
      - criteria
    template-path: personas/ba/templates/acceptance-criteria.md

  - name: scope-definition
    description: >-
      The In Scope / Out of Scope / Deferred boundary for a bean or feature.
      Frequently embedded in the bean-spec, but called out separately so
      personas that consume scope (Architect, Developer, Tech-QA) can point
      at it cleanly when answering "is this in this bean?".
    format: markdown
    required-fields:
      - in-scope
      - out-of-scope
      - deferred
    template-path: null

  - name: risk-register
    description: >-
      A list of risks, assumptions, and open questions identified during
      requirements analysis or architectural review. Each entry records
      likelihood, impact, owner, and mitigation. Used by Team-Lead for
      escalation and by Architect for design-time risk surfacing.
    format: markdown
    required-fields:
      - risks
      - assumptions
      - open-questions
    template-path: null

  - name: adr
    description: >-
      Architecture Decision Record — context, options considered, decision
      taken, and consequences. Numbered sequentially in
      ai/context/decisions.md. ADRs are append-only; superseded entries
      link to their replacement.
    format: markdown
    required-fields:
      - number
      - title
      - status
      - context
      - options
      - decision
      - consequences
    template-path: personas/architect/templates/adr.md

  - name: design-spec
    description: >-
      Detailed technical specification for a feature or component:
      overview, component diagram, API contract, data model, behavior
      sequences, non-functional requirements, dependencies, open
      questions. Produced when a bean activates the Architect.
    format: markdown
    required-fields:
      - overview
      - component-diagram
      - api-contract
      - data-model
      - behavior
      - non-functional-requirements
      - dependencies
    template-path: personas/architect/templates/design-spec.md

  - name: dev-decision
    description: >-
      Developer-level design decision recorded when an implementation
      choice has multiple reasonable options but does not warrant a full
      ADR (i.e., the decision is reversible and contained). Captures
      options considered and rationale; lighter-weight than an ADR.
    format: markdown
    required-fields:
      - title
      - context
      - options
      - decision
      - rationale
    template-path: personas/developer/templates/dev-design-decision.md

  - name: code-change
    description: >-
      A pull-request-ready changeset implementing a task. Covers production
      source edits, accompanying unit/integration tests authored by the
      Developer, and a PR description with How-to-Test instructions. The
      Developer's primary deliverable.
    format: markdown
    required-fields:
      - summary
      - what-changed
      - how-to-test
      - files-touched
    template-path: personas/developer/templates/pr-description.md

  - name: test-suite
    description: >-
      Tech-QA-authored automated tests (unit, integration, end-to-end) and
      manual test cases mapped to acceptance criteria. The Developer's
      own tests in code-change are part of the change; this artifact is
      the Tech-QA test-plan + test-cases bundle that lives alongside the
      bean and verifies AC coverage.
    format: markdown
    required-fields:
      - test-plan
      - test-cases
      - entry-criteria
      - exit-criteria
    template-path: personas/tech-qa/templates/test-plan.md

  - name: traceability-matrix
    description: >-
      A matrix linking acceptance-criteria → test-cases → code-change
      paths. Tech-QA owns the matrix; consumed by Team-Lead at bean
      verification time and by audit/compliance reviewers later.
    format: markdown
    required-fields:
      - bean-id
      - rows
    template-path: personas/tech-qa/templates/traceability-matrix.md

  - name: vdd-report
    description: >-
      Verification & Defect Disposition report — Tech-QA's per-bean
      verification output. Records test execution results, defects found
      (with severity), regression status, and a pass/fail recommendation
      to the Team-Lead's bean-verification step.
    format: markdown
    required-fields:
      - bean-id
      - test-results
      - defects
      - recommendation
    template-path: personas/tech-qa/templates/test-report.md

  - name: handoff-packet
    description: >-
      The structured payload one persona writes to `ai/outputs/<from>/`
      when its task completes, naming what produced artifacts the next
      persona should read. The compiler-emitted contract graph (BEAN-274)
      and per-edge handoff schemas (BEAN-276) build on this artifact.
    format: markdown
    required-fields:
      - from-persona
      - to-persona
      - bean-id
      - task-id
      - produced-artifacts
      - notes
    template-path: null

  - name: merge-summary
    description: >-
      Team-Lead's integration summary after multi-task or multi-persona
      outputs are reconciled and the bean is marked Done. Names the
      components integrated, decisions made during integration, rework
      triggered, and verification performed.
    format: markdown
    required-fields:
      - bean-id
      - components-integrated
      - integration-decisions
      - rework
      - verification
    template-path: null
```

### Note on `acceptance-criteria` ownership (for Architect / BEAN-275)

`acceptance-criteria` is the one artifact whose producer is conditional on
team composition rather than fixed:

- **When the BA is activated on a bean** (BA `Activated When` rules #1–#7),
  the BA produces `acceptance-criteria` as part of (or alongside) the
  `user-story`. This is the preferred default for any user-facing or
  ambiguous bean.
- **When the BA is *not* activated** (the default wave is Developer →
  Tech-QA), the **Team-Lead produces `acceptance-criteria`** as part of
  bean decomposition — the AC table inside `bean.md` is the artifact, and
  the Team-Lead is its author of record.

The persona contracts below reflect this by listing
`acceptance-criteria` under **both** BA `produces:` and Team-Lead
`produces:`. The contract graph therefore has two valid producers for one
type; the validator (BEAN-274) should treat that as legal as long as
exactly one producer is *active* on a given bean. The policy text — i.e.
how the validator chooses which producer is active — is BEAN-275 territory
and intentionally not codified here. Architect should ADR the rule in
Task 02 so Developer (Task 03) knows whether the loader needs special-case
handling for this type or whether the simple "name appears in registry,
name appears on at least one active persona's `produces:`" rule suffices.

Recommended ADR phrasing for Architect to consider:

> When more than one core persona declares `produces: acceptance-criteria`,
> the Team-Lead's declaration is treated as the *fallback* producer. If the
> BA is on the wave for a given bean, the BA's declaration wins and the
> Team-Lead's is suppressed for that bean. The validator MUST flag a bean
> whose composed team has zero active producers of `acceptance-criteria`.

---

## Persona Contracts

Each block below is the `produces:` / `consumes:` payload Developer will
graft into the corresponding `ai-team-library/personas/core/<persona>/persona.md`
file in Task 03 (per Architect's chosen format from Task 02 — frontmatter or
a fenced `contracts:` block). Every name resolves to an entry in the registry
above. No persona has empty `produces:` or `consumes:`.

### BA

```yaml
contracts:
  produces:
    - user-story
    - acceptance-criteria        # when BA is activated; see ownership note
    - scope-definition
    - risk-register
    - handoff-packet
  consumes:
    - bean-spec
    - scope-definition           # consumed when revising or extending a prior BA's scope artifact
```

### Architect

```yaml
contracts:
  produces:
    - adr
    - design-spec
    - risk-register              # design-time risks; complements BA's requirements-time risks
    - handoff-packet
  consumes:
    - bean-spec
    - user-story
    - acceptance-criteria
    - scope-definition
```

### Developer

```yaml
contracts:
  produces:
    - code-change
    - dev-decision
    - handoff-packet
  consumes:
    - task-spec
    - user-story
    - acceptance-criteria
    - design-spec
    - adr
```

### Tech-QA

```yaml
contracts:
  produces:
    - test-suite
    - traceability-matrix
    - vdd-report
    - handoff-packet
  consumes:
    - acceptance-criteria
    - design-spec
    - code-change
    - bean-spec
```

### Team-Lead

```yaml
contracts:
  produces:
    - bean-spec
    - task-spec
    - acceptance-criteria        # default ownership when BA is not on the wave
    - merge-summary
  consumes:
    - handoff-packet
    - vdd-report
    - traceability-matrix
    - code-change
    - design-spec
    - adr
    - risk-register
```

---

## Cross-Persona Edges (sanity check)

The bean AC requires that "at least one core persona pair has matching
`produces` → `consumes`." Here are the edges this contract set establishes;
each shows that the constraint holds far beyond the minimum.

| Producer    | Artifact                 | Consumer(s)                        |
|-------------|--------------------------|------------------------------------|
| Team-Lead   | `bean-spec`              | BA, Architect, Tech-QA             |
| Team-Lead   | `task-spec`              | Developer                          |
| Team-Lead   | `acceptance-criteria`*   | Architect, Developer, Tech-QA      |
| BA          | `user-story`             | Architect, Developer               |
| BA          | `acceptance-criteria`*   | Architect, Developer, Tech-QA      |
| BA          | `scope-definition`       | Architect (via consumes)           |
| BA          | `risk-register`          | (Architect & Team-Lead read; consumed inline via bean-spec / handoff) |
| Architect   | `design-spec`            | Developer, Tech-QA, Team-Lead      |
| Architect   | `adr`                    | Developer, Team-Lead               |
| Architect   | `risk-register`          | Team-Lead                          |
| Developer   | `code-change`            | Tech-QA, Team-Lead                 |
| Developer   | `dev-decision`           | (recorded; Team-Lead reviews via merge-summary; not a contract edge) |
| Tech-QA     | `traceability-matrix`    | Team-Lead                          |
| Tech-QA     | `vdd-report`             | Team-Lead                          |
| All         | `handoff-packet`         | Team-Lead                          |

\* See ownership note above — only one of {BA, Team-Lead} is the active
producer of `acceptance-criteria` on any given bean.

The two required edges are explicitly present:

- **BA → Developer:** BA produces `user-story` and (when active)
  `acceptance-criteria`; Developer consumes both. Either edge alone
  satisfies the AC.
- **Developer → Tech-QA:** Developer produces `code-change`; Tech-QA
  consumes `code-change`.

---

## Ambiguity Flagged for Architect (Task 02)

1. **`acceptance-criteria` dual producer.** Resolved structurally above
   (both BA and Team-Lead list it under `produces:`); the active-producer
   selection rule needs an ADR. Suggested phrasing inline.
2. **`risk-register` two flavors.** BA's risk-register is requirements-time
   (assumptions, stakeholder gaps); Architect's is design-time (technical
   risk, dependency risk). They share a name and a registry entry but the
   semantic split is real. Architect should decide whether to (a) keep one
   type with two producers (current proposal — simpler, matches
   acceptance-criteria pattern), or (b) split into `requirements-risks` and
   `design-risks`. Recommend (a) for BEAN-273 to keep the registry small;
   defer split to a later bean if the validator can't disambiguate.
3. **`dev-decision` is intentionally not consumed by another core persona.**
   It is recorded for institutional memory and reviewed by Team-Lead at
   merge time as part of `merge-summary` synthesis, but no persona declares
   `consumes: dev-decision`. The current registry tolerates this because
   no AC requires every produced type to be consumed. Architect should
   confirm in Task 02 whether the loader/validator needs to flag
   "dangling produced types" as warnings or treat them as legal.
4. **`handoff-packet` is produced by every persona.** It's the universal
   hand-off envelope. Architect should decide whether the registry should
   model that with a special "everyone produces" tag, or whether listing it
   on every persona's `produces:` (current approach) is acceptable. The
   current approach keeps the schema flat at the cost of a tiny amount of
   repetition.
5. **Where contracts live in `persona.md`.** The bean Notes recommend YAML
   frontmatter fenced with `---`. Architect's ADR (Task 02) makes the final
   call. The contracts above are format-agnostic — Developer can convert to
   either frontmatter or an inline `contracts:` block without re-deriving
   anything.

---

## Out of Scope for This Task (per bean Scope)

- Validating the contract graph at compose-time → BEAN-274.
- Schema enforcement on artifact bodies (e.g., user-story must contain
  Given/When/Then) → follow-up bean.
- Updating extended (non-core) personas → out of scope by bean Scope.
- Per-edge handoff schemas → BEAN-276.
- Codifying the `acceptance-criteria` policy text → BEAN-275.
