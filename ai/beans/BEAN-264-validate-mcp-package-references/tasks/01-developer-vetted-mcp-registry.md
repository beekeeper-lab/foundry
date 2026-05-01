# Task 01: Vetted MCP Registry + mcp_writer Refactor

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-17 18:18 |
| **Completed** | 2026-04-17 18:18 |
| **Duration** | < 1m |

## Goal

Replace the fictional `@anthropic/*` npm references emitted by
`foundry_app/services/mcp_writer.py` with real, published packages, and
move the source of truth into a vetted registry YAML that lives in
`ai-team-library/workflows/mcp-registry.yaml`.

## Inputs

- `foundry_app/services/mcp_writer.py`
- `ai-team-library/workflows/` (new file will be added here)

## Changes Required

1. Create `ai-team-library/workflows/mcp-registry.yaml` with this shape:

   ```yaml
   servers:
     <server-id>:
       type: stdio
       command: npx|uvx|...
       args: [...]
       package: "<npm or pypi ref>"   # documentation only
       notes: "<why this is vetted>"
   baseline:
     - <server-id>
   by_expertise:
     <expertise-id>:
       - <server-id>
   ```

2. Populate with real, published references only:
   - `filesystem` → `@modelcontextprotocol/server-filesystem` (official MCP server)
   - `obsidian` → `mcp-obsidian` via `uvx` (already real)
   - `trello` → `@delorenj/mcp-server-trello` (already real)
   - Remove fictional `python-docs`, `node-docs`, `react-docs`,
     `typescript-docs` — no good published substitute, per bean scope.

3. Refactor `mcp_writer.py`:
   - Remove the hard-coded `_BASELINE_SERVERS` / `_EXPERTISE_SERVERS` dicts.
   - Load the registry at generation time. Resolve by: all `baseline`
     server IDs, plus the union of `by_expertise[selected_expertise]`.
   - Emit only `{type, command, args}` for each server — `package` and
     `notes` are registry metadata, not runtime config.
   - Fail loudly if the registry is missing or malformed (let the error
     propagate; a generated project without vetted MCP refs is worse
     than a crash).

4. Locate the registry robustly: the generator already knows the library
   root via `spec.library_path` or equivalent. If the pipeline doesn't
   pass a library root to `write_mcp_config`, accept an explicit
   `library_root: Path` parameter and wire it from the generator.

## Acceptance Criteria

- [ ] `ai-team-library/workflows/mcp-registry.yaml` exists, contains only
      real packages, and has no `@anthropic/*` references.
- [ ] `foundry_app/services/mcp_writer.py` has no hard-coded server dicts
      and reads from the registry.
- [ ] Generated `mcp.json` contains only servers defined in the registry.
- [ ] `uv run pytest tests/test_mcp_writer.py` passes.
- [ ] `uv run ruff check foundry_app/` passes.

## Definition of Done

- Registry YAML lands under `ai-team-library/workflows/`.
- `mcp_writer.py` consults the registry.
- Generator wiring passes the library root through to the writer.
- Tests green, lint clean.
