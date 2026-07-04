# BEAN-296: ClaudeKit plugin packaging (ADR-016 phase 2)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-296 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-07-03 |
| **Started** | 2026-07-04 02:32 |
| **Completed** | 2026-07-04 02:55 |
| **Duration** | 23m |
| **Owner** | team-lead |
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

- [ ] (file-contains:ai/context/decisions/ADR-016-kit-distribution-plugin-direction-with-a-contribution-flow.md::Status) ADR-016 updated with phase-2 outcome
- [ ] (file:.claude/shared/.claude-plugin/plugin.json) Plugin manifest exists in the kit
- [ ] (file:.claude/shared/.claude-plugin/marketplace.json) Marketplace listing exists
- [ ] (file-contains:.claude/shared/README.md::marketplace) Install/update flow documented
- [ ] (test:tests/) All tests pass (`uv run pytest`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Plugin packaging (manifest, hooks.json, marketplace, README) | developer | — | Done |
| 2 | Verification + VDD report | tech-qa | 1 | Done |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

Scope change (2026-07-04, Team Lead): the 'pilot repo' AC was manual and unverifiable from this repo; replaced with machine-checkable packaging ACs. Pilot migration of a consuming repo happens when one is at hand, following the documented install flow.

Bounce (2026-07-04): Tech-QA's first gate run FAILed on AC #1 — the Team Lead had written a truncated ADR filename into the criterion (`...-contribution-fl.md`). AC corrected to the real path; no Developer rework. QA's non-blocking note about `permissions.deny` having no plugin-format equivalent added to the kit README migration text.

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
| **Personas activated** | team-lead, developer, tech-qa |
| **Bounces** | 1 (Tech-QA → Team-Lead: truncated ADR filename in AC #1; no Developer rework) |
| **Scope changes** | 1 (manual pilot AC replaced with machine-checkable packaging ACs; see Notes) |
| **Contract violations** | 0 |
| **Inputs escape-hatch invocations** | 0 |
| **Dispatch mode** | mixed (agent-subagent ×2, in-process ×2 tiny tasks: ADR status line, AC fix) |
