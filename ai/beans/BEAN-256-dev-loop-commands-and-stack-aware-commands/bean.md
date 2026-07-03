# BEAN-256: Dev-Loop Commands + Stack-Aware Command Selection

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-256 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 18:16 |
| **Completed** | 2026-04-17 19:15 |
| **Duration** | 59m (corrected 2026-07) |
| **Owner** | team |
| **Category** | App |

## Problem Statement

External audit (2026-04-17): "No dev-loop commands. Missing `/test`, `/build`, `/lint`, `/format`, `/dev`. The team has `/threat-model`, `/risk-liability`, `/ip-licensing`, `/contract-review`, `/regulatory-assessment` — governance-heavy, dev-light. Inverted priorities for a greenfield React app."

Two distinct issues:
1. **Missing baseline commands.** A generated project has no ergonomic commands for the daily dev loop — run tests, build, lint, dev server.
2. **Governance commands shipped by default.** Legal/compliance commands are in the default copy set when personas like `legal-counsel` are not even selected.

Both land on the same lever: **command pack selection should respond to the composition**, not ship everything or ship a fixed default.

## Goal

The generated `.claude/commands/` set contains the ergonomic dev-loop commands appropriate for the selected expertise, and does NOT contain heavy governance commands unless the composition opts in via an explicit persona or flag.

## Scope

### In Scope
- Add dev-loop commands to the library: `/test`, `/build`, `/lint`, `/format`, `/dev` — each with minimal stack-aware content (or composition-rendered variants).
- Map expertise → dev-loop command set (e.g., `python` → `uv run pytest`, `uv run ruff check`; `node`/`react`/`typescript` → `npm test`, `npm run build`, etc.).
- Define selection rules for governance commands: `/threat-model`, `/risk-liability`, `/ip-licensing`, `/contract-review`, `/regulatory-assessment` ship only when their associated persona (`security-engineer`, `legal-counsel`, `compliance-risk`) is on the team.
- Update `foundry_app/services/asset_copier.py` or the equivalent copier logic to apply the command-selection rules.
- Tests: a minimal composition (small-python-team) does not include `/ip-licensing`; a composition with `legal-counsel` does.
- Tests: a React/TS composition gets React-flavored `/test` and `/build`.

### Out of Scope
- Writing the actual test/build scripts for every stack (cover the common cases only).
- Custom command authoring by users.
- Redesigning the copier architecture.
- Hook selection (BEAN-255).

## Acceptance Criteria

- [ ] Library gains `/test`, `/build`, `/lint`, `/format`, `/dev` commands with stack-aware content (at least Python and Node/React/TS variants).
- [ ] Selection rules documented in `ai/context/command-selection.md` (or library README).
- [ ] Governance commands no longer appear in the generated project unless the composition explicitly includes the associated persona or flag.
- [ ] Regenerating `examples/small-python-team.yml` produces a `.claude/commands/` listing that includes dev-loop commands and excludes legal/compliance commands.
- [ ] Tests cover the selection rules end-to-end.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

> Skipped: BA (default — clear acceptance criteria), Architect (default — change is contained to one module; design alternative noted in bean Notes).

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add dev-loop command files to library (python + node/react/ts variants) | Developer | — | Done |
| 2 | Implement command/skill selection rules in `asset_copier.py` | Developer | 1 | Done |
| 3 | Document selection rules in `ai/context/command-selection.md` | Developer | 2 | Done |
| 4 | Add tests for dev-loop selection and governance gating; run full suite + ruff | Tech-QA | 2,3 | Done |

## Changes

| File | Lines |
|------|-------|
| `ai-team-library/claude/commands/dev-loop/python/{test,build,lint,format,dev}.md` | +149 (new) |
| `ai-team-library/claude/commands/dev-loop/node/{test,build,lint,format,dev}.md` | +146 (new) |
| `foundry_app/services/asset_copier.py` | +204/-10 |
| `ai/context/command-selection.md` | +63 (new) |
| `tests/test_asset_copier.py` | +234/-0 |

## Notes

**Pairs with BEAN-255.** Both close the "generation is not stack-aware" gap.

**Stance 1 alignment.** Per BEAN-251/253 (planning-only), the dev-loop commands *invoke* user-configured tooling — they do not install it. `/test` runs whatever test runner the user set up; it doesn't supply the test runner. The command docs should assume the user has initialized their stack and list which tool the command invokes (e.g., `/test (pytest)`, `/test (vitest)`).

**Interaction with BEAN-249.** If BEAN-249 is in flight (audit command/skill duplication), that audit should include the new dev-loop commands from this bean.

**Composition field.** A new `spec.generation.command_profile: "dev-only" | "full"` could replace the per-persona inference if the implementation gets complicated. Architect call.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add dev-loop command files to library (python + node/react/ts variants) | Developer | — | — | — | — |
| 2 | Implement command/skill selection rules in `asset_copier.py` | Developer | — | — | — | — |
| 3 | Document selection rules in `ai/context/command-selection.md` | Developer | — | — | — | — |
| 4 | Add tests for dev-loop selection and governance gating; run full suite + ruff | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 1269h 50m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |