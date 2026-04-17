# BEAN-264: Validate MCP Package References in Generated mcp.json

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-264 |
| **Status** | In Progress |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 18:15 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

External review (2026-04-17): "`mcp.json` references packages that
don't exist. `@anthropic/mcp-filesystem`, `@anthropic/mcp-react-docs`,
`@anthropic/mcp-typescript-docs` are not published under `@anthropic`.
Agents will get `npm ERR 404` on first MCP spin-up."

Confirmed in a fresh generation (2026-04-17):

```json
"filesystem": { "command": "npx", "args": ["-y", "@anthropic/mcp-filesystem"] }
"python-docs": { "command": "npx", "args": ["-y", "@anthropic/mcp-python-docs"] }
```

Neither package is published under the `@anthropic` scope at the time
of review. A generated project hits an npm 404 the first time an agent
tries to spin up these MCP servers.

## Goal

Every MCP server reference in a generated `mcp.json` resolves to a real,
installable package at generation time. The library maintains a vetted
registry of MCP server references, and the generator validates against
that registry.

## Scope

### In Scope
- Audit every MCP server entry currently emitted by
  `foundry_app/services/mcp_writer.py` (or equivalent).
- Replace `@anthropic/*` fictional references with real published
  alternatives (e.g. `@modelcontextprotocol/server-filesystem` for
  filesystem) or remove them if no good substitute exists.
- Add a vetted registry (YAML or JSON) of known-good MCP servers per
  technology/purpose.
- Optional: add a generation-time check (online or cached) that the
  referenced npm package exists. If online checks are too fragile,
  rely on the curated registry as the source of truth.
- Tests: generated `mcp.json` only contains references from the vetted
  registry.

### Out of Scope
- Writing new MCP servers.
- Runtime package resolution (the generator only emits configuration).
- Language-specific MCP server selection rules (related but separate —
  can be handled alongside BEAN-255/256 if stack-aware).

## Acceptance Criteria

- [ ] Every MCP reference in the default generated `mcp.json` corresponds
      to an npm/pypi package that exists as of the bean's completion date.
- [ ] A vetted registry file lives in the library and is the single
      source of truth for MCP references.
- [ ] `foundry_app/services/mcp_writer.py` consults that registry.
- [ ] Tests cover the invariant: generated `mcp.json` has no references
      outside the registry.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

> Skipped: BA (default), Architect (default)

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Vetted MCP registry + mcp_writer refactor | Developer | — | Done |
| 2 | Registry invariant tests + full regression | Tech-QA | 1 | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Source.** External review (2026-04-17). Confirmed in a fresh
`small-python-team` generation.

**Related.** BEAN-125 added the initial MCP config (Obsidian + Trello).
That bean's references were real; subsequent additions drifted to
fictional `@anthropic/*` names.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Vetted MCP registry + mcp_writer refactor | Developer | < 1m | 338,750 | 0 | $0.68 |
| 2 | Registry invariant tests + full regression | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |