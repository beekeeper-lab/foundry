# BEAN-296: ClaudeKit plugin packaging (ADR-016 phase 2)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-296 |
| **Status** | Unapproved |
| **Priority** | High |
| **Created** | 2026-07-03 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |
| **Depends On** | — |

## Problem Statement

ADR-016 accepted the plugin/marketplace direction for kit distribution, staged: phase 1 (contribution flow, publish guard) shipped with the audit. Phase 2 — packaging the stable layer (media skills, safety hooks, generic commands) as an installable Claude Code plugin — is not started, so consumers still depend on the submodule + sync apparatus for everything.

## Goal

The claude-kit repo carries a plugin manifest for the stable layer; one pilot consumer installs the kit as a plugin and retires its symlink layer for that content.

## Scope

### In Scope
- Plugin manifest + packaging in the claude-kit repo (stable layer only)
- Marketplace listing under beekeeper-lab
- Pilot migration of one consuming repo; document the install/update flow
- Decision note: what stays submodule (fast-moving orchestration layer) per the ADR's hybrid staging

### Out of Scope
- Migrating all consumers
- Retiring claude-sync.sh for the orchestration layer
- Any change to the library-copy generation path

## Acceptance Criteria

> Authored by: BA (when activated) | Team-Lead (default).

- [ ] (file-contains:ai/context/decisions/ADR-016-kit-distribution-plugin-direction-with-a-contribution-fl.md::Status) ADR-016 updated with phase-2 outcome
- [ ] Pilot repo installs the kit plugin and receives an update (manual)
- [ ] (test:tests/) All tests pass (`uv run pytest`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

Origin: SPEC-026 (`ai/context/audits/2026-07-agentic-excellence/SPEC-026-kit-distribution-evolution.md`) and ADR-016. Most of the work lives in the claude-kit repo; this bean tracks the foundry-side coordination.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | — (comma-separated, actual not planned) |
| **Bounces** | — (Tech-QA → Developer kicks) |
| **Scope changes** | — (in-flight scope edits) |
| **Contract violations** | — (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | — (BEAN-272's NONE-justified) |
| **Dispatch mode** | — (agent-subagent / agent-worktree / in-process / mixed) |
