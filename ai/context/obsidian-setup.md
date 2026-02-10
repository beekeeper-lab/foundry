# Obsidian MCP Integration Setup

How Claude Code agents read/write to the foundry Obsidian vault via Docker MCP.

## Architecture

```
Claude Code
    ↓  mcp__MCP_DOCKER__obsidian_* tool calls
Docker MCP Container (mcp/obsidian)
    ↓  HTTPS REST API via host.docker.internal:27124
Obsidian Desktop (Local REST API plugin)
    ↓  Direct file access
Foundry Vault (/home/gregg/Nextcloud/workspace/foundry/)
```

## Prerequisites

- **Docker Desktop** with MCP support (v28.5+)
- **Obsidian** desktop app with the foundry repo opened as a vault
- The foundry vault registered in `~/.config/obsidian/obsidian.json`

## Setup Steps

### 1. Enable Community Plugins

In Obsidian: Settings → Community plugins → Turn on community plugins.

This creates `.obsidian/community-plugins.json` in the vault.

### 2. Install Local REST API Plugin

In Obsidian: Settings → Community plugins → Browse → search "Local REST API" → Install → Enable.

This creates `.obsidian/plugins/obsidian-local-rest-api/` with the plugin files.

### 3. Configure the Plugin

The plugin auto-generates on first run:
- **Port:** 27124 (HTTPS, default)
- **API Key:** auto-generated SHA-256 hex string
- **Self-signed TLS cert:** auto-generated

Settings are stored in `.obsidian/plugins/obsidian-local-rest-api/data.json`.

### 4. Register Obsidian in Docker MCP

In Docker Desktop: Settings → MCP Catalog → enable "Obsidian".

This adds the entry to `~/.docker/mcp/registry.yaml`:

```yaml
registry:
  obsidian:
    ref: ""
```

### 5. Set the API Key Secret

In Docker Desktop: the Obsidian MCP server prompts for the `OBSIDIAN_API_KEY` secret on first use.

Copy the `apiKey` value from `.obsidian/plugins/obsidian-local-rest-api/data.json` and paste it into the Docker Desktop secret prompt.

### 6. Verify

From a Claude Code session, these tools should work:

- `mcp__MCP_DOCKER__obsidian_list_files_in_vault` — returns top-level vault files
- `mcp__MCP_DOCKER__obsidian_get_file_contents` — reads any file by relative path
- `mcp__MCP_DOCKER__obsidian_simple_search` — full-text search across vault

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `obsidian_list_files_in_vault` | List root-level files and directories |
| `obsidian_list_files_in_dir` | List files in a specific directory |
| `obsidian_get_file_contents` | Read a single file |
| `obsidian_batch_get_file_contents` | Read multiple files at once |
| `obsidian_append_content` | Append to a file (creates if missing) |
| `obsidian_patch_content` | Insert/replace content relative to a heading or block |
| `obsidian_delete_file` | Delete a file or directory |
| `obsidian_simple_search` | Full-text search across vault |
| `obsidian_complex_search` | JsonLogic query search |
| `obsidian_get_periodic_note` | Get current daily/weekly/monthly note |
| `obsidian_get_recent_periodic_notes` | Get recent periodic notes |
| `obsidian_get_recent_changes` | List recently modified files |

## Networking Details

- Docker Desktop on Linux resolves `host.docker.internal` to the host machine automatically
- The MCP container connects to `host.docker.internal:27124` (HTTPS with self-signed cert)
- Obsidian must be running for the REST API to be available
- If port 27124 is not listening, the MCP tools will fail with connection errors

## Troubleshooting

**Tools return connection errors:**
- Verify Obsidian is running with the vault open
- Check port: `ss -tlnp | grep 27124` — should show `electron` listening
- Ensure the Local REST API plugin is enabled (green toggle in Obsidian settings)

**Authentication errors:**
- The API key in Docker Desktop must match `.obsidian/plugins/obsidian-local-rest-api/data.json`
- If the key was regenerated, update the Docker Desktop secret

**Docker MCP not loading:**
- Check `~/.docker/mcp/registry.yaml` has the `obsidian` entry
- Restart Docker Desktop if the MCP server doesn't appear

## Security Notes

- `.obsidian/` is in `.gitignore` — plugin config (including API key and TLS cert) is never committed
- The API key and TLS private key are local-only, stored in the vault's `.obsidian/` directory
- The REST API only listens on `127.0.0.1` (localhost), not exposed to the network
- Docker reaches it via `host.docker.internal` which resolves to the host loopback
