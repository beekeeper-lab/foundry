# Task 01: Create VDD Policy Document & Update Team Docs

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-17 03:41 |
| **Completed** | 2026-02-17 03:43 |
| **Duration** | 2m |

## Goal

Create the Verification-Driven Development (VDD) policy document in `ai/context/vdd-policy.md` and update existing team documentation to reference VDD verification gates.

## Inputs

- `ai/context/bean-workflow.md` — current bean workflow (add VDD reference)
- `.claude/agents/tech-qa.md` — Tech-QA agent (add VDD checklist)
- `.claude/agents/team-lead.md` — Team Lead agent (add VDD compliance check)
- `ai/beans/BEAN-142-vdd-policy/bean.md` — bean acceptance criteria

## Acceptance Criteria

- [ ] `ai/context/vdd-policy.md` exists with:
  - Clear definition of VDD and its purpose
  - Verification requirements per bean category (App, Process, Infra)
  - Concrete verification evidence types (test results, lint output, document review)
  - Category-specific verification steps
- [ ] `ai/context/bean-workflow.md` updated:
  - Section 6 (Verification) references VDD policy
  - VDD gate mentioned in Section 7 (Closure) as a prerequisite
- [ ] `.claude/agents/tech-qa.md` updated:
  - VDD verification checklist added to Operating Principles or a new section
  - Category-specific verification responsibilities documented
- [ ] `.claude/agents/team-lead.md` updated:
  - "Closing a bean" section includes VDD compliance check
  - Reference to VDD policy document added

## Definition of Done

- All four files exist/updated with VDD content
- No broken markdown formatting
- Cross-references between documents are consistent
