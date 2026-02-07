# Architect -- Outputs

This document enumerates every artifact the Architect is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Architecture Decision Record (ADR)

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Architecture Decision Record                       |
| **Cadence**        | One per significant technical decision             |
| **Template**       | `personas/architect/templates/adr.md`              |
| **Format**         | Markdown                                           |

**Description.** A structured record of a single architectural decision,
including the context that prompted it, the options considered, the decision
made, and the consequences expected. ADRs are the team's permanent record of
why the system is shaped the way it is.

**Quality Bar:**
- The context section describes the problem or requirement that forced a
  decision, not just the solution chosen.
- At least two options are evaluated, each with stated pros and cons.
- The decision is stated as a clear, unambiguous sentence: "We will use X
  for Y."
- Consequences section includes both positive outcomes and trade-offs or risks
  accepted.
- Status is one of: Proposed, Accepted, Deprecated, Superseded.
- If superseded, the ADR links to its replacement. ADRs are never deleted.
- The ADR is numbered sequentially and stored in a dedicated `docs/adr/`
  directory.

**Downstream Consumers:** Developer (for implementation guidance), Team Lead
(for planning implications), Security Engineer (for security impact), future
team members (for historical context).

---

## 2. Design Specification

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Design Specification                               |
| **Cadence**        | One per feature or system component                |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown with text-based diagrams                  |

**Description.** A detailed technical specification for a feature or component,
covering structure, behavior, data flow, and integration points. This is the
primary input developers use to understand what they are building and how it fits
into the larger system.

**Required Sections:**
1. **Overview** -- One paragraph stating what this component does and why it
   exists.
2. **Component Diagram** -- Text-based diagram (Mermaid or ASCII) showing the
   component and its neighbors, with labeled connections.
3. **API Contract** -- For each public interface: endpoints or method
   signatures, request/response schemas, error codes, and authentication
   requirements.
4. **Data Model** -- Entities, their attributes, relationships, and ownership
   boundaries. Include a schema diagram if the model has more than three
   entities.
5. **Behavior** -- Key workflows described as numbered step sequences. Include
   the happy path and at least two failure scenarios.
6. **Non-Functional Requirements** -- Performance targets (latency, throughput),
   availability targets, data retention, and scalability expectations with
   concrete numbers.
7. **Dependencies** -- External services, libraries, or infrastructure this
   component requires, with version constraints if applicable.
8. **Open Questions** -- Unresolved design decisions with owners and deadlines.

**Quality Bar:**
- A developer can begin implementation from this document without needing to
  ask "but how should I handle X?" for any foreseeable scenario.
- All data flows are explicit: what data moves, in what format, through which
  channel, and what happens when the channel fails.
- Diagrams match the written specification. If they diverge, the spec is
  incorrect.
- Non-functional requirements have numbers, not adjectives. "Fast" is not a
  requirement. "p95 response time under 150ms" is.

**Downstream Consumers:** Developer (primary consumer), Tech QA (for test
planning), DevOps-Release (for infrastructure provisioning).

---

## 3. API Contract

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | API Contract                                       |
| **Cadence**        | One per service or integration boundary            |
| **Template**       | None (OpenAPI spec or structured Markdown)          |
| **Format**         | OpenAPI 3.x YAML or Markdown                       |

**Description.** A formal definition of an API's endpoints, request/response
schemas, authentication, and error handling. API contracts enable parallel
development: teams on both sides of an API can work independently once the
contract is agreed upon.

**Quality Bar:**
- Every endpoint has: HTTP method, path, request body schema (if applicable),
  response schema for success and each error code.
- Error responses use a consistent envelope: `{ "error": { "code": "...", "message": "..." } }`.
- Authentication and authorization requirements are stated per endpoint.
- Pagination, filtering, and sorting conventions are defined for collection
  endpoints.
- Versioning strategy is documented (URL path, header, or query parameter).
- Breaking changes are flagged explicitly and require an ADR.

**Downstream Consumers:** Developer (for implementation), Tech QA (for API
testing), external consumers (if the API is public).

---

## 4. Technology Evaluation

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Technology Evaluation                              |
| **Cadence**        | As needed for build-vs-buy or tool selection decisions |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A structured comparison of technology options for a specific
need. This is the supporting analysis that feeds into an ADR. The evaluation
is separate from the decision to allow the decision record to remain concise.

**Required Sections:**
1. **Need Statement** -- What capability is required and what constraints apply.
2. **Candidates** -- Each option with a one-paragraph description.
3. **Evaluation Criteria** -- Weighted criteria (e.g., team familiarity,
   operational cost, performance, community support, license compatibility).
4. **Comparison Matrix** -- Table scoring each candidate against each criterion.
5. **Recommendation** -- Which option to choose and why, with explicit
   acknowledgment of what is sacrificed.

**Quality Bar:**
- At least two candidates are compared (including "do nothing" or "build
  in-house" when applicable).
- Criteria weights reflect project priorities, not generic industry advice.
- Scoring is justified with evidence (benchmarks, documentation quality,
  adoption data), not gut feeling.
- License compatibility with the project's license is verified.

**Downstream Consumers:** Team Lead (for planning), Developer (for context on
tool choices), Stakeholders (for build-vs-buy decisions with cost implications).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository.
- ADRs live in `docs/adr/` with filenames like `001-use-postgresql.md`.
- Design specifications live alongside the code they describe, or in a central
  `docs/design/` directory if they span multiple components.
- Use text-based diagrams (Mermaid preferred) that render in standard Markdown
  viewers and are diffable in version control.
- Cross-reference related documents. An ADR should link to the design spec it
  supports. A design spec should link to the ADRs that constrain it.
- When a design evolves, update the document and note the change. Do not let
  design docs rot into fiction.
