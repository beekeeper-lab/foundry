# Task 03: Verify BEAN-283 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01, 02 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Independently verify every BEAN-283 acceptance criterion. Run the
test suite and lint. Confirm the new generate-audio skill works:
inline-block scanning, manifest invariants, voice routing, orphan
cleanup, content-hash contract preserved. Confirm no cloned voice
IDs in committed code. Sign off or list specific gaps.

## Inputs

- `ai/beans/BEAN-283-generate-audio-skill/bean.md`
- `ai/context/decisions.md` — ADR-011 (audio skill design); confirm BEAN-283 coverage
- `.claude/shared/skills/generate-audio/generate_audio.py` — Developer's new skill
- `.claude/shared/skills/generate-audio/SKILL.md` — Developer's new doc
- `tests/test_generate_audio.py` — Developer's new tests
- `foundry_app/services/asset_copier.py` — verify `generate-audio` in `_KIT_DISTRIBUTED_SKILLS`
- `.claude/shared/skills/_media_lib/text.py` — confirm Developer uses `normalize_narration_text` (delegation, not reimplementation)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_narration.py` — reference; spot-check manifest shape, voice map structure

CONTEXT DIET: stay within these inputs.

## BEAN-283 Acceptance Criteria

1. Skill at `.claude/shared/skills/generate-audio/` with `generate_audio.py` + `SKILL.md`.
2. Walks source markdown, finds `> 🎙️` blocks, generates MP3 per block.
3. Strips markdown markers via `_media_lib.text.normalize_narration_text` before sending (delegation verified).
4. Writes per-source manifest with stripped text.
5. Default voice `rachel`; `--voice` overrides; voice map handles names + raw IDs.
6. Default model `eleven_multilingual_v2`; `--model` overrides.
7. Skip-on-disk: missing → generate; `--force`, `--regenerate-changed`, `--dry-run`, `--all` all behave per spec.
8. Orphan MP3s removed on manifest rewrite.
9. End-of-run summary prints char-count = credits.
10. `.env` discovery resolves `ELEVENLABS_API_KEY` via `_media_lib.env.load_env`.
11. **No cloned voice IDs in committed code.** (Critical — search the source for any `s6d7r1gfIA8ArVv5Vocl` or similar IDs.)
12. `generate-audio` added to `_KIT_DISTRIBUTED_SKILLS`.
13. All tests pass (`uv run pytest`).
14. Lint clean (`uv run ruff check foundry_app/`).

## Verification Steps

1. **ADR-011 review** — confirm structure and all six "Decision" commitments.
2. **Skill files present** — `ls .claude/shared/skills/generate-audio/`.
3. **Inline scanner** — read the block-finding code; confirm it matches `> 🎙️` blockquotes (handles multi-line; ignores plain blockquotes).
4. **Stripping delegation** — grep the source for `normalize_narration_text` import. Confirm Developer is using `_media_lib.text.normalize_narration_text`, not reimplementing the regexes.
5. **Manifest schema** — read the manifest writer; confirm `{index, module, audio_file, text, size_bytes}` shape and that `text` is the **stripped** text (not the raw blockquote).
6. **Voice map** — read it; confirm `rachel` → `21m00Tcm4TlvDq8ikWAM`, no cloned voice IDs.
7. **Cloned voice ID search** — `grep -r "s6d7r1gfIA8ArVv5Vocl" .claude/ tests/ ai/` should return no results in committed code (the user's cloned voice ID stays in their personal projects).
8. **Skip-on-disk modes** — read the dispatch logic; trace each mode's behavior.
9. **Orphan cleanup** — read the manifest-rewrite code; confirm MP3s missing from the new block list are removed.
10. **Cost report** — confirm char-count = credit-count is computed and printed at end-of-run.
11. **Run `uv run pytest`** — capture count and any failures. Report delta from prior baseline (2081).
12. **Run `uv run ruff check foundry_app/`** — must be clean.
13. **Run BEAN-283's specific tests**: `uv run pytest tests/test_generate_audio.py -v`.
14. **`_KIT_DISTRIBUTED_SKILLS`** — confirm `generate-audio` is in the registry.
15. **Commit message** — confirm `BEAN-283 task NN: ...` style.

## This Task's Acceptance Criteria

- [ ] Every BEAN-283 acceptance criterion verified.
- [ ] Verification report appended under `## Verification Report`: PASS/FAIL/NOTES per criterion.
- [ ] Pytest count + delta + lint result captured.
- [ ] Cloned voice ID search confirmed clean (zero results).
- [ ] Stripping delegation confirmed (uses `_media_lib`, not reimplemented).
- [ ] Manifest invariant confirmed (stripped text, not raw).
- [ ] Any gaps documented; not silently accepted.

## Definition of Done

- Verification report written.
- Bean is ready for Team Lead to mark Done OR specific gaps documented.
- Commit message: `BEAN-283 task 03: tech-qa verification`.
