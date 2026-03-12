# BEAN-229: BA Engagement Rules

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-229 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-23 |
| **Started** | 2026-02-23 20:49 |
| **Completed** | 2026-02-23 20:55 |
| **Duration** | 57h 5m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The BA persona is underutilized, similar to how the architect was before BEAN-228. Currently the BA is almost never engaged, leaving requirements validation solely to Tech-QA and the Team Lead. The user wants two things: (1) a flag that controls whether the BA is fully engaged (managing a separate requirements register, running at the start of every workflow) or partially engaged (current mode), and (2) even in partial mode, clearer rules that engage the BA more often — especially for complex beans, documentation tasks, and cases where interrogating existing requirements would add value.

## Goal

Define a BA engagement system with two modes controlled by a project-level flag:
- **Full mode**: BA maintains a requirements register, runs at the start of every bean to check/update requirements, and feeds relevant requirements to downstream personas.
- **Partial mode** (default): BA is engaged based on clear rules — more often than today, covering complex beans, documentation tasks, and requirements ambiguity.

Update all relevant agent and workflow files with the new BA engagement rules and the mode flag mechanism.

## Scope

### In Scope
- Define the full-engagement vs partial-engagement flag and where it lives (project config or bean-workflow)
- Define clear, actionable rules for when the BA should be engaged in partial mode
- Define the BA's workflow in full mode (requirements register, pre-bean analysis, handoff)
- Update `team-lead.md` with BA engagement rules and flag handling
- Update `ba.md` with the two operating modes
- Update `bean-workflow.md` with revised BA participation criteria
- Create the requirements register template if full mode is defined

### Out of Scope
- Implementing full-mode BA workflow end-to-end (this bean defines the rules; a follow-up bean can implement the requirements register)
- Changing architect or tech-qa engagement rules
- Retroactive requirements analysis on past beans

## Acceptance Criteria

- [ ] A project-level flag mechanism is defined for BA full-engagement vs partial-engagement
- [ ] Clear, numbered rules define when the BA is engaged in partial mode
- [ ] Partial-mode rules cover: complex beans, documentation tasks, requirements ambiguity, multi-stakeholder trade-offs
- [ ] Full-mode BA workflow is specified: requirements register location, pre-bean analysis steps, handoff format
- [ ] Team-lead agent updated with new BA engagement rules and flag handling
- [ ] BA agent updated with two operating modes
- [ ] Bean-workflow.md updated with revised BA participation criteria
- [ ] Rules are observable — the team lead can evaluate them without ambiguity

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Define BA engagement rules and modes | developer | — | Done |
| 2 | Verify BA engagement rules | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (documentation-only process bean)

## Changes

| File | Lines |
|------|-------|
| ai/beans/BEAN-229-ba-engagement-rules/bean.md | +101 |
| ai/beans/BEAN-229-ba-engagement-rules/tasks/01-developer-ba-rules.md | +88 |
| ai/beans/BEAN-229-ba-engagement-rules/tasks/02-tech-qa-verify-rules.md | +41 |
| ai/beans/_index.md | +1 |
| ai/context/bean-workflow.md | +50/-4 |

## Notes

This bean depends on BEAN-228 (Architect Engagement Rules), which is now Done. The patterns established in BEAN-228 (numbered rules, exclusion lists, "when in doubt" heuristic) should be followed for consistency.

User guidance from Trello card: Two modes — full engagement (BA manages requirements, runs every bean) and partial engagement (BA used more often than today). Even in partial mode, the BA should be engaged for complex beans, documentation tasks, and when interrogating existing requirements would help.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6999ef66ec665acc9676772f |
| **Card Name** | BA team member. |
| **Card URL** | https://trello.com/c/aq6EUyOu/94-ba-team-member |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Define BA engagement rules and modes | developer | 2m | 1,621,916 | 1,295 | $2.69 |
| 2 | Verify BA engagement rules | tech-qa | 1m | 849,688 | 7 | $1.45 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 3m |
| **Total Tokens In** | 2,471,604 |
| **Total Tokens Out** | 1,302 |
| **Total Cost** | $4.14 |