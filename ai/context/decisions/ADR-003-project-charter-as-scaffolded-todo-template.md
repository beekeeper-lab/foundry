# ADR-003: Project Charter as Scaffolded TODO Template

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-252 |
| **Deciders** | Architect |

## Context

External audit (2026-04-17) flagged that a freshly generated Foundry project has no purpose statement. When `spec.project.description` is empty, the generated README falls back to `"AI-team-backed project for <Name>"` — a single line of generic prose that tells personas nothing about what the project is, who it serves, or what "done" looks like. The audit called this the #1 day-1 blocker: *"Nine personas, zero product. A team with no goal will invent one, inconsistently."*

Two implementation paths were considered:

1. **Scaffold a charter file** — emit `ai/context/project-charter.md` from the scaffold pipeline as a structured TODO template (Purpose / Audience / Success Criteria / Non-Goals / Constraints).
2. **Promote `description` to required** — make `ProjectIdentity.description` mandatory with a minimum length, validated at the wizard and CLI boundaries.

## Decision

Scaffold `ai/context/project-charter.md` as a structured TODO template. The file is emitted by `foundry_app/services/scaffold.py` alongside `README.md`, overlay-safe (only written if missing), with sections for Purpose, Audience, Success Criteria, Non-Goals, and Constraints. If `spec.project.description` is set it is echoed under the title; otherwise a TODO line is shown.

## Consequences

**Positive:**
- Strictly additive — does not break existing wizard flows, CLI invocations, or YAML files in the wild.
- Mirrors the existing README emission pattern (overlay-safe, footer with version+date), so the implementation surface is small and well-precedented.
- The TODO-marked sections are visually loud — personas opening the project see immediately that there is unfilled context to address.
- Composes with future hardening: a follow-up bean can promote `description` to required without contradicting this decision.

**Negative:**
- A charter file with the TODO markers still in place is not enforced — a careless user can ignore it. Mitigated by the `> **Status:** TODO` admonition at the top of the file, which is greppable.
- Adds one more file to the scaffold output (currently ~10 files at the project root level).

## Alternatives Rejected

1. **Promote `description` to required (Option 2):** Larger blast radius — touches the model, validator, wizard, and CLI; breaks existing YAML compositions that rely on the optional default; a one-line description is still terse compared to a five-section charter. Reserved as a possible follow-up if the charter alone proves insufficient.
2. **Embed the charter in `CLAUDE.md`:** CLAUDE.md is already instruction-dense and is regenerated from the spec; mixing user-authored prose into a regenerated file invites overwrite conflicts.
3. **Embed the charter in `README.md`:** README is for humans landing on the repo; the charter is for personas opening the project. Co-locating with `ai/context/project.md` (the architecture/module map) keeps the AI-team-facing context in one place.

