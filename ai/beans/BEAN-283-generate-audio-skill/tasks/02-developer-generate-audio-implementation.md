# Task 02: Implement `generate-audio` Skill (ElevenLabs)

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-04-29 20:17 |
| **Completed** | 2026-04-29 20:44 |
| **Duration** | 27m |

## Goal

Build the new `generate-audio` skill at
`.claude/shared/skills/generate-audio/` per ADR-011 (from Task 01).
Take `Course_Material/Git_Fundamentals/scripts/generate_narration.py`
(274 lines) as the basis — production-tested. Adapt for Foundry
conventions: import `_media_lib.env.load_env` and
`_media_lib.text.normalize_narration_text` (BEAN-281), no cloned
voice IDs in source, `NARRATION-PLAN.md` frontmatter parsing,
char-count cost reporting, full skip-on-disk mode set.

Add `generate-audio` to `_KIT_DISTRIBUTED_SKILLS` so library-copy-mode
projects ship with it.

## Inputs

- `ai/beans/BEAN-283-generate-audio-skill/bean.md` — full scope
- `ai/context/decisions.md` — ADR-011 (audio skill design) and ADR-009 (kit distribution)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_narration.py` — basis (copy and adapt with attribution header)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md` — reference (manifest format, voice routing, cost rate)
- `.claude/shared/skills/_media_lib/env.py` — `load_env`
- `.claude/shared/skills/_media_lib/text.py` — `normalize_narration_text` (use this verbatim — do not reimplement)
- `foundry_app/services/asset_copier.py` — registry to extend with `"generate-audio"`
- `tests/` — directory for new tests
- `pyproject.toml` — only if you need to declare elevenlabs as dep (prefer `uv run --with elevenlabs` so it's not a hard runtime dep)
- `.claude/shared/skills/generate-audio/` — destination (does not exist yet; create it)

CONTEXT DIET: stay within these inputs.

## Pacing — commit at natural checkpoints

This is a substantial task. Commit at these checkpoints (interim message: `BEAN-283 task 02 (WIP): <chunk>`):

1. After: source-file `> 🎙️` blockquote scanner + tests pass.
2. After: `NARRATION-PLAN.md` frontmatter parser + tests pass.
3. After: ElevenLabs client integration (mocked) + voice routing + tests pass.
4. After: per-source manifest writer + content-hash invariant + tests pass.
5. After: skip-on-disk modes (`--force`, `--regenerate-changed`, `--dry-run`, `--all`) + orphan cleanup + tests pass.
6. After: cost reporting + char-count summary + tests pass.
7. Final: SKILL.md + `_KIT_DISTRIBUTED_SKILLS` registration + final commit (`BEAN-283 task 02: generate-audio skill (ElevenLabs)`).

Each interim commit must leave tests passing.

## Critical pieces

1. **Source = inline `> 🎙️` blocks.** Walk source markdown files (default glob `module-*.md`; `--all` includes auxiliary files). For each file, find contiguous blockquoted lines starting with the microphone emoji.
2. **Pre-send stripping** uses `_media_lib.text.normalize_narration_text`. The result is what's sent to ElevenLabs AND what's stored in the manifest's `text` field. Don't reimplement the normalization.
3. **Voice routing** — `voice_map` dict covers `rachel` (`21m00Tcm4TlvDq8ikWAM`) and a few stock ElevenLabs names. Unknown values pass through as raw IDs. `--voice <name-or-id>` overrides the frontmatter. **No cloned voice IDs in committed code.**
4. **`NARRATION-PLAN.md` parser** — frontmatter only: `Voice:`, `Model:`. CLI flags override frontmatter. The plan markdown is informational (review surface); inline source is authoritative.
5. **Manifest** at `audio/<source-stem>/manifest.json` — array of `{index, module, audio_file, text, size_bytes}`. `index` 1-based; MP3 filename is `NN_<source-stem>.mp3`. `text` is stripped narration.
6. **Skip-on-disk modes**:
   - Missing MP3 → generate.
   - `--regenerate-changed` → manifest's old `text` ≠ current stripped → regenerate; else skip.
   - `--force` → regenerate everything for this run.
   - `--dry-run` → walk plan, print, no API calls.
   - `--all` → include auxiliary source files beyond `module-*.md`.
7. **Orphan cleanup** — when rewriting a manifest, remove MP3s whose blocks no longer exist in current source.
8. **`_media_lib.env.load_env`** at startup. Requires `ELEVENLABS_API_KEY`.
9. **Cost summary** — total chars sent = total credits. End-of-run prints provider, count, total credits. Plan-aware: when invoked with a `NARRATION-PLAN.md`, also print "remaining in plan: X credits" if char totals are tracked there.
10. **Skill files**: `generate_audio.py` (basis = Stonewaters' `generate_narration.py`, 274 lines, with attribution header) and `SKILL.md` documenting inline source convention, plan format, voice routing, manifest schema, content-hash dedup contract, env vars, cost expectations.
11. **Add `"generate-audio"` to `_KIT_DISTRIBUTED_SKILLS`** in `foundry_app/services/asset_copier.py`. Keep alphabetical: `("_media_lib", "generate-audio", "generate-image", "generate-screen")`.
12. **Update ADR-011 (or ADR-009) registry list** to include `generate-audio`.
13. **Tests** at `tests/test_generate_audio.py`:
    - Block scanner: finds `> 🎙️` blocks; ignores other blockquotes; handles multi-line blocks.
    - Stripping: delegate-not-reimplement (assert `_media_lib.text.normalize_narration_text` is called; don't re-test it here).
    - Manifest writer: shape; stripped-text invariant.
    - Skip-on-disk modes: missing/regenerate-changed/force/dry-run/all.
    - Orphan cleanup: removes MP3s whose blocks no longer exist.
    - Voice map: rachel resolves to ID; unknown name passthrough; `--voice` overrides frontmatter.
    - Char-count cost report: matches expected total.
    - ElevenLabs SDK calls mocked end-to-end (don't actually hit the API in tests).

## Acceptance Criteria

- [ ] Skill at `.claude/shared/skills/generate-audio/` with `generate_audio.py` + `SKILL.md`.
- [ ] Walks source markdown, finds `> 🎙️` blocks, generates MP3 per block.
- [ ] Strips markdown markers via `_media_lib.text.normalize_narration_text` before sending.
- [ ] Writes per-source manifest with stripped text.
- [ ] Default voice `rachel`; `--voice` overrides; voice map handles names + raw IDs.
- [ ] Default model `eleven_multilingual_v2`; `--model` overrides.
- [ ] Skip-on-disk: missing → generate; `--force`, `--regenerate-changed`, `--dry-run`, `--all` all behave per spec.
- [ ] Orphan MP3s removed on manifest rewrite.
- [ ] End-of-run summary prints char-count = credits.
- [ ] `.env` discovery resolves `ELEVENLABS_API_KEY` via `_media_lib.env.load_env`.
- [ ] No cloned voice IDs in committed code.
- [ ] `generate-audio` added to `_KIT_DISTRIBUTED_SKILLS`.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Definition of Done

- Code committed on the feature branch.
- Tests pass; lint clean.
- SKILL.md complete.
- Commit message: `BEAN-283 task 02: generate-audio skill (ElevenLabs)`.
