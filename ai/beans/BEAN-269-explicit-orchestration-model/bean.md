# BEAN-269: Make Team Orchestration Model Explicit in Generated Artifacts

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-269 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

External review (2026-04-17, second pass): "The orchestration model is
still not explicit enough. A reader can still come away with one of
these mistaken interpretations: all listed team members are active by
default; the Team Lead is vaguely coordinating but not clearly the
assignment authority; role participation is ad hoc rather than
rule-based."

Our **intent** is a specific operating model:

- The Team Lead is the orchestrator.
- The generated team roster is an **available bench of specialists**,
  not an always-active squad.
- For software development work, **Developer and Tech-QA are mandatory**
  on every bean.
- All other specialists (Architect, UX/UI Designer, Integrator Merge
  Captain, BA, and any additional personas on the bench) are
  **opt-in** — the Team Lead assigns them only when the bean or task
  needs them.

This model is captured internally (`MEMORY.md`, BEAN-228, BEAN-229,
agent activation sections), but it is not stated plainly enough in the
**generated project** for a cold-start reviewer to see it. The
reviewer's updated assessment raised the score from 6/10 to 8.4/10
after the intent was explained verbally — evidence that the intent is
sound but its surfacing is weak.

## Goal

A cold-start agent opening a freshly generated project can read the
orchestration model from the generated artifacts alone — no verbal
explanation required. The model is stated in at least three
surfaces, consistent in each:

1. `CLAUDE.md` — short project-level **Team Orchestration Model**
   section with the four-bullet policy.
2. `.claude/agents/team-lead.md` — an **Orchestration Rules** section
   that is operational (what the Team Lead does, in imperatives).
3. `ai/team/composition.yml` (or adjacent machine-readable config) —
   a structured orchestration block that encodes the policy.

## Scope

### In Scope
- Update the generated `CLAUDE.md` template / compiler output to include
  a **Team Orchestration Model** section immediately after the Team
  roster. Content matches the reviewer's suggested wording:
  - Team Lead is the orchestrator.
  - Team roster is an available bench, not always-active.
  - Developer + Tech-QA are mandatory for software development.
  - Architect, UX/UI Designer, Integrator Merge Captain, and any other
    specialists are opt-in per bean or task needs.
- Update `ai-team-library/personas/team-lead/persona.md` (the library
  source) to add an **Orchestration Rules** section stated
  operationally. Regeneration propagates this to
  `.claude/agents/team-lead.md` in downstream projects.
- Decide whether `ai/team/composition.yml` gets a machine-readable
  `orchestration:` block at emit time. Proposed shape:
  ```yaml
  orchestration:
    orchestrator_role: team-lead
    team_model: available-bench
    required_roles:
      software-development:
        - developer
        - tech-qa
    optional_roles:
      - architect
      - ux-ui-designer
      - integrator-merge-captain
      - ba
  ```
  If implementation cost is high, defer the YAML block as a follow-up
  and land the prose-only change first.
- Audit existing skills/commands/hook docs for wording that implies
  "all personas are active by default" and correct it. Candidates to
  check:
  - `ai-team-library/claude/skills/long-run/SKILL.md`
  - `ai-team-library/claude/skills/backlog-refinement/SKILL.md`
  - Any command that decomposes work.
  (This overlaps with BEAN-265 — coordinate.)

### Out of Scope
- Changing the wave model itself.
- Rewriting persona files beyond the team-lead orchestration section.
- Adding new personas or activation criteria — BEAN-257 covers that.
- Re-expanding the rest of CLAUDE.md (BEAN-268 covers pointer content;
  this bean adds orchestration content specifically).

## Acceptance Criteria

- [ ] Generated `CLAUDE.md` contains a **Team Orchestration Model**
      section that names the four-bullet policy (orchestrator, bench
      model, mandatory Developer + Tech-QA, opt-in specialists).
- [ ] Generated `.claude/agents/team-lead.md` contains an
      **Orchestration Rules** section that restates the policy in
      operational / imperative terms for the Team Lead persona.
- [ ] Either `ai/team/composition.yml` gains a structured
      `orchestration:` block, or the bean's Notes section documents
      why the YAML form was deferred to a follow-up.
- [ ] A grep of the generated project for "all members", "entire team",
      or "full wave" finds no wording that contradicts the bench model.
- [ ] Cold-start verification: reading only CLAUDE.md, an agent can
      state (a) who assigns tasks, (b) which roles are always on, and
      (c) which roles are opt-in.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Source.** External review, second pass (2026-04-17). Reviewer rated
this the single most important next improvement.

**Related beans.**
- BEAN-228 / BEAN-229 established the Architect/BA engagement rules;
  this bean elevates those rules to the generated project's top-level
  surface.
- BEAN-257 (Activation Rules for Remaining Personas) will round out
  the opt-in list; land after or alongside this bean.
- BEAN-265 (Sync library long-run skill) overlaps — the wave-model
  language in long-run and the orchestration model in CLAUDE.md must
  agree.
- BEAN-268 (Workflow pointers) adds *navigational* content to CLAUDE.md;
  this bean adds *policy* content. Complementary.

**Reviewer's suggested CLAUDE.md wording** (adopt or adapt):

```markdown
## Team Orchestration Model

- **Team Lead is the orchestrator.**
- The listed personas are an **available bench of specialists**, not the
  default active participants for every bean or task.
- For **software development work**, the Team Lead must always assign:
  - **Developer**
  - **Tech-QA**
- Other specialists such as **Architect**, **UX/UI Designer**, and
  **Integrator Merge Captain** are assigned only when the bean or
  task requires them.
- The Team Lead is responsible for selecting beans, decomposing work
  into tasks, assigning the right people, and sequencing the work.
```

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
