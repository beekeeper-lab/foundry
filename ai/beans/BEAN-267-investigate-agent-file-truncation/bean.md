# BEAN-267: Investigate Reported Agent File Truncation in Multi-Expertise Compositions

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-267 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 18:45 |
| **Completed** | 2026-04-17 18:47 |
| **Owner** | developer + tech-qa |
| **Duration** | 1269h 39m |
| **Category** | App |

> Skipped: BA (default — defect is code-level, not requirements-ambiguous), Architect (default — fix is localized to one function in one service).

## Problem Statement

External review (2026-04-17): "All 6 `.claude/agents/*.md` files are
truncated mid-code-block. Every one ends like: `'target': 'ES2022',`
— the tsconfig Baseline jsonc fence never closes. The agent snapshot
loader is cutting the expertise section too aggressively."

Could not reproduce in a fresh `small-python-team.yml` generation
(Python-only composition, agent files close cleanly). The report is
specific to a React/TypeScript composition with ~6 personas and at
least one expertise that embeds an unterminated jsonc block
(likely `typescript` conventions containing a baseline `tsconfig.json`
example).

If the report is accurate, every agent file in that composition ships
with an unclosed code fence — which breaks Markdown rendering, confuses
the agent, and indicates the agent writer is truncating content
mid-fence rather than boundary-aware.

## Goal

Regenerate a representative React/TypeScript composition, confirm or
refute the truncation claim, and — if confirmed — make the agent
writer boundary-aware so it never truncates inside a fenced code block.

## Scope

### In Scope
- Build or identify a React/TypeScript example composition that exercises
  the reported case (e.g. `react`, `typescript`, `node` expertise +
  6 personas).
- Regenerate it and inspect every `.claude/agents/<persona>.md` for
  unclosed code fences and mid-statement truncation.
- If reproduced: fix `foundry_app/services/agent_writer.py` (or
  whichever component emits the expertise-context excerpt in agent
  files) so it never cuts inside a fenced block.
- Tests: an agent file with an embedded expertise that contains a jsonc
  block renders with balanced code fences.
- If not reproducible in the current codebase, document the attempt
  and close as Deferred with evidence.

### Out of Scope
- Rewriting the expertise-extraction logic wholesale.
- Changing how much expertise content appears in agent headers
  (that's a size-budget question — separate bean if needed).

## Acceptance Criteria

- [x] A regeneration of a React/TS-flavored composition is performed
      and its agent files inspected.
- [x] The investigation's findings are recorded in the bean Notes.
- [x] The defect was confirmed and the fix landed with a regression test
      that asserts balanced code fences in every generated agent file.
- [x] All tests pass (`uv run pytest` → 1852 passed).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Reproduce truncation against `typescript` conventions (via `_extract_expertise_highlights`) | developer | — | Done |
| 2 | Make the expertise-highlights extractor fence-aware | developer | 1 | Done |
| 3 | Add regression test: generated agent files always have balanced ` ``` ` fences | tech-qa | 2 | Done |
| 4 | Run `uv run pytest` + `uv run ruff check foundry_app/` | tech-qa | 3 | Done |

## Changes

| File | Lines |
|------|-------|
| `foundry_app/services/agent_writer.py` | `_extract_expertise_highlights` — fence-aware truncation |
| `tests/test_agent_writer.py` | +3 test classes / 4 tests (unit + end-to-end + real-library) |

## Notes

**Source.** External review (2026-04-17).

**Reproduction.** Confirmed. `_extract_expertise_highlights` captures the
Defaults section and hard-breaks at 15 lines. For `typescript/conventions.md`
the 15th highlight lands at `"target": "ES2022",` — inside the `jsonc`
`tsconfig Baseline` fence, exactly as the external review described. Every
`.claude/agents/<persona>.md` rendered against the typescript expertise
therefore ended with an unclosed `` ``` `` fence.

**Fix.** `_extract_expertise_highlights` now tracks fence state during the
scan. When the soft cap (`_MAX_EXPERTISE_HIGHLIGHT_LINES = 15`) is hit
while a `` ``` `` fence is open, extraction continues until the fence
closes — bounded by a hard cap (4× the soft cap) to prevent runaway on
malformed input. A final safety net drops any dangling opener that a
malformed source leaves unclosed. Net effect: every generated agent file
has a balanced number of `` ``` `` fences.

**Verification.**
- Direct call on `ai-team-library/expertise/typescript/conventions.md`
  now produces a balanced 2-fence excerpt ending with the closing `` ``` ``.
- `TestRealLibraryAgentFencesBalanced` runs the full `full-stack-web.yml`
  composition (react + typescript + node + clean-code × 9 personas) against
  the real library and asserts every written agent file has an even fence
  count.
- Full suite: **1852 passed**, 0 failures. `ruff` clean.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Reproduce truncation against `typescript` conventions (via `_extract_expertise_highlights`) | developer | — | — | — | — |
| 2 | Make the expertise-highlights extractor fence-aware | developer | — | — | — | — |
| 3 | Add regression test: generated agent files always have balanced ` ``` ` fences | tech-qa | — | — | — | — |
| 4 | Run `uv run pytest` + `uv run ruff check foundry_app/` | tech-qa | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 1269h 39m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |