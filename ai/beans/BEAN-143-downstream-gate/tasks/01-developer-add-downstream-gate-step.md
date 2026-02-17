# Task 01: Add Downstream Gate Step to Backlog Refinement Skill

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-17 04:02 |
| **Completed** | 2026-02-17 04:02 |
| **Duration** | < 1m |

## Goal

Add a "Downstream Gate" step to the backlog-refinement skill (`/.claude/skills/backlog-refinement/SKILL.md`). The step must require listing downstream systems impacted by each proposed bean and explicit verification commands for each.

## Inputs

- `ai/beans/BEAN-143-downstream-gate/bean.md` — Bean definition with acceptance criteria
- `.claude/skills/backlog-refinement/SKILL.md` — Current backlog-refinement skill to modify

## Definition of Done

- [x] A new "Downstream Gate" phase/step is added to the backlog-refinement skill's Process section
- [x] The step requires listing impacted downstream systems (tests, CI, build, deployment, docs, migrations, monitoring)
- [x] Each impacted system must have an explicit verification command
- [x] Missing verifications are flagged and must be added before proceeding
- [x] The change is minimal and focused — no unnecessary refactoring
- [x] Existing phases and steps remain intact and unbroken
