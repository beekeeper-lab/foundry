# Task 01: Fix Library Skill Templates for Worktree Merge Loop

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-21 16:46 |
| **Completed** | 2026-02-21 16:48 |
| **Duration** | 2m |

## Goal

Fix three library template files so that generated sub-apps have a working parallel worktree merge flow. The orchestrator must run a persistent dashboard loop that monitors worker status, merges completed branches, re-reads the backlog, and spawns replacements on every iteration.

## Inputs

- `ai-team-library/claude/skills/long-run/SKILL.md` — current library long-run skill
- `ai-team-library/claude/commands/long-run.md` — current library long-run command
- `ai-team-library/claude/commands/spawn-bean.md` — current library spawn-bean command
- `.claude/skills/long-run/SKILL.md` — Foundry's working reference (Parallel Phase 4)
- `.claude/commands/internal/spawn-bean.md` — Foundry's working reference (Step 4)

## Changes Required

### 1. `ai-team-library/claude/skills/long-run/SKILL.md`

Replace "Parallel Phase 4: Dashboard Monitoring" with "Parallel Phase 4: Continuous Assignment Dashboard Loop":
- Rename section header
- Add preamble: "The main window enters a persistent dashboard loop..."
- Restructure into clear per-iteration steps (read status → process completed workers → assign replacements → render dashboard → alert → check exit → sleep)
- Explicitly describe merge sub-steps: remove worktree, sync, merge, update index, mark merged
- Add fresh re-read instruction for replacement assignment
- Add explicit exit condition: "only when both: all done/merged AND no approved beans remain"
- Add loop termination note

### 2. `ai-team-library/claude/commands/long-run.md`

Update "Bean assignment rules" and "Progress monitoring — dashboard loop" sections:
- Make it explicit that the dashboard loop is the merge + assignment mechanism, not just a passive monitor
- Clarify the merge sequence happens as part of each loop iteration
- Add explicit exit condition

### 3. `ai-team-library/claude/commands/spawn-bean.md`

Restructure Step 4 to integrate merge handling into the dashboard loop:
- Move "Worker completion — orchestrator merge" from a separate section INTO the dashboard loop steps
- Add merge as an explicit per-iteration step (between reading status and rendering dashboard)
- Add replacement assignment as a loop step
- Add explicit exit condition

## Acceptance Criteria

- [ ] Library long-run SKILL.md Parallel Phase 4 matches Foundry's "Continuous Assignment Dashboard Loop" structure
- [ ] Library long-run command's parallel section clearly describes the persistent merge+assign loop
- [ ] Library spawn-bean command's Step 4 integrates merge into the dashboard loop iteration
- [ ] All three files are internally consistent (same vocabulary, same patterns)
- [ ] No changes to Foundry's own templates (`.claude/`)

## Definition of Done

All three library template files updated with the correct orchestrator merge loop pattern.
