# BEAN-079: Obsidian MCP Integration

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-079 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-09 |
| **Completed** | 2026-02-09 |
| **Duration** | <1 day |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The Obsidian MCP server (Docker Desktop catalog) cannot reach Obsidian because the **Local REST API** community plugin is not installed in any vault, so nothing is listening on port 27124. The Docker-side plumbing exists (`host.docker.internal` resolution, `MCP_DOCKER` server registered in `~/.docker/mcp/registry.yaml`) but the host-side endpoint is missing. This blocks Claude agents from reading/writing Obsidian notes for bean review, knowledge management, and approval workflows.

Additionally, the foundry repo is now registered as an Obsidian vault (`.obsidian/` added to `.gitignore`) but has no community plugins configured yet.

## Goal

Claude agents can read and write to the foundry Obsidian vault via MCP tools (`mcp__MCP_DOCKER__obsidian_*`), enabling bean review workflows, knowledge capture, and note management directly from Claude Code sessions.

## Scope

### In Scope
- Install and configure the **Local REST API** Obsidian plugin in the foundry vault
- Enable community plugins in the foundry vault's Obsidian config
- Verify `host.docker.internal` resolves correctly from Docker Desktop on this Linux host
- Configure the `OBSIDIAN_API_KEY` secret for the Docker MCP server
- End-to-end verification: Claude agent successfully calls `obsidian_list_files_in_vault`
- Document the setup steps in `ai/context/` for future reference

### Out of Scope
- Modifying the Docker MCP catalog image itself (managed by Docker Desktop)
- Building custom MCP servers for Obsidian
- Obsidian plugin development
- Syncing the foundry vault to other Obsidian instances

## Acceptance Criteria

- [x] Local REST API plugin is installed and enabled in the foundry Obsidian vault
- [x] Port 27124 is listening on localhost when Obsidian is running
- [x] The Docker MCP container can reach `host.docker.internal:27124`
- [x] `OBSIDIAN_API_KEY` is configured for the Docker MCP server
- [x] `mcp__MCP_DOCKER__obsidian_list_files_in_vault` returns the foundry vault's file list from a Claude Code session
- [x] `mcp__MCP_DOCKER__obsidian_get_file_contents` can read `ai/beans/_index.md`
- [x] `.obsidian/` remains in `.gitignore`
- [x] Setup steps are documented in `ai/context/obsidian-setup.md`

## Investigation Findings

### Current State
- **Docker Desktop** v28.5.1 running on Linux (Arch, kernel 6.18.7)
- **Docker MCP registry** (`~/.docker/mcp/registry.yaml`) has `obsidian` registered
- **Docker MCP catalog** (`~/.docker/mcp/catalogs/docker-mcp.yaml`) defines the image: `mcp/obsidian@sha256:0eba4c05...`
- **Obsidian** installed at `/usr/bin/obsidian`, using Electron 39
- **Foundry vault** registered in `~/.config/obsidian/obsidian.json` (vault ID `4e52fa876ba9fffa`)
- **No community plugins** installed in any vault — `plugins/` directory doesn't exist
- **Port 27124** not listening — Local REST API plugin not installed

### Docker Networking
- `host.docker.internal` is Docker Desktop's built-in host resolution mechanism
- Docker Desktop on Linux handles this natively (unlike plain Docker Engine which needs `--add-host`)
- The MCP container config sets `OBSIDIAN_HOST=host.docker.internal`
- Authentication uses `OBSIDIAN_API_KEY` env var (secret managed by Docker Desktop)

### Architecture
```
Host: Obsidian + Local REST API plugin → localhost:27124
         ↑
Docker: host.docker.internal:27124 ← MCP Obsidian container
         ↑
Claude Code ← mcp__MCP_DOCKER__obsidian_* tools
```

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Enable community plugins in foundry vault config | team-lead | | Done |
| 2 | Install Local REST API plugin in Obsidian | team-lead | 1 | Done |
| 3 | Configure plugin settings (port 27124, API key) | team-lead | 2 | Done |
| 4 | Set OBSIDIAN_API_KEY in Docker Desktop MCP config | team-lead | 3 | Done |
| 5 | Verify host.docker.internal resolution from container | team-lead | | Done |
| 6 | End-to-end test: Claude → MCP → Obsidian round-trip | team-lead | 3, 4 | Done |
| 7 | Write setup docs at ai/context/obsidian-setup.md | team-lead | 6 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Tasks 1-4 require manual interaction with the Obsidian GUI (community plugin install) and Docker Desktop (secret configuration). Claude can assist but cannot fully automate these steps.
- The GPG credential error when pulling Docker images (`gpg: no gpg-agent running`) is a separate issue — the MCP container image should already be cached by Docker Desktop.
- The foundry vault `.obsidian/` config was created when Obsidian first opened the vault. It contains `app.json`, `appearance.json`, `core-plugins.json`, `workspace.json` but no `community-plugins.json` yet.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | Enable community plugins | team-lead | — | — | — |
| 2 | Install Local REST API plugin | team-lead | — | — | — |
| 3 | Configure plugin settings | team-lead | — | — | — |
| 4 | Set OBSIDIAN_API_KEY in Docker MCP | team-lead | — | — | — |
| 5 | Verify host.docker.internal resolution | team-lead | — | — | — |
| 6 | End-to-end test round-trip | team-lead | — | — | — |
| 7 | Write setup docs | team-lead | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | ~3m (git), longer with manual Obsidian setup |
| **Total Tokens In** | — (not tracked) |
| **Total Tokens Out** | — (not tracked) |

> Backfilled from git reflog: branch 19:48:11 → merge 19:51:40 (shared commit with BEAN-080). Most tasks involved manual GUI interaction outside git timeline. Token data unavailable.

> Duration backfilled from git timestamps (commit→merge, 7s).
