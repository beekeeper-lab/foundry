# BEAN-126: Generate Native Claude Code Hooks

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-126 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-15 |
| **Started** | 2026-02-16 00:00 |
| **Completed** | 2026-02-16 00:25 |
| **Duration** | 25m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The safety writer service (`safety_writer.py`) generates `.claude/settings.json` with a custom Foundry safety model (keys like `git`, `shell`, `filesystem`, `network`, `secrets`, `destructive_ops`). This is not the native Claude Code hooks format. Claude Code expects `PreToolUse` and `PostToolUse` arrays with command matchers and hook definitions. Generated projects therefore have no functional Claude Code hooks — the safety config is documentation-only and doesn't actually enforce anything at the Claude Code level.

## Goal

Generated projects get a `.claude/settings.json` with proper Claude Code native `PreToolUse`/`PostToolUse` hook definitions that actually enforce the safety policies based on the hook packs the user selected in the wizard.

## Scope

### In Scope
- Replace the custom safety model format in `safety_writer.py` with native Claude Code hook format
- Map hook pack selections from the composition spec to concrete `PreToolUse`/`PostToolUse` entries
- Use the hook markdown files from the library as reference for what each pack should enforce
- Support all existing hook packs: git hooks, Azure DevOps hooks, compliance, security, pre-commit lint, post-task QA
- Update tests to verify the new hook format

### Out of Scope
- Keeping the old custom safety model format (fully replaced)
- Adding new hook packs beyond what exists in the library
- Runtime hook execution (Claude Code handles that natively)

## Acceptance Criteria

- [ ] Generated `settings.json` uses Claude Code native hook format (`PreToolUse`/`PostToolUse` arrays)
- [ ] Hook entries correspond to the hook packs selected in the wizard
- [ ] If no hook packs are selected, `settings.json` has empty hook arrays
- [ ] Generated hooks follow Claude Code's expected schema (command matcher, hook script/message)
- [ ] Safety writer tests rewritten to verify native hook format
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design hook pack → native hook mapping | architect | — | Done |
| 2 | Rewrite safety writer with native hook format | developer | 1 | Done |
| 3 | Rewrite safety writer tests | tech-qa | 2 | Done |
| 4 | Full test suite & lint verification | tech-qa | 3 | Done |

## Notes

- Reference Foundry's own `.claude/settings.json` for the correct native hook format (it uses `PreToolUse`/`PostToolUse` with command matchers)
- The hook pack markdown files in the library describe what each hook should do — these need to be translated into concrete Claude Code hook definitions
- Related to BEAN-069 (Workflow Hook Packs) and BEAN-030 (Safety Writer Service)
- BEAN-124 (Hook-Selective Asset Copier) controls which hook markdown files are copied; this bean controls the settings.json hook definitions

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | Design hook pack → native hook mapping | architect | — | — | — |
| 2 | Rewrite safety writer with native hook format | developer | — | — | — |
| 3 | Rewrite safety writer tests | tech-qa | — | — | — |
| 4 | Full test suite & lint verification | tech-qa | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 25m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |