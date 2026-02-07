# Task 01: Design Communication Template

| Field | Value |
|-------|-------|
| **Owner** | team-lead |
| **Status** | Done |
| **Depends On** | — |

## Goal

Design the structured communication template that the Team Lead uses during bean processing. Three sections: Header Block, Task Progress Table, Completion Summary.

## Inputs

- `ai/beans/BEAN-014-team-lead-progress-dashboard/bean.md` — requirements and constraints
- `.claude/agents/team-lead.md` — current agent format

## Acceptance Criteria

- [ ] Header Block format defined (bean ID, title, summary)
- [ ] Task Progress Table format defined (columns: #, Task, Owner, Status)
- [ ] Output ordering rules defined (header+table top, work below, prompts bottom)
- [ ] Re-presentation rules defined (when to reprint)
- [ ] Completion Summary format defined (for merge captain handoff)
- [ ] Fits within ~100 column width constraint
- [ ] Template written to `ai/outputs/team-lead/bean-014-communication-template.md`

## Definition of Done

Template design document exists with all three sections fully specified.
