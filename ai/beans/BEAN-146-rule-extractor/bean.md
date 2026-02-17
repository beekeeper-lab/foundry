# BEAN-146: Rule Extractor

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-146 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 04:01 |
| **Completed** | 2026-02-17 04:05 |
| **Duration** | 4m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The AI team accumulates knowledge through bean execution, but lessons learned and recurring patterns are not systematically extracted into reusable rules or guidelines. This leads to repeated mistakes and inconsistent quality across beans.

## Goal

Create a rule extraction process that captures recurring patterns, anti-patterns, and lessons learned from completed beans and codifies them into actionable rules for future work.

## Scope

### In Scope
- Define a process for extracting rules from completed beans
- Specify where extracted rules are stored (e.g., MEMORY.md, context docs)
- Add a post-bean review step that captures lessons learned

### Out of Scope
- Automated rule extraction tooling
- Changes to the application code

## Acceptance Criteria

- [x] Rule extraction process is documented
- [x] Process specifies how to identify and capture recurring patterns
- [x] Storage location for extracted rules is defined
- [x] Post-bean review step is added to workflow
- [x] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add rule extraction step to bean closure | developer | — | Done |
| 2 | Verify documentation quality | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (default)

## Notes

(Trello card had no description.)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993df812164fbd8dd33ac36 |
| **Card Name** | Rule Extractor |
| **Card URL** | https://trello.com/c/zcjmGVLO/22-rule-extractor |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add rule extraction step to bean closure | developer | — | — | — | — |
| 2 | Verify documentation quality | tech-qa | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |