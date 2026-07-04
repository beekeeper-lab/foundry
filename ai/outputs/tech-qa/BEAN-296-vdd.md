# BEAN-296 — VDD Verification Report

| Field | Value |
|-------|-------|
| **Bean** | BEAN-296 — ClaudeKit plugin packaging (ADR-016 phase 2) |
| **Date** | 2026-07-04 |
| **Verifier** | tech-qa |

**Verdict:** PASS

Programmatic gate (`uv run foundry-cli vdd 296 --manual pass`) reports
`Aggregate verdict: PASS` — see `ai/outputs/tech-qa/vdd-296.md`. Full suite:
**2567 passed, 0 failed** (`QT_QPA_PLATFORM=offscreen uv run pytest -q`).

## First run (history note)

The initial verification (2026-07-04, first run) returned **FAIL**: bean.md
AC #1 referenced a truncated ADR filename
(`ADR-016-...-contribution-fl.md` instead of `...-contribution-flow.md`),
so the gate's file-contains check could not resolve the path. Deliverable
content was already correct. Bounced to Team-Lead, who corrected the AC path
in bean.md and additionally promoted this report's non-blocking
`permissions.deny` observation into a migration-caveat bullet in the kit
README's plugin-install section. No deliverable content changed; re-run of
the gate passes.

## Per-AC Results

| # | AC | Result | Evidence |
|---|----|--------|----------|
| 1 | ADR-016 updated with phase-2 outcome (file-contains ::Status) | PASS | Gate: "found 'Status' in ai/context/decisions/ADR-016-kit-distribution-plugin-direction-with-a-contribution-flow.md". Status line reads: "Accepted — phase 2 (plugin packaging) shipped 2026-07-04 via BEAN-296: plugin.json + hooks.json + self-hosted marketplace in claude-kit; install flow documented in the kit README. Pilot consumer migration pending (phase 3)." |
| 2 | Plugin manifest exists (`.claude/shared/.claude-plugin/plugin.json`) | PASS | File exists, parses; name `claude-kit`, version `1.0.0`, description and author present |
| 3 | Marketplace listing exists (`.claude/shared/.claude-plugin/marketplace.json`) | PASS | File exists, parses; name `beekeeper-lab`, owner present, `plugins[0]` = claude-kit with `source: "."` and description |
| 4 | Install/update flow documented (README contains "marketplace") | PASS | README.md lines 100–122: `/plugin marketplace add beekeeper-lab/claude-kit`, `/plugin install claude-kit@beekeeper-lab`, hybrid-staging note, and new migration-caveat bullet on `permissions.deny` |
| 5 | All tests pass | PASS | `QT_QPA_PLATFORM=offscreen uv run pytest -q` → **2567 passed, 4 warnings in 15.29s**; gate row 5 PASS |

## Packaging Findings

**JSON validity.** All three files parse cleanly:
`python3 -c "import json; [json.load(open(p)) for p in (...)]"` → OK for
plugin.json, marketplace.json, hooks.json.

**hooks.json script references.** All nine `${CLAUDE_PLUGIN_ROOT}/hooks/*.py`
references resolve to real files under `.claude/shared/hooks/`:
bash_safety.py, write_safety.py, validate-task-inputs.py, vdd-gate.py,
handoff-reminder.py, telemetry-stamp.py, format-on-save.py,
session-start-context.py, stop-quality-reminder.py.

**Fidelity to settings.json.** Event structure mirrors
`.claude/shared/settings.json` exactly: 6 PreToolUse entries (including the
identical inline branch-protection shell command with the same matcher
`Edit|Write|NotebookEdit`), 2 PostToolUse, 1 SessionStart, 1 Stop — same
matchers, same order, no hook lost in translation. Zero
`$CLAUDE_PROJECT_DIR/.claude/shared` paths remain in hooks.json
(`grep 'CLAUDE_PROJECT_DIR' hooks.json` → no matches).

**permissions.deny caveat (resolved).** `settings.json` carries a
`permissions.deny` block (force-push, .env/SSH-key reads, etc.) that the
plugin hooks.json format cannot carry. Now documented in the kit README's
plugin-install section (lines 118–122): plugin consumers should copy that
block into their project's own `.claude/settings.json` until permissions
ship in a plugin-native form. Verified the bullet matches the intent of the
original finding.

## Recommendation

**Go for merge.** Programmatic gate green, full suite green, all packaging
checks verified, bounce resolved with no deliverable content change.
