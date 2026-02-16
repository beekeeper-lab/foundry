# Task 01: Design Hook Pack → Native Claude Code Hook Mapping

| Field | Value |
|-------|-------|
| **Owner** | architect |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-16 00:02 |
| **Completed** | 2026-02-16 00:03 |
| **Duration** | 1m |

## Goal

Define the concrete mapping from each hook pack ID to native Claude Code `PreToolUse`/`PostToolUse` hook definitions. This design informs the developer implementation.

## Inputs

- `.claude/settings.json` — Foundry's own native hook format (reference)
- `ai-team-library/claude/hooks/*.md` — Hook pack markdown files describing enforcement policies
- `foundry_app/core/models.py` — `HookPackSelection`, `HooksConfig`, `HookMode`, `Posture`

## Approach

For each hook pack, define:
1. Which hook type (PreToolUse or PostToolUse) it maps to
2. The tool matcher regex (e.g., "Edit|Write", "Bash")
3. The shell command that implements the check
4. How HookMode (enforcing/permissive/disabled) affects inclusion

Document the mapping as a registry that the developer can implement directly.

## Acceptance Criteria

- [ ] Every hook pack has a defined mapping to PreToolUse/PostToolUse entries
- [ ] Matchers use valid Claude Code tool names
- [ ] Commands are concrete shell scripts that implement the checks
- [ ] Design accounts for HookMode (disabled packs produce no hooks)
- [ ] Design covers empty case (no packs → empty hook arrays)

## Definition of Done

Design document produced in ai/outputs/architect/ with complete mapping.
