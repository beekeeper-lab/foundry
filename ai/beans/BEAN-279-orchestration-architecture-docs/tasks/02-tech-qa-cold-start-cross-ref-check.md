# Task 02: Cold-Start Verification — Cross-References, Checklist Coverage, Generated-Project Spot-Check

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Independently verify the documentation sweep landed coherently:

- Read the new `orchestration-architecture.md` cold and confirm any
  reader (human or fresh agent) would understand the cluster's
  architecture without supervisor clarification.
- Verify cross-references resolve (every doc-to-doc link points to
  a real anchor; every bean reference names a real bean).
- Spot-check a generated project's CLAUDE.md + agent files + skill
  docs read coherently and consistently with the new orchestration
  model.
- Verify MEMORY.md's documentation checklist update landed and the
  CHANGELOG.md entry is present.

## Inputs

- The artifacts the Developer (Task 01) produced — read what's there:
  - `ai/context/orchestration-architecture.md` (new)
  - `ai/context/decisions.md` (new ADR-015 at the bottom)
  - `CLAUDE.md`, `README.md`, `ai/context/bean-workflow.md`,
    `ai/context/project.md`
  - `.claude/agents/{team-lead, ba, architect, developer, tech-qa}.md`
  - `.claude/skills/long-run/SKILL.md`,
    `.claude/commands/long-run.md`
  - `CHANGELOG.md`
  - `ai-team-library/README.md`
  - MEMORY.md at the absolute path noted in the bean spec
- One generated example project for the spot-check: pick the
  smallest example that exercises the new orchestration features.
  Run a generation against `examples/small-python-team.yml` (or
  any compositions that includes the right personas/contracts).
  Inspect the generated `CLAUDE.md` and `.claude/agents/*.md` for
  consistency with the orchestration narrative.

## Acceptance Criteria

- [ ] Cold-start review of `orchestration-architecture.md`: a fresh
      reader can understand the three principles, the evaluation
      methodology, and how a bean flows under the new architecture.
      Note any ambiguities in your report rather than fixing them.
- [ ] Cross-reference check: every doc-to-doc link in the new doc and
      in the swept docs resolves; every bean reference names a real
      bean. Use grep to find `BEAN-NNN` references in the swept docs
      and confirm the IDs exist in `ai/beans/_index.md`.
- [ ] MEMORY.md's documentation checklist now includes
      `ai/context/orchestration-architecture.md`.
- [ ] `CHANGELOG.md` has a v1.1.0 (or chosen version) entry naming
      the orchestration cluster.
- [ ] Generated-project spot-check: run `uv run foundry-cli generate
      examples/small-python-team.yml --library ai-team-library`
      against a temp output directory and skim the generated
      `CLAUDE.md` for consistency with the orchestration narrative.
      Note any inconsistencies.
- [ ] `uv run pytest` passes (full suite).
- [ ] `uv run ruff check foundry_app/` clean.

## Definition of Done

- Cold-start review report delivered in the supervisor handback.
- Cross-reference check report delivered.
- Spot-check report delivered.
- Status set to `Done`.

## Notes

**Verify, don't re-write.** If you find a doc inconsistency or a
broken cross-reference, **stop and report** rather than fix. Light
factual corrections (a wrong line number, a missing comma) can be
fixed inline; substantive content edits should be a follow-up.

**Cluster closure.** This is the last bean of the BEAN-269..279
cluster. Be especially attentive to whether the new documentation
*matches the code* — drift between the two is the worst failure
mode for a documentation bean.

**Do not destroy real artifacts.** The generated-project spot-check
must use a `tmp_path` or `/tmp/` output directory, not a real
project location.

**Light-touch testing.** No new Python tests required — the
acceptance is documentation-quality. The pytest pass is just to
confirm no doc-induced breakage.
