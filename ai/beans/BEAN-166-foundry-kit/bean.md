# BEAN-166: Foundry Kit — Shared Config Architecture Spec

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-166 |
| **Status** | In Progress |
| **Priority** | High |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:39 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

Currently, Claude Code configurations (.claude/skills, .claude/commands, .claude/agents, .claude/hooks, CLAUDE.md) are copy-pasted per repo. Improvements made in one project do not propagate to others. Foundry templates also drift from reality. We need a "Foundry Kit" approach: a canonical shared baseline, versioned, and consumed by repos.

## Goal

Produce a comprehensive architecture spec for a shared configuration kit that eliminates config drift across projects. The spec must cover options analysis, recommended architecture, implementation plan, and examples.

## Scope

### In Scope
- Options analysis (at least 4 approaches: git submodule, git subtree, symlink, sync script)
- Recommended architecture with Mermaid diagrams
- Implementation plan with step-by-step migration
- Examples: version pinning, overrides, remote server, Trello integration
- Trello integration standardization (card creation, idempotent updates, multi-machine support)
- Versioning strategy (tags, semver, changelog)
- Conflict handling and precedence rules
- Local and remote environment parity

### Out of Scope
- Building a plugin marketplace
- Rewriting Claude Code
- Implementing the kit (spec only)

## Acceptance Criteria

- [ ] Options analysis covers at least 4 approaches with pros/cons/failure modes
- [ ] Recommended architecture includes Mermaid diagrams
- [ ] Implementation plan has step-by-step migration path
- [ ] Examples cover: version pinning + override, multi-repo remote server, Trello batch card creation, emergency hotfix rollout
- [ ] Trello integration architecture documented (idempotency, config storage, env parity)
- [ ] Spec is in Markdown format in `ai/outputs/architect/`

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Foundry Kit Architecture Spec | Architect | — | Pending |
| 2 | Review Foundry Kit Architecture Spec | Tech-QA | 1 | Pending |

> Skipped: BA (default — requirements fully specified in Trello card)
> Bottleneck check: no contention — sequential Architect → Tech-QA

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

This is a large architecture spec. Requires Architect persona. The full card description from Trello contains detailed requirements including deliverable sections A through D.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998651bb0e6135998fd197d |
| **Card Name** | foundry-kit |
| **Card URL** | https://trello.com/c/YIQSO7R5/42-foundry-kit |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Foundry Kit Architecture Spec | Architect | — | — | — | — |
| 2 | Review Foundry Kit Architecture Spec | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |