# BEAN-070: MCP Config Generation

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-070 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Generated projects have no MCP (Model Context Protocol) server configuration. Claude Code uses `.claude/mcp.json` to configure MCP servers that provide additional tools and context. Foundry itself uses MCP servers (e.g., Obsidian integration), and generated projects should be able to declare their own MCP server needs based on the selected stacks and architecture.

Without MCP config, generated projects miss out on enhanced Claude Code capabilities like database access, API documentation tools, or cloud resource management tools that would be relevant to their tech stack.

## Goal

Create a service that generates `.claude/mcp.json` for generated projects based on the composition spec. The MCP config should include sensible defaults based on the selected stacks (e.g., a database MCP server for SQL-focused projects) and allow the user to configure additional MCP servers through the wizard.

## Scope

### In Scope
- New service: `foundry_app/services/mcp_writer.py`
- Generate `.claude/mcp.json` in output project directory
- Default MCP server suggestions based on selected stacks:
  - Python projects: filesystem server for project navigation
  - SQL/database projects: database MCP server template
  - DevOps projects: cloud resource MCP server template
- MCP config structure matching Claude Code's expected format
- Wire into `generator.py` pipeline (new stage)
- Basic MCP server catalog in the library (name, description, config template)
- Tests for MCP writer service

### Out of Scope
- MCP server installation or runtime setup (just config generation)
- Custom MCP server development
- Wizard UI for fine-grained MCP configuration (future bean — for now, auto-select based on stacks)
- MCP server health checking or validation

## Acceptance Criteria

- [ ] New `foundry_app/services/mcp_writer.py` service exists
- [ ] Generated projects include `.claude/mcp.json` with valid structure
- [ ] MCP config includes at minimum a filesystem server for all projects
- [ ] Stack-aware MCP suggestions are included as commented-out entries or enabled defaults
- [ ] MCP writer wired into `generator.py` pipeline
- [ ] MCP config matches Claude Code's expected `mcp.json` format
- [ ] Tests cover: default config, stack-based suggestions, empty stacks
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- This bean is independent of BEAN-067 (Wire Pipeline) but benefits from it being done first
- Claude Code MCP config format: `{"servers": {"server-name": {"type": "...", "command": "...", "args": [...]}}}` — verify against current Claude Code docs
- Consider reading Foundry's own `.claude/mcp.json` as a reference for the generated config
- Start simple — a filesystem MCP server for all projects is a good baseline, with stack-specific servers as stretch goals
- The MCP server catalog could later be managed through the Library Manager UI

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

> Duration backfilled from git timestamps (commit→merge, 9s).
