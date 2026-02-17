# Task 01: Document Blast Radius Budget

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-17 04:08 |
| **Completed** | 2026-02-17 04:08 |
| **Duration** | < 1m |

## Goal

Add a "Blast Radius Budget" concept to the bean workflow documentation and backlog-refinement skill. Define metrics, guideline thresholds, and a check that flags beans exceeding the budget for decomposition.

## Inputs

- `ai/context/bean-workflow.md` — current bean lifecycle (especially §4 Molecularity Gate)
- `.claude/skills/backlog-refinement/SKILL.md` — backlog refinement process
- `ai/beans/BEAN-152-blast-radius-budget/bean.md` — bean definition

## Outputs

- Updated `ai/context/bean-workflow.md` with Blast Radius Budget section
- Updated `.claude/skills/backlog-refinement/SKILL.md` with budget check in the iteration phase

## Definition of Done

- [x] Blast Radius Budget concept is defined with clear metrics (files changed, systems touched, lines modified)
- [x] Guideline thresholds are specified (e.g., <=10 files, <=1 system boundary)
- [x] A check step is added to backlog-refinement that flags beans exceeding the budget
- [x] The molecularity gate in bean-workflow.md references the blast radius budget
- [x] Changes are minimal and don't disrupt existing documentation structure
