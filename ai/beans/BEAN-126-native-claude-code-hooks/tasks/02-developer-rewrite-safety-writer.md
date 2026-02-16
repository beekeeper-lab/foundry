# Task 02: Rewrite Safety Writer with Native Hook Format

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-02-16 00:03 |
| **Completed** | 2026-02-16 00:05 |
| **Duration** | 2m |

## Goal

Replace the custom safety model format in `safety_writer.py` with native Claude Code hook format. The generated `.claude/settings.json` should contain `PreToolUse`/`PostToolUse` hook arrays instead of the custom `safety` object.

## Inputs

- `foundry_app/services/safety_writer.py` — Current implementation to rewrite
- Task 01 design output — Hook pack → native hook mapping
- `foundry_app/core/models.py` — `HookPackSelection`, `HooksConfig`, `HookMode`

## Approach

1. Create a hook pack registry mapping pack IDs to native hook definitions
2. Replace `_build_safety_config()` with a function that builds native hook arrays from `spec.hooks.packs`
3. For each enabled pack (mode != DISABLED), add its PreToolUse/PostToolUse entries
4. Generate `{"hooks": {"PreToolUse": [...], "PostToolUse": [...]}}` format
5. Handle edge cases: no packs selected → empty arrays; posture still influences default packs

## Acceptance Criteria

- [ ] `write_safety()` generates native Claude Code hook format
- [ ] Hook entries correspond to enabled hook packs from the spec
- [ ] Disabled packs produce no hook entries
- [ ] Empty pack list produces `{"hooks": {"PreToolUse": [], "PostToolUse": []}}`
- [ ] Each hook entry has valid `matcher` and `hooks` array with `type`/`command`
- [ ] The `safety` key is no longer generated

## Definition of Done

safety_writer.py fully rewritten, compiles without errors.
