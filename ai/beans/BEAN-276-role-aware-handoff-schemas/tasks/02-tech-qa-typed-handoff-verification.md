# Task 02: Verify Typed `/handoff` — Cold-Start Walkthrough + Registry/Index Tests

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-05-01 00:58 |
| **Completed** | 2026-05-01 01:00 |
| **Duration** | 2m |

## Goal

Independently verify the new typed `/handoff` skill: walk through it
cold (as if you were a persona reading it for the first time), check
that the registry's `pair-fields` schema is parseable, validate the
example handoff demonstrates the format end-to-end, and ensure
`ai/handoffs/_index.md` exists. Add tests where Python code can be
involved (registry parsing) — the skill spec itself is markdown and
will be reviewed for clarity, not unit-tested.

## Inputs

- `ai/beans/BEAN-276-role-aware-handoff-schemas/bean.md` — bean spec.
- The artifacts the Developer (Task 01) just produced — read what's
  there, don't assume:
  - `ai-team-library/claude/skills/handoff/SKILL.md`
  - `ai-team-library/claude/commands/handoff.md`
  - `ai-team-library/contracts/artifact-types.yml` (esp. new `pair-fields:` section)
  - `ai-team-library/personas/core/*/persona.md` (typed-handoff
    references)
  - `ai/handoffs/_index.md`
  - `ai/handoffs/<example-handoff>.md`
- `foundry_app/services/library_indexer.py` — `_load_persona_contracts`
  (around line 124). The skill references its data shape; verify the
  reference is accurate.
- `tests/test_persona_contracts.py` — existing contract tests; the
  pattern for any new registry-shape test you add.

## Acceptance Criteria

- [ ] Cold-start review: read the new SKILL.md fresh and confirm any
      persona could produce a typed packet from the spec without
      needing to ask the supervisor for clarification. Note any
      ambiguities in your report rather than fixing them silently.
- [ ] Registry test: a new test (likely in
      `tests/test_persona_contracts.py` or a new
      `tests/test_artifact_types_registry.py`) loads
      `ai-team-library/contracts/artifact-types.yml` and asserts the
      `pair-fields:` section is well-formed (each entry has `from`,
      `to`, `extras`).
- [ ] Verify the example handoff is valid against the spec: every
      required field for the artifacts in the sender's-`produces` ∩
      receiver's-`consumes` intersection is present, plus any pair-fields
      extras for that edge.
- [ ] `ai/handoffs/_index.md` exists with the documented schema
      (header + table with `| Date | From | To | Bean | Packet |`).
- [ ] If the Developer's blocking-validation step (sender hasn't
      produced a required artifact) is described unambiguously in the
      spec — confirm it. If the description is vague, file as a
      finding rather than fixing.
- [ ] `uv run pytest` passes (full suite).
- [ ] `uv run ruff check foundry_app/` clean.

## Definition of Done

- Cold-start review report appended to the bean as a note (or
  delivered in the supervisor handback).
- Registry/example tests added and passing.
- Full pytest suite green.
- Status set to `Done`.

## Notes

**Verify, don't re-implement.** If you find the SKILL.md is unclear,
or the example handoff is missing required fields, **stop and report
rather than fix**. The Developer owns the spec; Tech-QA verifies and
surfaces gaps.

**Coverage focus.** The contract this bean adds is: every
sender/receiver pair gets a typed packet whose shape is determined by
the registry. Tests should make that contract break loudly if a
future change weakens it (registry shape, missing example field,
broken intersection logic in the spec).

**Light-touch testing.** No need to write Python tests for behaviors
that are *only* expressible in the markdown spec. The registry shape
is testable; the spec's intersection logic is not (it's executed by
personas at runtime, not by code). Don't over-fit.
