# BEAN-150: Examples-First

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-150 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 04:07 |
| **Completed** | 2026-02-17 04:09 |
| **Duration** | 2m |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

AI team members sometimes produce outputs (code, documentation, configurations) that don't match the expected format or patterns because they haven't seen concrete examples of the desired output. Abstract instructions alone can be ambiguous.

## Goal

Establish an "examples-first" principle in the bean workflow where each task includes or references concrete examples of the expected output format before work begins. This reduces ambiguity and improves first-attempt quality.

## Scope

### In Scope
- Define the examples-first principle for task execution
- Add guidance for including examples in task definitions
- Update agent instructions or workflow docs to reference this principle

### Out of Scope
- Changes to the application code
- Creating example libraries for all possible output types

## Acceptance Criteria

- [x] Examples-first principle is documented
- [x] Task template or guidance includes a place for examples
- [x] Agent instructions reference the principle
- [x] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add Examples-First principle to workflow and agent docs | Developer | — | Done |
| 2 | Verify Examples-First documentation | Tech-QA | Task 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention — sequential 2-task wave, no shared resource conflicts

## Notes

(Trello card had no description.)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993df9ece83e1c082f3cc63 |
| **Card Name** | Examples-First |
| **Card URL** | https://trello.com/c/qit4mQ2S/23-examples-first |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add Examples-First principle to workflow and agent docs | Developer | < 1m | 9 | 1,169 | $0.09 |
| 2 | Verify Examples-First documentation | Tech-QA | < 1m | 8 | 461 | $0.03 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 17 |
| **Total Tokens Out** | 1,630 |
| **Total Cost** | $0.12 |