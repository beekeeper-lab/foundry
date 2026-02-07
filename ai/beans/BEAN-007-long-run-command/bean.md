# BEAN-007: Long Run Command

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-007 |
| **Status** | New |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |

## Problem Statement

Running beans through the team workflow currently requires manual intervention at every step: the user must tell the Team Lead to pick a bean, approve the decomposition, kick off the wave, and then repeat for the next bean. This is tedious when there are multiple beans to process and the user trusts the Team Lead to make good sequencing decisions.

## Goal

Create a `/long-run` command that puts the Team Lead in control of the backlog. The Team Lead autonomously picks the best bean to work on, decomposes it into tasks, runs the full team wave (BA → Architect → Developer → Tech-QA, skipping roles when appropriate), marks the bean as done, and then moves on to the next bean. One bean at a time, sequentially.

## Scope

### In Scope
- `/long-run` command in `.claude/commands/long-run.md`
- Corresponding skill in `.claude/skills/long-run/SKILL.md`
- Team Lead bean selection logic: considers priority, dependencies between beans, and logical ordering (e.g., infrastructure before features)
- Full bean lifecycle per iteration: pick → decompose → execute wave → verify → close
- Progress reporting after each bean completes (summary of what was done)
- Commit after each completed bean
- Graceful handling when backlog is empty (report and stop)
- Single-bean-at-a-time processing (no parallelism)

### Out of Scope
- Parallel bean processing (future enhancement)
- User approval gates between beans (this is autonomous mode)
- Automatic creation of new beans during the run
- Integration with CI/CD or external systems
- Modifying the bean or task file formats

## Acceptance Criteria

- [ ] `/long-run` command exists in `.claude/commands/long-run.md`
- [ ] Skill exists in `.claude/skills/long-run/SKILL.md`
- [ ] Team Lead selects beans based on priority, dependencies, and logical order
- [ ] Each bean goes through the full lifecycle: pick → decompose → wave → verify → close
- [ ] Roles are skipped when not needed (matching existing Team Lead behavior)
- [ ] Progress summary reported after each bean completes
- [ ] Changes committed after each bean completes
- [ ] Stops gracefully when no actionable beans remain
- [ ] Command format matches existing commands
- [ ] Skill format matches existing skills
- [ ] Team Lead agent updated to reference `/long-run`

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| | | | | |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

This command automates the manual loop the user runs today:
1. "team lead pick the next bean"
2. "yes kick off the wave"
3. "ok commit and push"
4. Repeat

**Bean selection heuristics** (Team Lead decides):
- Beans with explicit priority take precedence (High > Medium > Low)
- Dependencies between beans are respected (if BEAN-X depends on BEAN-Y, do Y first)
- Logical ordering applies even without explicit dependencies (infrastructure before features, data models before UI, etc.)
- When priorities and dependencies are equal, process in ID order

**Per-bean flow:**
1. Read `_index.md` — find beans with status `New` or `Picked`
2. Select the best candidate using heuristics above
3. Update status to `Picked` → `In Progress`
4. Decompose into tasks (create task files in `tasks/`)
5. Execute the wave: each persona claims and completes their task(s) in dependency order
6. Verify all acceptance criteria are met
7. Update status to `Done`
8. Commit changes
9. Loop back to step 1

Future iterations could add: parallel bean processing, user checkpoints, automatic bean creation from discovered work, and estimated completion reporting.
