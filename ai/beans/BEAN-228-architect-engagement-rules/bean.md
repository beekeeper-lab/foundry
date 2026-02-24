# BEAN-228: Architect Engagement Rules

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-228 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-23 |
| **Started** | 2026-02-23 20:03 |
| **Completed** | 2026-02-23 20:07 |
| **Duration** | 56h 17m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The architect persona is underutilized. The current activation criteria are too vague, resulting in the team lead almost never engaging the architect. Important architectural decisions are being made without ADRs, refactoring happens without architectural oversight, and early-project setup work bypasses the architect entirely. The threshold for architect engagement needs to be lowered and codified into clear, actionable rules.

## Goal

Define a concrete set of principles and rules that tell the team lead when to engage the architect persona. These rules should ensure the architect is activated for refactoring, new subsystem setup, early-project foundations, and any work that warrants an ADR — while still avoiding unnecessary engagement for trivial changes like adding a button to a form.

## Scope

### In Scope
- Review current architect activation criteria in `.claude/agents/architect.md` and `.claude/agents/team-lead.md`
- Define clear, actionable rules for when the architect should be engaged
- Update the team-lead agent with the new engagement rules
- Update the architect agent if needed to align with new engagement patterns
- Ensure ADR creation is triggered when architectural decisions are made
- Update bean-workflow.md with revised participation decision criteria

### Out of Scope
- Changing the architect's actual output format or workflow
- Modifying other persona activation criteria (BA, Tech-QA)
- Retroactive ADR creation for past decisions

## Acceptance Criteria

- [ ] Clear, numbered rules define when the architect must be engaged
- [ ] Rules cover: refactoring, new functionality requiring structural changes, early project setup, ADR-worthy decisions
- [ ] Rules explicitly exclude trivial changes (simple UI additions, text changes, etc.)
- [ ] Team-lead agent updated with new architect engagement rules
- [ ] Architect agent updated if alignment changes are needed
- [ ] Bean-workflow.md participation decisions section updated
- [ ] Rules are observable — the team lead can evaluate them without ambiguity

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Draft and apply architect engagement rules | developer | — | Done |
| 2 | Verify architect engagement rules | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (default — process documentation update, not system design)

## Changes

| File | Lines |
|------|-------|
| ai/beans/BEAN-228-architect-engagement-rules/bean.md | +93 |
| ai/beans/BEAN-228-architect-engagement-rules/tasks/01-developer-architect-rules.md | +61 |
| ai/beans/BEAN-228-architect-engagement-rules/tasks/02-tech-qa-verify-rules.md | +38 |
| ai/beans/_index.md | +1 |
| ai/context/bean-workflow.md | +15/-5 |

## Notes

Trello card description from user: The architect should be engaged more often. Key scenarios include: any refactoring triggered by new functionality, early project setup/foundations, and whenever an architectural decision warrants an ADR. The rules should be iterative — observe for several iterations and adjust.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6999ef4bc733cdb33fa2aee5 |
| **Card Name** | Architectural team member. |
| **Card URL** | https://trello.com/c/hOlfnB5T/93-architectural-team-member |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Draft and apply architect engagement rules | developer | 1m | 976,679 | 2,070 | $1.78 |
| 2 | Verify architect engagement rules | tech-qa | < 1m | 560,923 | 7 | $1.01 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 1,537,602 |
| **Total Tokens Out** | 2,077 |
| **Total Cost** | $2.79 |