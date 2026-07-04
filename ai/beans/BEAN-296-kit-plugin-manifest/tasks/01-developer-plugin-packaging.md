# Task 1: Package claude-kit as a Claude Code plugin

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Dependencies** | — |
| **Status** | Done |

## Objective

Create the plugin manifest, hooks config, and marketplace listing in the
claude-kit submodule; document the install/update flow in its README.

## Inputs

- .claude/shared/ — the kit tree being packaged (commands/, skills/, agents/, hooks/, settings.json)
- ai/context/decisions/ADR-016-kit-distribution-plugin-direction-with-a-contribution-flow.md — the decision this implements

## Acceptance Criteria

- [ ] (file:.claude/shared/.claude-plugin/plugin.json) Manifest exists and is valid JSON
- [ ] (file:.claude/shared/.claude-plugin/marketplace.json) Marketplace listing exists
- [ ] (file-contains:.claude/shared/README.md::marketplace) Install flow documented

## Telemetry

| Field | Value |
|-------|-------|
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
