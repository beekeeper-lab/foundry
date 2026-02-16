# Task 001: Add Seed Task Templates for 8 Missing Personas

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-129-T001 |
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Description

Add entries to both `_DETAILED_TASKS` and `_KICKOFF_TASKS` dictionaries in `foundry_app/services/seeder.py` for these 8 personas:

1. `code-quality-reviewer` — Code review, standards enforcement, PR feedback
2. `devops-release` — CI/CD pipelines, deployment, release management
3. `security-engineer` — Threat modeling, security review, vulnerability assessment
4. `compliance-risk` — Regulatory mapping, compliance evidence, audit documentation
5. `researcher-librarian` — Research memos, decision matrices, knowledge base
6. `technical-writer` — READMEs, runbooks, API docs, user guides
7. `ux-ui-designer` — Wireframes, component specs, interaction flows, UX criteria
8. `integrator-merge-captain` — Merge strategy, integration validation, release notes

Each persona gets 2-3 detailed tasks and 1 kickoff task, following the same pattern as the existing 5 personas.

## Acceptance Criteria

- [ ] All 8 personas added to `_DETAILED_TASKS` with 2-3 tasks each
- [ ] All 8 personas added to `_KICKOFF_TASKS` with 1 task each
- [ ] Tasks are meaningful and aligned with each persona's role
