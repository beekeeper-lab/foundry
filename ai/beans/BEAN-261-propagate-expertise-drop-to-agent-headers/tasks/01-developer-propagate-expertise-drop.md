# Task 01: Propagate Expertise Drop to Agent Headers and Member Files

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-17 18:21 |
| **Completed** | 2026-04-17 18:21 |
| **Duration** | < 1m |

## Goal

Extend the BEAN-247 drop so that missing-source expertise is filtered
from **every** generated artifact that references it — not just
`CLAUDE.md`. Specifically, `.claude/agents/<persona>.md` headers and
`ai/generated/members/<persona>.md` expertise-context blocks must list
only expertise whose source file was written.

## Inputs

- `foundry_app/services/compiler.py` — `_build_context`, `compile_project`
- `foundry_app/services/agent_writer.py` — `write_agents`
- `foundry_app/templates/agent.md.j2` — agent file template
- `tests/test_compiler.py`, `tests/test_agent_writer.py` — existing tests

## Changes Required

1. Add a helper in `compiler.py` to compute the emitted-expertise ID list
   from the spec + library index (an expertise whose `conventions.md`
   exists).
2. Extend `_build_context` / `_build_persona_context` to accept the
   emitted-expertise list and use it when substituting
   `{{ expertise | join(", ") }}` into persona / prompts sources.
3. Update `compile_project` to compute the emitted-expertise list **before**
   compiling persona sections so member files don't reference missing
   expertise.
4. Update `write_agents` so `expertise_names` (and the derived
   `primary_expertise` used to build `role_name`) reflect only emitted
   expertise.
5. Do not change `ai/team/composition.yml` emission — that file records
   the user's input spec and is intentionally unfiltered (documented in
   bean Notes).
6. Keep the existing warning behaviour — every missing expertise still
   produces a warning via `StageResult.warnings`.

## Acceptance Criteria

- [ ] Every generated `.claude/agents/<persona>.md` header lists only
      expertise whose source file was written.
- [ ] Every generated `ai/generated/members/<persona>.md` references
      only expertise whose source file was written, including the
      `{{ expertise | join(", ") }}` substitution in persona prose.
- [ ] `ai/team/composition.yml` still records the user's input spec
      as-is (recorded decision — see bean Notes).
- [ ] Missing-expertise warnings are still emitted.
- [ ] New unit tests cover the agent-header and member-file invariants.
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check foundry_app/` passes.

## Definition of Done

- Code changes land in compiler.py and agent_writer.py.
- New tests verify the invariants for both agent files and member files.
- Full test suite passes.
- Lint clean.
