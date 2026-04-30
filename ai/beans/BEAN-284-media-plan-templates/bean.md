# BEAN-284: Media Plan Templates + Foundry Scaffolder Integration

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-284 |
| **Status** | In Progress |
| **Priority** | Medium |
| **Created** | 2026-04-29 |
| **Started** | 2026-04-29 21:36 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | Infra |
| **Depends On** | BEAN-282, BEAN-283 |

## Problem Statement

The image and audio skills (BEAN-282, BEAN-283) are plan-driven by design — the plan is the gate, generation is downstream. But a freshly-Foundry-generated project arrives with the skills installed and **no plan files**. The first user has to either:

1. Find the format documentation, hand-author `IMAGE-PLAN.md` and `NARRATION-PLAN.md` from scratch.
2. Skip plan-mode entirely and use the single-shot CLI — at which point the plan-first discipline is lost on day one.

Right thing: ship plan templates with sensible default frontmatter, opt-in via the composition spec, stamped by the scaffolder so they appear at the project root of every Foundry-generated project that opts in.

## Goal

A new Foundry project optionally arrives with `IMAGE-PLAN.md` and `NARRATION-PLAN.md` skeletons at the project root, frontmatter pre-filled with kit defaults (Gemini, `eleven_multilingual_v2`, `rachel`), an empty body, and inline guidance comments showing how to add entries.

## Scope

### In Scope

- **Templates in `ai-team-library/templates/media/`**:
  - `IMAGE-PLAN.md.j2` — Jinja2 template with frontmatter (`Style`, `Generator`, `Aspect ratio`, `Background`, `Text in image`, `Avoid`) and one commented-out example image entry.
  - `NARRATION-PLAN.md.j2` — Jinja2 template with frontmatter (`Voice`, `Model`) and an explanation of the `> 🎙️` inline-block convention.
  - Each template's frontmatter is interpolated from `CompositionSpec` fields where possible (project name in title; `Generator:` and `Voice:` from kit defaults).
- **`CompositionSpec` flag**: `include_media_skills: bool = False` (or similar). When `True`, the scaffolder stamps the plan templates.
- **Scaffolder change** (`foundry_app/services/scaffold.py` or `seeder.py`, whichever owns optional asset emission today):
  - When `include_media_skills` is set, render and write the two plan files to the generated project root.
  - Don't overwrite if the user already has plans (overlay-safe like the rest of asset_copier).
- **Tests** (`tests/services/test_scaffold_media.py`):
  - Flag off → no plan files written.
  - Flag on → both plan files appear at project root with expected frontmatter.
  - Existing plan files are preserved (no overwrite).
  - Frontmatter interpolation: project name shows up in the title.

### Out of Scope

- Any change to BEAN-282/283 skill behavior.
- Changes to `IMAGE-PLAN-ADDITIONS.md` workflow (the additions file is a runtime convention, not something the scaffolder pre-creates).
- UI wizard surfacing of `include_media_skills` — separate Foundry UI work; the spec field exists, the wizard checkbox can be added in a follow-up.

## Acceptance Criteria

- [ ] `ai-team-library/templates/media/IMAGE-PLAN.md.j2` exists with the documented frontmatter keys.
- [ ] `ai-team-library/templates/media/NARRATION-PLAN.md.j2` exists with the documented frontmatter keys.
- [ ] `CompositionSpec.include_media_skills` field added (Pydantic-validated, defaults to `False`).
- [ ] Scaffolder writes both plan files to project root when the flag is `True`.
- [ ] Files are not overwritten if they already exist.
- [ ] Frontmatter is interpolated with project-spec values (title at minimum).
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Implement templates + spec field + scaffolder | Developer | — | Done |
| 02 | Verify acceptance criteria | Tech-QA | 01 | Pending |

> Activated: Developer, Tech-QA.
> Skipped: BA (requirements concrete), Architect (additive flag + template emission, no boundary changes; follows existing scaffolder conventions).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Depends on BEAN-282, BEAN-283.** Templates must match the parsers' expected frontmatter shape; build those first so the contract is firm.

**Project root vs subdirectory.** Plans land at project root (per recommendation; matches Stonewaters convention). The user can move them and pass `--plan path/to/file.md` to the generators if they prefer scoping under `media/` or similar.

**Wizard integration is a follow-up.** This bean exposes the spec field and wires the scaffolder. A separate UI bean can add the checkbox to `wizard_pages/`.

**Default frontmatter.** Don't pre-fill style descriptions — that's project-specific and the user must own it (plan-first discipline). Do pre-fill structural defaults: `Aspect ratio: 16:9`, `Background: white`, `Text in image: minimal`, `Generator: gemini-3-pro-image-preview`.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 01 | Implement templates + spec field + scaffolder | Developer | — | — | — | — |
| 02 | Verify acceptance criteria | Tech-QA | — | — | — | — |
| 01 | Implement templates + spec field + scaffolder | Developer | — | — | — | — |
| 02 | Verify acceptance criteria | Tech-QA | — | — | — | — |