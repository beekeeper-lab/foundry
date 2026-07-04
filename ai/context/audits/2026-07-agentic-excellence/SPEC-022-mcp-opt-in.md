# SPEC-022: MCP servers become composition-driven and opt-in

- **Priority:** P2
- **Effort:** M
- **Area:** pipeline+kit
- **Depends on:** none
- **Status:** Proposed

## Problem

Every generated project gets `obsidian` and `trello` MCP servers whether or not it uses Obsidian or Trello, and the kit hard-wires a `trello` server (requiring `TRELLO_API_KEY`/`TRELLO_TOKEN`) into every consuming repo. There is no way to add, remove, or configure an MCP server from `composition.yml`, and no `env` passthrough — so any server needing credentials is emitted non-functional. The emitted file also lands at `.claude/mcp.json`, while Claude Code reads project MCP config from the repo-root `.mcp.json`.

## Evidence

- `ai-team-library/workflows/mcp-registry.yaml:49-52` — `baseline:` is `filesystem, obsidian, trello`; baseline is "always emitted."
- `foundry_app/services/mcp_writer.py:18` — `_EMITTED_FIELDS = ("type", "command", "args")`; no `env` ever reaches the output, so a credentialed server is born broken.
- `foundry_app/services/mcp_writer.py:116` — output path is `out_root / ".claude" / "mcp.json"`, not the root `.mcp.json` Claude Code discovers.
- `foundry_app/core/models.py` — `CompositionSpec` has no `mcp:` section; the only lever is the registry file inside the library, which users are told not to modify.
- `generated-projects/small-python-team/.claude/mcp.json` — `filesystem`, `obsidian`, `trello` emitted for a plain Python library project.
- `.claude/shared/settings.json:53-62` — kit ships `mcpServers.trello` with `TRELLO_API_KEY`/`TRELLO_TOKEN` env placeholders to every consuming project; `mcpServers` inside `settings.json` is the legacy location.
- `.claude/shared/scripts/claude-sync.sh:326-333` — `sync_mcp()` symlinks `.claude/local/mcp.json` → `.claude/mcp.json`, which Claude Code does not read (root `.mcp.json` is the convention).

## Proposed change

1. **Add an `mcp:` section to the composition schema** (`models.py`, `composition_io.py`):
   ```yaml
   mcp:
     include: [filesystem]          # registry ids; omit → registry baseline
     exclude: [obsidian, trello]    # subtract from whatever is included
     servers:                       # ad-hoc, project-specific servers
       my-api:
         type: stdio
         command: npx
         args: ["-y", "some-server"]
         env: { API_KEY: "${MY_API_KEY}" }
   ```
2. **Trim the registry baseline to `filesystem` only** (`mcp-registry.yaml:49-52`). Move `obsidian`/`trello` behind explicit opt-in (either `mcp.include` or a new `by_persona`/`by_feature` key — e.g. trello only when the composition enables Trello sync).
3. **Support `env` end-to-end:** add `env` to `_EMITTED_FIELDS` semantics (emit when present, values as `${VAR}` placeholders, never literal secrets), validate placeholder syntax in `mcp_writer._load_registry`.
4. **Emit to root `.mcp.json`** (`mcp_writer.py:116`) and update the generated `.gitignore`/docs accordingly. Keep writing `.claude/mcp.json` for one release with a deprecation note, or migrate cleanly in one pass — decide in review.
5. **Kit side:** remove `mcpServers` from `.claude/shared/settings.json`; move the trello server to an example in `.claude/local/` documentation. Update `sync_mcp()` to link local MCP config to root `.mcp.json`.
6. **Validator:** warn when a composition references an unknown registry id, and when a server with `env` placeholders is emitted (reminder that the user must supply the variables).

## Out of scope

- Vetting new MCP servers for the registry (registry hygiene rules already exist in the file header).
- Per-agent MCP scoping.
- SPEC-016's permissions work (separate spec).

## Acceptance criteria

- [ ] `file-contains:` `foundry_app/core/models.py` defines an `McpConfig` (or equivalent) model with `include`, `exclude`, `servers` (with `env`).
- [ ] `test:` generating `examples/small-python-team.yml` unchanged emits only `filesystem` (new baseline) at the project root `.mcp.json`.
- [ ] `test:` a composition with `mcp.servers.<id>.env` emits that `env` block verbatim into `.mcp.json`.
- [ ] `test:` `mcp.exclude` removes a baseline server from the output.
- [ ] `file-contains:` `.claude/shared/settings.json` no longer contains `mcpServers`.
- [ ] `manual:` a generated project opens in Claude Code with the emitted servers visible via `/mcp` and no failed `trello` spawn.

## Files to touch

- `foundry_app/core/models.py`, `foundry_app/io/composition_io.py`
- `foundry_app/services/mcp_writer.py`, `foundry_app/services/validator.py`
- `ai-team-library/workflows/mcp-registry.yaml`
- `.claude/shared/settings.json`, `.claude/shared/scripts/claude-sync.sh` (kit repo — via kit PR flow)
- `tests/` (mcp_writer + validator tests), `README.md` (MCP section), `examples/*.yml`
