# BEAN-249: Audit Library Command/Skill Duplication

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-249 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-30 08:53 |
| **Completed** | 2026-04-30 09:09 |
| **Duration** | 1572h 2m |
| **Owner** | team-lead |
| **Category** | Infra |

## Problem Statement

External review (2026-04-17): "Commands and skills still duplicate too much. `/compile-team` and the `compile-team` skill are clearly describing the same capability, but both are long-form operational specs. That creates drift risk." The intended split is:

- **Command** (`.claude/commands/<name>.md`) = short user-facing trigger; reminds the reader what the command does and points to the skill.
- **Skill** (`.claude/skills/<name>/SKILL.md`) = canonical execution specification. Single source of truth for behavior.

Drift risk: when both files carry the same operational detail, one inevitably falls behind the other, and readers cannot tell which is authoritative.

The Foundry repo's own `.claude/commands/` files are generally short, but the *library* copies that get generated into downstream projects (`ai-team-library/claude/commands/` vs. `ai-team-library/claude/skills/`) need to be audited systematically.

## Goal

Every library-shipped command is a short trigger (≤30 lines) that names the skill it invokes. Every library-shipped skill is the canonical spec. No command restates the skill's detailed process steps, quality criteria, or error taxonomy.

## Scope

### In Scope
- Audit every `ai-team-library/claude/commands/*.md` against its paired `ai-team-library/claude/skills/<name>/SKILL.md`. Build a table of `{command, skill, command-lines, skill-lines, overlap notes}`.
- Trim commands where duplication is significant. Target ≤30 lines per command file.
- Preserve the command's role as the user-facing doc: keep name, one-sentence description, usage, argument list, and a pointer to the skill.
- Delete from commands: full "Process" sections, error condition tables, quality criteria, implementation detail — anything that already lives in the skill.
- Do NOT modify skills in this bean (focus is on trimming commands). If a skill is weak or missing detail, file a follow-up bean.

### Out of Scope
- Changing the set of commands or skills offered.
- Modifying `.claude/commands/` in the Foundry repo itself (that's the scaffolding; the library is what ships into generated projects).
- Moving content from skills to commands (the direction is one-way: commands shrink).

## Acceptance Criteria

- [x] An audit table in `ai/outputs/team-lead/bean-249-command-skill-audit.md` lists every library command/skill pair with before/after line counts.
- [x] Every `ai-team-library/claude/commands/*.md` is ≤30 lines of content (front matter + one-sentence description + usage + skill pointer).
- [x] No command file contains "Process" or "Error Conditions" sections; those live only in skills.
- [x] `uv run foundry-cli generate examples/small-python-team.yml --library ai-team-library` still emits every expected command file.
- [x] All tests pass (`uv run pytest`).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Audit and trim library commands | developer | — | Done |
| 2 | Verify audit and trim | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (default) — mechanical audit/trim with clear acceptance criteria, no requirements ambiguity or design decisions.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**Origin.** External review, 2026-04-17: "command = user-facing wrapper, skill = canonical execution logic. Right now both are trying to be canonical."

**Measuring duplication.** The audit should identify commands that restate the skill's Process section word-for-word, or that re-list acceptance criteria / error taxonomy. Minor overlap (name, one-line description) is expected and fine.

**Follow-up risk.** If some commands have content that is *not* in the skill (command-only detail), that detail needs to migrate *into* the skill, not disappear. Flag those during the audit.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Audit and trim library commands | developer | 13m | 627,657 | 4,837 | $1.55 |
| 2 | Verify audit and trim | tech-qa | 2m | 287,940 | 2,393 | $0.64 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 15m |
| **Total Tokens In** | 915,597 |
| **Total Tokens Out** | 7,230 |
| **Total Cost** | $2.19 |