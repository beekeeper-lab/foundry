# BEAN-133: Analyze Show Backlog Command

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-133 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-16 |
| **Started** | 2026-02-16 |
| **Completed** | 2026-02-16 19:03 |
| **Duration** | < 1m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The `/show-backlog` command currently exists only as a legacy command file (`.claude/commands/show-backlog.md`) without a corresponding SKILL.md in the skills directory. All other major skills in the system have been migrated to the structured SKILL.md format with defined Trigger, Inputs, Process, Outputs, Quality Criteria, and Error Conditions sections. This inconsistency needs to be analyzed so a future bean can address the gap.

## Goal

Produce a comprehensive analysis document that evaluates the current `/show-backlog` command implementation, compares it against the structured SKILL.md format used by peer skills, identifies gaps and improvement opportunities, and provides actionable recommendations for a future enhancement bean.

## Scope

### In Scope
- Analyze the current `.claude/commands/show-backlog.md` command file
- Compare against structured SKILL.md format (using `/bean-status`, `/backlog-refinement`, `/backlog-consolidate` as reference)
- Identify functional gaps, missing error handling, and UX improvements
- Evaluate overlap/relationship with `/bean-status` skill
- Provide recommendations for SKILL.md migration

### Out of Scope
- Implementing any changes to the show-backlog command
- Creating the actual SKILL.md file
- Modifying any code or skill files

## Acceptance Criteria

- [x] Analysis document exists at `ai/outputs/team-lead/bean-133-show-backlog-analysis.md`
- [x] Document covers current implementation review
- [x] Document compares against SKILL.md format standards
- [x] Document identifies functional gaps and improvement opportunities
- [x] Document evaluates relationship with /bean-status
- [x] Document provides actionable recommendations

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Analyze show-backlog command and write output document | Developer | — | Done |

> **Skipped personas:**
> - **BA**: Skipped — Process analysis bean; requirements are self-contained in the bean definition. No external stakeholder requirements to gather.
> - **Architect**: Skipped — No system design decisions needed; this is a read-only analysis task.
> - **Tech QA**: Skipped — No code changes to test; output is a documentation artifact only.

## Notes

Part of the parallel analysis batch (BEAN-131 through BEAN-135) analyzing existing command/skill files for gaps and improvement opportunities.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Analyze show-backlog command | Developer | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
