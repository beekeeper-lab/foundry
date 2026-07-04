# BEAN-268: Add Workflow Pointers Section to Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-268 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-30 09:39 |
| **Completed** | 2026-04-30 09:42 |
| **Duration** | 3m (corrected 2026-07) |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

External review (2026-04-17): "CLAUDE.md is too thin. Doesn't mention
beans, the skill library, `/pick-bean`, `/long-run`, or the workflow at
all. An agent cold-starting here sees the team roster and directory
tree, then stops."

BEAN-164 and BEAN-233 deliberately pruned the generated CLAUDE.md to a
lean form (~100 lines) to avoid context bloat. That pruning went too
far: it removed the signposts an agent needs to discover the bean
workflow and the available commands. A cold-start agent should see at
least a single line per core concept with a pointer to the detailed
source.

## Goal

A freshly generated CLAUDE.md contains a small **Workflow** section
that names the bean workflow, the `_index.md` backlog, and the top-level
slash commands (e.g. `/long-run`, `/show-backlog`, `/pick-bean`) with
one-line descriptions and file pointers. The section adds ~15-25 lines
total, not a re-expansion to pre-BEAN-164 size.

## Scope

### In Scope
- Update `foundry_app/services/compiler.py`'s `_build_lean_claude_md` to
  emit a `## Workflow` section (or similar heading) after the Team
  table.
- Include:
  - One sentence on the bean workflow with a pointer to
    `ai/beans/_index.md` and `ai/context/bean-workflow.md` (if the
    latter exists in the generated project).
  - A short list of the top ~5-7 commands that ship by default, with
    one-line descriptions and the file path under `.claude/commands/`.
- Make the section opt-out via a composition flag if that is required
  to keep tests deterministic.
- Tests: assert the new section is present and contains the expected
  pointers.

### Out of Scope
- Re-expanding the rest of CLAUDE.md.
- Listing every command (be selective — only the ones most relevant to
  day-1 operation).
- Changing command content.

## Acceptance Criteria

- [x] Generated CLAUDE.md contains a `## Workflow` section naming the
      bean workflow and the core commands.
- [x] Section is ≤25 lines.
- [x] An agent reading only CLAUDE.md can discover the bean backlog and
      the `/long-run` / `/show-backlog` commands without external
      context.
- [x] Tests cover the new section.
- [x] All tests pass (`uv run pytest`).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add Workflow section to generated CLAUDE.md | developer | — | Done |
| 2 | Verify Workflow section | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (default) — small focused enhancement to existing CLAUDE.md generator, no requirements ambiguity, no new design decisions.

## Changes

| File | Lines |
|------|-------|
| ai/beans/BEAN-268-claudemd-workflow-pointers/bean.md | 40 |
| ai/beans/BEAN-268-claudemd-workflow-pointers/tasks/01-developer-workflow-section.md | 38 |
| ai/beans/BEAN-268-claudemd-workflow-pointers/tasks/02-tech-qa-verify.md | 33 |
| ai/beans/_index.md | 2 |
| ai/outputs/tech-qa/bean-268-verification.md | 29 |
| foundry_app/services/compiler.py | 29 |
| tests/test_compiler.py | 57 |
| **Total** | **7 files: +209 / -19** |

## Notes

**Source.** External review (2026-04-17).

**Tension.** BEAN-164 and BEAN-233 deliberately shrank CLAUDE.md; this
bean re-adds a small subset of that content. The principle: signposts
are cheap, full docs are expensive. Keep signposts, don't re-expand.

**Interaction.**
- If BEAN-256 (dev-loop commands) lands first, its commands should
  appear in this pointer list.
- BEAN-269 (explicit orchestration model) adds a **policy** section to
  CLAUDE.md. This bean adds **navigation** pointers. Land them
  together so CLAUDE.md gains coherent "how this project works"
  content in one pass rather than two drafts.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add Workflow section to generated CLAUDE.md | developer | < 1m | 1,668,905 | 3,916 | $2.90 |
| 2 | Verify Workflow section | tech-qa | < 1m | 1,507,892 | 3,734 | $2.62 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 3,176,797 |
| **Total Tokens Out** | 7,650 |
| **Total Cost** | $5.52 |