# Task 01: Wire Merge Captain into Bean Execution Wave

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Add the Merge Captain as the final stage in the bean execution wave. Update the `/long-run` skill, create a `/merge-bean` command and skill, and update the integrator-merge-captain agent.

## Inputs

- `ai/beans/BEAN-011-merge-captain-auto-merge/bean.md` — acceptance criteria and safe merge sequence
- `.claude/skills/long-run/SKILL.md` — skill to update with Merge Captain stage
- `.claude/agents/team-lead.md` — agent to update with merge references
- `ai-team-library/personas/integrator-merge-captain/persona.md` — existing persona reference

## Implementation

1. **`.claude/commands/merge-bean.md`**: New command for merging a single bean's feature branch into `test`
2. **`.claude/skills/merge-bean/SKILL.md`**: New skill with safe merge sequence (checkout test → pull → merge → push)
3. **`.claude/skills/long-run/SKILL.md`**: Add Merge Captain as Phase 5.5 (after verification, before commit-on-branch step in sequential; after worker completion in parallel)
4. **`.claude/agents/team-lead.md`**: Add `/merge-bean` to Skills & Commands table

## Acceptance Criteria

- [ ] `/merge-bean` command and skill created
- [ ] Safe merge sequence documented (checkout test, pull, merge, push)
- [ ] Conflict handling documented (report and stop)
- [ ] `/long-run` skill updated with Merge Captain as final stage
- [ ] Team Lead agent updated with `/merge-bean` reference
- [ ] Works for both sequential and parallel modes
- [ ] Format matches existing command/skill patterns

## Definition of Done

Command, skill, and agent files updated. Merge Captain wired into the execution wave.
