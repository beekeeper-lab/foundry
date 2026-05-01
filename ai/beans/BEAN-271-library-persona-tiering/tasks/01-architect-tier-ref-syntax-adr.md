# Task 01: ADR — Extended-Persona Reference Syntax in `composition.yml`

| Field | Value |
|-------|-------|
| **Owner** | architect |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-30 23:39 |
| **Completed** | 2026-04-30 23:41 |
| **Duration** | 2m |

## Goal

Decide and record the reference syntax for **extended** personas in
`composition.yml`. Two finalist forms:

- **A.** Tier-prefixed: `extended/security-engineer` (and core personas
  always referenced bare: `developer`).
- **B.** Bare names with implicit two-directory scan:
  `security-engineer` (loader scans both `core/` and `extended/`,
  resolving without ambiguity).

Pick one and write the ADR. Cover loader behavior, error messaging when an
unknown or wrong-tier name is referenced, and migration impact for
existing example compositions.

## Inputs

- `ai/beans/BEAN-271-library-persona-tiering/bean.md` — bean spec
  (especially the **Notes** section: "Architect required" call-out).
- `ai/context/decisions.md` — append the new ADR after ADR-013. The
  next number is **ADR-014**.
- `examples/foundry-dogfood.yml`, `examples/full-stack-web.yml`,
  `examples/security-focused.yml`, `examples/small-python-team.yml` —
  current persona references.
- `foundry_app/services/library_indexer.py` (`_scan_personas`) — for
  context on the loader you're constraining.

## Acceptance Criteria

- [ ] ADR-014 appended to `ai/context/decisions.md` with the standard
      sections (Status, Context, Decision, Consequences).
- [ ] Decision is unambiguous (one syntax chosen, alternatives
      explicitly rejected with one-line rationale).
- [ ] Loader behavior specified: how `_scan_personas` should resolve
      references and what error message it emits when a reference is
      invalid or points to the wrong tier.
- [ ] Migration impact documented for the 4 example compositions in
      `examples/` (which need edits, which don't).
- [ ] No code changes in this task — design only. Developer (Task 02)
      implements the chosen syntax.

## Definition of Done

- ADR committed to `ai/context/decisions.md`.
- Status set to `Done`.
- Decision is concrete enough that the Developer task can implement it
  without further clarification.
