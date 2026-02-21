# Task 01: Update All Workflow Files for Trunk-Based Development

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-21 17:48 |
| **Completed** | 2026-02-21 17:55 |
| **Duration** | 7m |

## Goal

Replace all `test` branch references with `main` across skills, commands, agents, library templates, workflow docs, and memory files.

## Inputs

- Exploration results listing all files with `test` branch references

## Files to Update

### Foundry Local (.claude/)
1. `.claude/skills/long-run/SKILL.md` — Phase 0 check main not test; merge targets main
2. `.claude/commands/long-run.md` — Phase 0, merge steps, final message
3. `.claude/skills/internal/merge-bean/SKILL.md` — default target main
4. `.claude/commands/internal/merge-bean.md` — all test→main
5. `.claude/skills/deploy/SKILL.md` — repurpose as tag/release only
6. `.claude/commands/deploy.md` — remove test→main promotion, keep as tag tool
7. `.claude/agents/team-lead.md` — branch references
8. `.claude/commands/internal/spawn-bean.md` — worktree branch references

### Library Templates (ai-team-library/claude/)
9. `ai-team-library/claude/skills/long-run/SKILL.md` — mirror local changes
10. `ai-team-library/claude/commands/long-run.md` — mirror local changes
11. `ai-team-library/claude/skills/merge-bean/SKILL.md` — mirror local changes
12. `ai-team-library/claude/commands/merge-bean.md` — mirror local changes
13. `ai-team-library/claude/commands/spawn-bean.md` — mirror local changes
14. `ai-team-library/claude/commands/deploy.md` — mirror local changes

### Docs & Context
15. `ai/context/bean-workflow.md` — remove integration branch concept
16. `docs/long-run-deep-dive.md` — update workflow diagrams
17. `docs/backlog-refinement-deep-dive.md` — update workflow references
18. `CLAUDE.md` — update if test branch mentioned
19. MEMORY.md — update bean workflow notes

## Acceptance Criteria

- [ ] No workflow file references `test` as a merge target
- [ ] `/long-run` requires `main` branch, not `test`
- [ ] `/merge-bean` defaults to `main`
- [ ] `/deploy` repurposed as tag/release tool
- [ ] Library templates mirror all local changes

## Definition of Done

All files updated. No stale `test` branch workflow references remain.
