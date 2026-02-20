# Task 01: Add Bottleneck Check Step to Bean Workflow

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-17 04:01 |
| **Completed** | 2026-02-17 04:03 |
| **Duration** | 2m |
| **Tokens** | — |

## Goal

Add a "Bottleneck Check" step to the bean workflow that the Team Lead performs during decomposition, before execution begins. This step systematically identifies sequential dependencies, shared resource contention, and parallelization opportunities.

## Inputs

- `ai/context/bean-workflow.md` — current workflow definition
- `.claude/agents/team-lead.md` — Team Lead agent instructions
- `ai/beans/BEAN-144-bottleneck-check/bean.md` — bean requirements

## Acceptance Criteria

- [x] A "Bottleneck Check" subsection is added to the Decomposition phase in `ai/context/bean-workflow.md`
- [x] The check covers: sequential dependencies, shared resource contention, parallelization opportunities
- [x] Mitigation strategies are documented for each bottleneck category
- [x] The Team Lead agent instructions reference the bottleneck check step
- [x] Changes are minimal and integrate naturally with existing workflow

## Definition of Done

- `ai/context/bean-workflow.md` contains a bottleneck check step in the decomposition section
- `.claude/agents/team-lead.md` references the bottleneck check during decomposition
- No existing workflow steps are broken or contradicted
