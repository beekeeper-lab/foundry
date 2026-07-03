# SPEC-017: Extend typed contracts to extended personas

- **Priority:** P1
- **Effort:** L
- **Area:** library
- **Depends on:** none (amplified by SPEC-008; SPEC-007 fixes the stale template paths referenced here)
- **Status:** Proposed

## Problem

The typed-contract system (ADR-013: `produces`/`consumes` per persona, compose-time graph validation, typed `/handoff` packets) covers only the 5 core personas. The other **20 extended personas** (note: audit reports said 19; the directory contains 20) have no `contracts.yml`, and the handoff skill *hard-codes* the core five as the only legal endpoints — so any wave including a security engineer, merge captain, or designer **cannot** emit a typed handoff even by hand. The artifact registry also has holes: four types have no backing template, there is no `code-review` artifact type for the Code Quality Reviewer's ship/no-ship output, the task-spec template's field names diverge from the registry's required-fields, and the `acceptance-criteria` dual-producer (BA + team-lead) rule lives only in prose.

## Evidence

- `ls ai-team-library/personas/extended/*/contracts.yml` — zero matches; all 20 extended personas lack one (core five have them).
- `ai-team-library/claude/skills/handoff/SKILL.md:220-221` — `FromPersonaNotFound`/`ToPersonaNotFound`: "Use one of `team-lead, ba, architect, developer, tech-qa`".
- `ai-team-library/contracts/artifact-types.yml:113,126,245,260` — `template-path: null` for `scope-definition`, `risk-register`, `handoff-packet`, `merge-summary`; team-lead's `contracts.yml` declares `produces: merge-summary` with no template anywhere.
- No `code-review` entry in `artifact-types.yml` despite Code Quality Reviewer being a first-class reviewer role.
- `ai-team-library/contracts/artifact-types.yml:66-72` requires `goal`, `depends-on`; the backing template `personas/core/team-lead/templates/task-spec.md:20,38` uses `## Objective` and `## Dependencies`.
- `ai-team-library/personas/core/ba/contracts.yml:7` — AC dual-producer "active-producer pick is BEAN-274"; the rule exists only as prose in `team-lead/persona.md:106-116`.
- `orchestration-architecture.md:433-434` concedes extended personas are uncovered.

## Proposed change

1. **Author `contracts.yml` for all 20 extended personas.** Derive `produces` from each persona's existing `outputs.md` deliverables; map each to a registry artifact type (adding types where genuinely new — see 3). `consumes` from each persona's "Collaboration & Handoffs" table. Keep them small: 2–4 produces, 1–3 consumes each.
2. **Lift the core-five restriction.** `handoff/SKILL.md`: resolve personas by scanning `personas/{core,extended}/<id>/contracts.yml` (ADR-014 reference form `extended/<id>`), and update error text at `:220-221`. Same change in any validator path that enumerates the core five.
3. **New artifact types.** At minimum: `code-review` (producer: code-quality-reviewer; required-fields: verdict, findings, scope) and `threat-model` (producer: security-engineer) if absent. Add templates for the four `template-path: null` types — `handoff-packet` and `merge-summary` under `personas/core/team-lead/templates/`, `scope-definition` under `personas/core/ba/templates/`, `risk-register` under `personas/extended/compliance-risk/templates/`.
4. **Align task-spec fields.** The registry is canonical: rename template headings `## Objective` → `## Goal`, `## Dependencies` → `## Depends On`, and update the two seeded-task renderers if they emit the old headings (`foundry_app/services/seeder.py`). One convention, both directions.
5. **Codify the AC active-producer rule** in `contracts/artifact-types.yml` under the `acceptance-criteria` entry: `active-producer: ba-when-present, else team-lead`, and make `validate_contract_graph` (`foundry_app/services/validator.py:336-502`) implement it instead of tolerating the ambiguity.
6. **Contract-graph validation covers extended personas** automatically once (1) lands; add a validator test with a mixed core+extended team whose graph only closes via an extended producer.

## Out of scope

- Making `/handoff` mechanically enforced (SPEC-008).
- Body-schema (required-fields) enforcement of artifact files — remains advisory; a future spec may add it to `/vdd`.
- Scope-boundary sections for extended personas (worthwhile, but a content pass, not a contract change).

## Acceptance criteria

- [ ] `test:` `ls ai-team-library/personas/extended/*/contracts.yml | wc -l` equals 20.
- [ ] `file-contains:` `ai-team-library/contracts/artifact-types.yml` contains `code-review` and zero `template-path: null` entries.
- [ ] `file-contains:` `ai-team-library/claude/skills/handoff/SKILL.md` no longer contains the literal list restriction "Use one of `team-lead, ba, architect, developer, tech-qa`".
- [ ] `file-contains:` `personas/core/team-lead/templates/task-spec.md` contains `## Goal` and `## Depends On`.
- [ ] `test:` validator test passes where a team's contract graph closes through an extended persona's `produces`.
- [ ] `test:` validator flags a dual-producer AC conflict per the codified active-producer rule.
- [ ] `test:` `uv run pytest` passes.
- [ ] `manual:` `/handoff` from `developer` to `extended/security-engineer` produces a typed packet in a scratch project.

## Files to touch

- `ai-team-library/personas/extended/*/contracts.yml` (20 new files)
- `ai-team-library/contracts/artifact-types.yml`
- `ai-team-library/claude/skills/handoff/SKILL.md` (and kit mirror `.claude/shared/skills/`)
- `ai-team-library/personas/core/{team-lead,ba}/templates/`, `personas/extended/compliance-risk/templates/`
- `foundry_app/services/validator.py`, `seeder.py`
- `tests/` (contract-graph and handoff tests)
