# Handoff Packet: developer → tech-qa (BEAN-296, task 01)

| Field | Value |
|-------|-------|
| **From** | developer |
| **To** | tech-qa |
| **Bean** | BEAN-296 |
| **Task** | 01-developer-plugin-packaging |
| **Date** | 2026-07-04 |

## Artifacts

| Artifact type | Path | Required fields present? |
|---------------|------|--------------------------|
| code-change | .claude/shared/.claude-plugin/{plugin.json,marketplace.json} | yes |
| code-change | .claude/shared/hooks/hooks.json | yes |
| code-change | .claude/shared/README.md (install section) | yes |
| code-change | ai/context/decisions/ADR-016-*.md (status update, team-lead) | yes |

## Edge Extras

- **test-targets:** JSON validity of the three new files; hook command
  paths use `${CLAUDE_PLUGIN_ROOT}`; every script referenced in
  hooks.json exists under .claude/shared/hooks/
- **rerun-command:** `python3 -c "import json; [json.load(open(p)) for p in ('.claude/shared/.claude-plugin/plugin.json','.claude/shared/.claude-plugin/marketplace.json','.claude/shared/hooks/hooks.json')]"`

## Summary

claude-kit is installable as a Claude Code plugin: manifest + self-hosted
marketplace listing + plugin-format hook wiring translated from
settings.json. Submodule consumers unchanged (ADR-016 hybrid staging).

## Receiver Can Start When

- This packet exists; all three JSON files parse.
