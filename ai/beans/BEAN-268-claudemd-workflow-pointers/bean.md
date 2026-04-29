# BEAN-268: Add Workflow Pointers Section to Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-268 |
| **Status** | Deferred |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
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

- [ ] Generated CLAUDE.md contains a `## Workflow` section naming the
      bean workflow and the core commands.
- [ ] Section is ≤25 lines.
- [ ] An agent reading only CLAUDE.md can discover the bean backlog and
      the `/long-run` / `/show-backlog` commands without external
      context.
- [ ] Tests cover the new section.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

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
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
