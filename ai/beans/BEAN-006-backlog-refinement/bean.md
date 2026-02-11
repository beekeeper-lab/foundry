# BEAN-006: Backlog Refinement Command

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-006 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

There is no structured way to turn raw ideas, feature descriptions, or broad vision text into well-formed beans. Users currently have to manually create each bean, which requires them to already know the decomposition. The `/new-bean` command creates a single bean from explicit fields, but there's nothing that takes unstructured input and refines it into one or more beans through dialogue.

## Goal

Create a `/backlog-refinement` command that takes free-form text input, engages in an iterative conversation to clarify scope and intent, and produces one or more properly-formed beans as output.

## Scope

### In Scope
- `/backlog-refinement` command in `.claude/commands/`
- Corresponding skill in `.claude/skills/backlog-refinement/`
- Iterative dialogue flow: read input, ask clarifying questions, refine understanding
- Support for broad input (produces multiple beans) and specific input (produces one bean)
- Uses `/new-bean` to create each resulting bean
- Team Lead persona owns the refinement process
- Updates `_index.md` with all created beans

### Out of Scope
- Automated prioritization (Team Lead assigns priority through dialogue)
- Integration with external tools or issue trackers
- Modifying the bean template format
- Auto-decomposition of beans into tasks (that's the Team Lead's `/pick-bean` workflow)

## Acceptance Criteria

- [ ] `/backlog-refinement` command exists in `.claude/commands/backlog-refinement.md`
- [ ] Skill exists in `.claude/skills/backlog-refinement/SKILL.md`
- [ ] Command accepts free-form text as input
- [ ] Process includes clarifying questions before creating beans
- [ ] Produces one or more beans via `/new-bean` based on the input
- [ ] Each created bean has complete Problem Statement, Goal, Scope, and Acceptance Criteria
- [ ] Command format matches existing commands (sections, tables, examples)
- [ ] Skill format matches existing skills (sections, tables, process steps)
- [ ] Team Lead agent updated to reference `/backlog-refinement`

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Create Backlog Refinement Command & Skill | developer | — | Done |
| 02 | Backlog Refinement Verification | tech-qa | 01 | Done |

> BA and Architect skipped — requirements are clear in the bean, and this creates markdown command/skill files following existing patterns.

## Notes

This command is the "front door" to the beans workflow. The flow is:
1. User runs `/backlog-refinement` with raw text
2. Team Lead reads the text, identifies potential beans
3. Team Lead asks clarifying questions (priority, scope boundaries, dependencies)
4. User and Team Lead iterate until understanding is clear
5. Team Lead creates beans using `/new-bean` for each identified unit of work
6. Summary of created beans presented to the user

This makes the beans system accessible to users who think in terms of "here's what I want" rather than "here's a well-scoped unit of work."

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (single commit, no merge).
