# Task 01: Add Rule Extraction Step to Bean Closure

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

Add a rule extraction step to the bean closure process. After a bean is marked Done, the Team Lead should extract recurring patterns, anti-patterns, and lessons learned and record them in MEMORY.md or a designated context doc.

## Inputs

- `.claude/agents/team-lead.md` — Team Lead agent instructions (closure workflow)
- `ai/context/bean-workflow.md` — Bean lifecycle specification (closure section)

## Changes Required

1. Add a new step to the "Closing a bean" section in `.claude/agents/team-lead.md` that instructs the Team Lead to extract rules after closure
2. Add a corresponding step to the "Closure" section in `ai/context/bean-workflow.md`
3. Keep changes minimal — add the extraction step without restructuring existing content

## Definition of Done

- [x] Rule extraction step added to Team Lead agent closure workflow
- [x] Rule extraction step added to bean-workflow.md closure section
- [x] Step specifies how to identify patterns (recurring issues, anti-patterns, lessons learned)
- [x] Step specifies where to store extracted rules (MEMORY.md or context docs)
- [x] Existing workflow steps are not broken or reordered
- [x] Changes are minimal and focused
