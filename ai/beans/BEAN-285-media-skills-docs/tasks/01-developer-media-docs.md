# Task 01: Apply Doc Edits Across All Surfaces (Media Skills)

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Land every doc surface change listed in BEAN-285 scope. The prior beans
(BEAN-280..284) introduced kit-distributed skills, two new external
dependencies (OpenAI, ElevenLabs), the `include_media_skills` flag, two
plan-file conventions, and an env-var discovery convention. None of
that is documented anywhere yet. Make every doc surface accurate.

## Inputs

- `ai/beans/BEAN-285-media-skills-docs/bean.md` — scope and acceptance criteria.
- **Existing docs to edit:**
  - `CLAUDE.md` (foundry root) — add Media Skills section.
  - `.claude/shared/CLAUDE.md` — Available Skills + Kit-Distributed Skills sections.
  - `README.md` (foundry root) — add media-skills opt-in note.
  - `ai/context/project.md` — module map.
  - `ai/context/decisions.md` — confirm BEAN-280 ADR exists; reference from this bean's notes if not already.
  - `.claude/shared/skills/generate-image/SKILL.md` — rewrite for current implementation.
  - `.claude/shared/skills/generate-audio/SKILL.md` — confirm/extend (BEAN-283 created it; verify it covers env vars + cost + manifest schema + content-hash dedup pointer).
- **New files to create:**
  - `.env.example` (foundry root) — three keys with comments.
  - `.claude/shared/skills/generate-audio/BUILD_EXAMPLE.md` — short worked example using `_media_lib.text.hash_text` for cross-page dedup.
  - Generated-project README template — see `foundry_app/services/scaffold.py` `_render_readme` (the README is rendered inline in Python, so add a conditional section there when `include_media_skills` is True).
- **Reference for content (read-only, summarize in Foundry's voice; don't copy verbatim):**
  - `.claude/shared/skills/generate-image/generate_image.py` — current implementation (frontmatter keys, provider routing, quality flag, cost rate).
  - `.claude/shared/skills/generate-audio/generate_audio.py` — manifest schema, cost rate, voice map, env var discovery.
  - `foundry_app/services/asset_copier.py` — `_KIT_DISTRIBUTED_SKILLS` registry.
  - `ai/beans/BEAN-280-claudekit-canonical-skills-distribution/bean.md` — kit-distributed skills design.

CONTEXT DIET: stay within these inputs. The bean's Notes warn against
duplicating the cost table — reference the source-of-truth, don't restate
it.

## Acceptance Criteria

- [ ] Foundry root `CLAUDE.md` has a "Media Skills" section listing the three env vars (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`), the `_media_lib.env.load_env` discovery precedence (cwd → parents → `$HOME`), the plan-first workflow (link to skills), and a one-line cost-discipline note.
- [ ] `.claude/shared/CLAUDE.md` "Available Skills" gains `generate-image` and `generate-audio` rows; new "Kit-Distributed Skills" section names the four kit-owned skills (`_media_lib`, `generate-image`, `generate-screen`, `generate-audio`) and the two distribution paths (subtree mode + asset_copier).
- [ ] `generate-image/SKILL.md` covers both plan-driven and single-shot modes, frontmatter keys (`Style`, `Generator`, `Aspect ratio`, `Background`, `Text in image`, `Avoid`), provider routing (Gemini default; OpenAI verified/unverified variants), unified `--quality` flag, sidecar `<slug>.json` schema, env vars.
- [ ] `generate-audio/SKILL.md` covers inline `> 🎙️` blocks, plan format (`Voice`, `Model`), voice routing (rachel default; raw IDs passthrough), per-source manifest schema (`{index, module, audio_file, text, size_bytes}`), the **stripped text** invariant, content-hash dedup contract pointer to `_media_lib.text.hash_text`, env vars, cost expectations.
- [ ] Foundry root `README.md` mentions `include_media_skills: true` opt-in.
- [ ] Generated-project README template (rendered by `scaffold.py:_render_readme`) gains a conditional "Generating images and audio" section when `include_media_skills` is True. The section points at `IMAGE-PLAN.md` and `NARRATION-PLAN.md` (which the same scaffold pass writes) and explains the plan-first workflow in 1–2 paragraphs.
- [ ] `ai/context/decisions.md` ADR-012 (or next available) cross-references kit-distributed skills (BEAN-280); ADR-011 (audio skill, BEAN-283) and ADR-010 (image skill, BEAN-282) already exist — confirm and link from this bean's Notes.
- [ ] `ai/context/project.md` module map includes `_media_lib`, `generate-image`, `generate-audio`.
- [ ] `MEMORY.md` doc checklist — add the new files (`.env.example`, both SKILL.md files, the BUILD_EXAMPLE.md) to the appropriate "Always check" / "Check when relevant" sections so future doc-update sweeps cover them.
- [ ] `.env.example` exists at foundry root with `GEMINI_API_KEY=`, `OPENAI_API_KEY=`, `ELEVENLABS_API_KEY=` and a one-line comment per key explaining when it's needed.
- [ ] Build-pipeline content-hash example exists (`generate-audio/BUILD_EXAMPLE.md` or inline section in SKILL.md). Library function (`_media_lib.text.hash_text`) usage shown; not a runnable script.
- [ ] Tests still pass (`uv run pytest`) — should be unaffected since this is doc-only, but confirm.
- [ ] Lint clean (`uv run ruff check foundry_app/`) — relevant if `scaffold.py` is touched for the README template addition.

## Definition of Done

- Every acceptance criterion green.
- Commit messages follow `BEAN-285 task 01: <area>` style. Multiple commits OK if helpful (e.g., one per major doc surface).
