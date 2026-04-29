# BEAN-280: ClaudeKit as Canonical Source for Cross-Project Skills

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-280 |
| **Status** | In Progress |
| **Priority** | High |
| **Created** | 2026-04-29 |
| **Started** | 2026-04-29 18:29 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |
| **Depends On** | — |

## Problem Statement

Foundry has two paths for getting `.claude/` content into a generated project:

1. **Subtree mode** (`subtree_setup.py`) — `git subtree add --prefix=.claude` from `claude-kit.git`. Generated project receives the entirety of `.claude/shared/`.
2. **Library-copy mode** (`asset_copier.py`) — copies from `ai-team-library/claude/` into the new project's `.claude/`.

The two paths produce **different skill sets**. The existing `generate-image` skill lives only in `.claude/shared/skills/` (ClaudeKit). It is **not** in `ai-team-library/claude/skills/`. So today, library-copy-mode generated projects silently miss `generate-image` (and `generate-screen`). This will repeat for every future cross-project skill — including the media skills proposed in BEAN-282 / BEAN-283 — unless the architecture is fixed.

The right answer is a single source of truth. ClaudeKit owns cross-project skills; ai-team-library owns project-template assets (commands, hooks, persona templates, plan skeletons). Both modes pull skills from ClaudeKit.

## Goal

Library-copy-mode and subtree-mode generated projects ship with the same set of cross-project skills, sourced from a single canonical location (`.claude/shared/skills/`). No mirror, no drift.

## Scope

### In Scope

- **ADR** in `ai/context/decisions.md` documenting:
  - The split: ClaudeKit = cross-project skills; ai-team-library = project-template assets.
  - The "kit-distributed skills" registry (an explicit list of skill names ClaudeKit owns).
  - How asset_copier resolves them in library-copy mode.
- **`asset_copier.py` extension**:
  - New `claude_kit_root` parameter on `copy_assets`, defaulting to `<foundry-root>/.claude/shared/`.
  - New constant `_KIT_DISTRIBUTED_SKILLS` (initially `["generate-image", "generate-screen"]` — extended by BEAN-282/283).
  - When in library-copy mode, asset_copier copies kit-distributed skills from `claude_kit_root/skills/<name>/` instead of `ai-team-library/claude/skills/<name>/`.
  - Conflict / overlay rules match the existing copier's behavior.
- **Generator wiring**: `generator.py` passes `claude_kit_root` through to `asset_copier`. Default resolves to the bundled submodule path.
- **Backfill the existing gap**: library-copy-mode projects start receiving `generate-image` and `generate-screen` once this lands.
- **Tests**:
  - copy_assets correctly resolves kit-distributed skills from `claude_kit_root` in library-copy mode.
  - copy_assets skips kit-distributed skills in subtree mode (subtree already covers them).
  - End-to-end: a generated project in library-copy mode has `.claude/skills/generate-image/` after generation.

### Out of Scope

- Implementing the new media skills themselves (BEAN-282, BEAN-283).
- Symlinks, mirroring scripts, or any duplication of skill files.
- Migration of other skills currently in `ai-team-library/claude/skills/` — those remain owned by the library.
- Subtree-mode behavior changes (it already pulls from ClaudeKit).

## Acceptance Criteria

- [ ] ADR added to `ai/context/decisions.md` with the canonical-source rationale and the kit-distributed skill registry.
- [ ] `_KIT_DISTRIBUTED_SKILLS` constant defined in `asset_copier.py`.
- [ ] `copy_assets` accepts `claude_kit_root` parameter; sensible default.
- [ ] In library-copy mode, kit-distributed skills resolve from `claude_kit_root/skills/<name>/`.
- [ ] In subtree mode, kit-distributed skills are not double-copied.
- [ ] Generated project (library-copy mode) ships with `.claude/skills/generate-image/` and `.claude/skills/generate-screen/`.
- [ ] Tests cover both modes.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | ADR — kit-distributed skills pattern | Architect | — | Done |
| 02 | asset_copier extension + tests | Developer | 01 | Pending |
| 03 | Verify acceptance criteria | Tech-QA | 01, 02 | Pending |

> Activated: Architect (cross-cutting service change + ADR + new module boundary), Developer, Tech-QA.
> Skipped: BA (requirements concrete from spec).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Foundation for media skills.** BEAN-282 and BEAN-283 add to `_KIT_DISTRIBUTED_SKILLS`. Land this bean first.

**Why not symlinks or a sync script?** Both create a second location to maintain. The right architecture has one home for each skill.

**ai-team-library remains valuable.** It still owns commands, hooks, persona templates, plan skeletons (BEAN-284), and orchestration scaffolding. This bean only carves out cross-project *skills* as ClaudeKit-owned.

**Reference:** `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md` motivates the media skills that exercise this pattern.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 01 | ADR — kit-distributed skills pattern | Architect | — | — | — | — |
| 02 | asset_copier extension + tests | Developer | — | — | — | — |
| 03 | Verify acceptance criteria | Tech-QA | — | — | — | — |