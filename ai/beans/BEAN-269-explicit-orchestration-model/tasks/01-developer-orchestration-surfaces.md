# Task 01: Implement Orchestration Model Surfaces

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-17 18:48 |
| **Completed** | 2026-04-17 18:48 |
| **Duration** | ~20m |

## Goal

Make the team orchestration model explicit in **three** surfaces of a
freshly generated project, so a cold-start agent can read the model
from artifacts alone:

1. `CLAUDE.md` — a **Team Orchestration Model** section immediately
   after the Team roster, stating the four-bullet policy.
2. `.claude/agents/team-lead.md` — an **Orchestration Rules** section
   stated operationally (via the library source persona file).
3. `ai/team/composition.yml` — a structured `orchestration:` block
   emitted at scaffold time.

Also audit library skill/command wording for phrases that contradict
the bench model.

## Inputs

- `foundry_app/services/compiler.py` — `_build_lean_claude_md`
- `ai-team-library/personas/team-lead/persona.md` — persona source
- `foundry_app/services/scaffold.py` — composition emit site
- `foundry_app/io/composition_io.py` — `save_composition`
- `ai-team-library/claude/skills/long-run/SKILL.md` — wording audit
- `ai-team-library/claude/commands/long-run.md` — wording audit

## Changes Required

1. **CLAUDE.md — Team Orchestration Model section.** Extend
   `_build_lean_claude_md` in `compiler.py` to append a `## Team
   Orchestration Model` section after the Team roster with the four
   bullets: orchestrator, available bench, mandatory Developer +
   Tech-QA for software development, opt-in specialists. Emit the
   section even when no personas are selected (reviewer-facing
   policy is always valid).
2. **Team Lead persona Orchestration Rules.** Add an
   `## Orchestration Rules` section to
   `ai-team-library/personas/team-lead/persona.md` stating the policy
   in operational imperatives (restate four bullets + name the
   always-on and opt-in roles explicitly).
3. **composition.yml `orchestration:` block.** Append a static
   `orchestration:` YAML block after the serialized spec in
   `scaffold.py` (or tee it through `save_composition`) with the
   shape proposed in the bean. Keep the field as a dict literal so
   downstream consumers can read it. Document in bean Notes that
   this is a static policy block (not model-driven) for v1.
4. **Audit library wording.** Replace "full team wave" in
   `ai-team-library/claude/skills/long-run/SKILL.md` and
   `ai-team-library/claude/commands/long-run.md` with wording that
   doesn't imply every persona is engaged (e.g. "through the team
   wave" or "through the assigned wave"). Do not change wave model
   behavior.

## Acceptance Criteria

- [ ] Generated `CLAUDE.md` contains a `## Team Orchestration Model`
      heading and the four-bullet policy text.
- [ ] `.claude/agents/team-lead.md` (via regenerated member file /
      library source) contains `## Orchestration Rules` section with
      operational imperatives.
- [ ] Generated `ai/team/composition.yml` contains an
      `orchestration:` block with `orchestrator_role`, `team_model`,
      `required_roles.software-development`, and `optional_roles`.
- [ ] `rg -i "full team wave|all members active|entire team active"`
      over the generated project returns no contradicting matches.
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check foundry_app/` passes.

## Definition of Done

- Compiler appends the Team Orchestration Model section.
- Team-lead persona source has an Orchestration Rules section.
- Scaffold emits an `orchestration:` block in composition.yml.
- Library wording audited and corrected.
- Full test suite passes, lint clean.
