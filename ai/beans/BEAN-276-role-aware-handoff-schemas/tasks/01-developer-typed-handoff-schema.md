# Task 01: Implement Typed `/handoff` — Skill Spec, Pair-Fields Registry, Index, Example

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 00:50 |
| **Completed** | 2026-05-01 00:56 |
| **Duration** | 6m |

## Goal

Rewrite the `/handoff` skill (`ai-team-library/claude/skills/handoff/SKILL.md`)
so it reads sender's `produces:` and receiver's `consumes:` from the
contract registry (BEAN-273), computes the intersection, and emits a
typed packet with the registry's `required-fields` per artifact type.
Add a `pair-fields` extension to the artifact-types registry for
sender/receiver pairs that need extras beyond an artifact's defaults.
Make handoffs observable via `ai/handoffs/_index.md`. Land at least
one example handoff under `ai/handoffs/`.

## Inputs

- `ai/beans/BEAN-276-role-aware-handoff-schemas/bean.md` — bean spec.
  Read **Scope — In Scope**, **Acceptance Criteria**, **Notes**.
- `ai-team-library/claude/skills/handoff/SKILL.md` (73 lines) —
  current generic skill; rewrite to be contract-aware.
- `ai-team-library/claude/commands/handoff.md` (20 lines) —
  trigger only; per BEAN-249 keep ≤30 lines.
- `ai-team-library/contracts/artifact-types.yml` (229 lines) —
  artifact type registry. Add a top-level `pair-fields:` map
  alongside `types:`. Schema:
  ```yaml
  pair-fields:
    - from: developer
      to: tech-qa
      extras:
        - test-targets
        - rerun-command
  ```
  Document the extras in the file's header comment.
- `ai-team-library/personas/core/*/persona.md` — five core persona
  files. Add a one-paragraph "Typed Handoffs" section (or update an
  existing handoff section) referencing the new skill flow.
- `foundry_app/services/library_indexer.py` — for context on how
  `produces`/`consumes` are loaded today (`_load_persona_contracts`
  around line 124). The skill's behavioral spec must reference the
  loader's data shape so Tech-QA can verify it.

## Acceptance Criteria

- [ ] `ai-team-library/claude/skills/handoff/SKILL.md` is rewritten
      to read sender's `produces:` and receiver's `consumes:`,
      compute the intersection, and emit a typed packet with the
      registry's `required-fields` per artifact in the intersection.
- [ ] Skill spec includes a "Validate before emitting" step: if the
      sender hasn't actually produced an artifact for a required type
      in the intersection (no file at the expected path under
      `ai/outputs/<from>/`), the handoff is **blocked** with a clear
      error naming the missing artifact type.
- [ ] `ai-team-library/claude/commands/handoff.md` is ≤30 lines —
      thin trigger only (per BEAN-249).
- [ ] `ai-team-library/contracts/artifact-types.yml` has a
      `pair-fields:` section documenting at least one real
      sender/receiver pair (e.g., developer→tech-qa wants
      `test-targets`).
- [ ] Skill spec describes how `pair-fields` extras are merged with
      the artifact-type's `required-fields` to produce the final
      packet schema for a given handoff edge.
- [ ] `ai/handoffs/_index.md` exists with a header and an empty
      table (or a single demo row pointing at the example handoff).
      Schema: `| Date | From | To | Bean | Packet |`.
- [ ] One example handoff lives at `ai/handoffs/<from>-to-<to>-<bean-or-task>.md`
      demonstrating the typed format end-to-end. Use a real recent
      handoff (e.g., developer→tech-qa for BEAN-274 task 02 — the
      contract-validator test sweep) so the example is grounded.
- [ ] Each `ai-team-library/personas/core/*/persona.md` has a section
      (or updated existing section) referencing the new typed
      handoff flow.
- [ ] Lint clean: `uv run ruff check foundry_app/`.

## Definition of Done

- All listed files updated/created.
- Lint clean.
- Status set to `Done`.

## Notes

**No Python code changes are required for the handoff skill itself.**
The skill is a markdown specification followed by personas at
handoff time — the contract-loading code (`_load_persona_contracts`)
already exists from BEAN-273. Your job is to specify the new skill
behavior precisely enough that any persona reading it can produce the
same typed packet.

**Pair-fields schema choice.** The bean's notes call this an
"Architect-required" decision but the bean explicitly leaves Architect
optional. Make the schema choice inline; document the decision in
the registry file's header comment with a one-paragraph rationale (no
ADR needed).

**Example handoff freshness.** Pick a recent real bean's
developer→tech-qa edge (e.g., BEAN-274 contract-validator). Build the
packet from real artifacts the developer would have produced.

**Out of scope:**
- Auto-generating handoff content (the persona authors it; the schema
  defines the shape).
- Renaming the command.
- Handoffs between extended personas (focus on core 5).
- Retroactive handoff generation for past beans (one example is
  enough).
- Python code changes — none needed for the skill itself.
