# BEAN-285: Documentation + CLAUDE.md Updates for Media Skills

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-285 |
| **Status** | In Progress |
| **Priority** | Medium |
| **Created** | 2026-04-29 |
| **Started** | 2026-04-29 21:44 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | Process |
| **Depends On** | BEAN-280, BEAN-281, BEAN-282, BEAN-283, BEAN-284 |

## Problem Statement

BEAN-280 through BEAN-284 introduce a substantial new capability surface: a kit-distributed-skills architecture, two new external dependencies (OpenAI, ElevenLabs), a new composition-spec flag, two plan-file conventions, a unified quality knob, and an env-var discovery convention. None of that is documented in CLAUDE.md, the skill READMEs, the project README, or the generated-project README template. Without docs, the next agent (or human) hitting any of this will reinvent or misuse it.

## Goal

Every doc surface that a future agent or operator could consult to learn about media generation reflects the new design accurately, and the env-var requirements are recorded where they'll be checked.

## Scope

### In Scope

- **Foundry root `CLAUDE.md`**: add a "Media Skills" section listing the env-var requirements (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`), the `.env` lookup precedence (cwd → parents → `$HOME`), the plan-first workflow link, and the cost-discipline note.
- **`.claude/shared/CLAUDE.md`** (ClaudeKit, gets distributed):
  - "Available Skills" section gains `generate-image` and `generate-audio` entries with a one-line description of plan-driven mode and provider routing.
  - Brief "Kit-Distributed Skills" section explaining that some skills (`generate-image`, `generate-screen`, `generate-audio`, `_media_lib`) are owned by ClaudeKit and reach generated projects via either subtree mode or the asset_copier kit-distribution path.
- **`generate-image/SKILL.md`**: rewrite to cover both plan-driven and single-shot modes, frontmatter keys, provider routing, unified quality flag, sidecar schema, env vars.
- **`generate-audio/SKILL.md`**: new file covering inline `> 🎙️` blocks, plan format, voice routing, manifest schema, content-hash dedup contract, env vars, cost expectations.
- **Foundry README.md**: pipeline section gains a note that generated projects can opt into media skills via `include_media_skills: true` in the composition YAML.
- **Generated-project README template** (in `ai-team-library/`): if media skills are included, the README ships with a "Generating images and audio" section explaining the plan-first workflow and pointing at `IMAGE-PLAN.md` / `NARRATION-PLAN.md`.
- **`ai/context/decisions.md`**: BEAN-280's ADR (kit-distributed skills) is captured. Reference back to it from this bean's notes.
- **`ai/context/project.md`**: update module map to include `_media_lib`, `generate-image`, `generate-audio`.
- **MEMORY.md doc checklist**: add the new files to the "Always check" / "Check when relevant" lists so future docs-update sweeps cover them.
- **Build pipeline example**: a short worked example in `.claude/shared/skills/generate-audio/SKILL.md` (or a sibling `BUILD_EXAMPLE.md`) showing how a downstream build tool would use `_media_lib.text.hash_text` to dedupe MP3s across pages. Library function + example, not a runnable script.
- **`.env` template at Foundry root** (`.env.example`): list the three keys with placeholder values + comments. The real `.env` already has `GEMINI_API_KEY`; the user will add `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` when they want those providers.

### Out of Scope

- Any code changes (those live in the prior beans).
- Wizard UI copy (separate UI bean, not yet filed).
- A full build-pipeline implementation — only the example/library function lands here.

## Acceptance Criteria

- [ ] Foundry CLAUDE.md "Media Skills" section exists.
- [ ] `.claude/shared/CLAUDE.md` lists generate-image and generate-audio with kit-distributed marker.
- [ ] Both SKILL.md files reflect actual implementation behavior (plan + single-shot modes for images; inline-block + manifest for audio).
- [ ] Foundry README mentions media-skills opt-in.
- [ ] Generated-project README template includes media-workflow guidance when the flag is on.
- [ ] `decisions.md` ADR exists from BEAN-280; cross-referenced.
- [ ] `project.md` module map updated.
- [ ] MEMORY.md doc checklist includes the new files.
- [ ] `.env.example` lists all three keys with comments.
- [ ] Build-pipeline content-hash example exists.
- [ ] No tests required for docs (per project convention), but lint clean (`uv run ruff check foundry_app/`) since some doc generation may touch code.

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Apply doc edits across all surfaces | Developer | — | Pending |
| 02 | Verify acceptance criteria | Tech-QA | 01 | Pending |

> Activated: Developer (technical-writer not in this team), Tech-QA.
> Skipped: BA, Architect (no scope/design decisions; just documentation of the prior beans' decisions).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Depends on BEAN-280, BEAN-281, BEAN-282, BEAN-283, BEAN-284.** Land last in the wave.

**Don't duplicate the cost table.** The table lives in `generate_image.py` (load-bearing). Docs reference it; they don't re-state it.

**The `.env.example` is important.** Currently the project has a real `.env` with one key. Adding two more keys without an `.env.example` makes onboarding fragile.

**Reference doc:** `Course_Material/AGENTIC-MEDIA-SKILLS.md` is the source design. Cite it from `decisions.md` as the inspiration but document Foundry's adapted choices in our own words.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 01 | Apply doc edits across all surfaces | Developer | — | — | — | — |
| 02 | Verify acceptance criteria | Tech-QA | — | — | — | — |