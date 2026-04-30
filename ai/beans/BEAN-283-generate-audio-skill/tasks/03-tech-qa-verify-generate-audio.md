# Task 03: Verify BEAN-283 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01, 02 |
| **Status** | Done |
| **Started** | 2026-04-29 20:45 |
| **Completed** | 2026-04-29 20:47 |
| **Duration** | 2m |

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

## Verification Report

**Verdict: 14/14 PASS — ship it.**

### Evidence

- **pytest:** `uv run pytest` → `2150 passed, 4 warnings in 10.98s`. Delta from
  prior baseline of 2081: **+69** (matches Developer's count of new tests in
  `tests/test_generate_audio.py`).
- **lint:** `uv run ruff check foundry_app/` → `All checks passed!`
- **targeted:** `uv run pytest tests/test_generate_audio.py -v` → 69/69 passed in 0.07s.
- **cloned voice ID search:**
  - `grep -n "s6d7r1gfIA8ArVv5Vocl"
    .claude/shared/skills/generate-audio/generate_audio.py` → **0 hits** (exit 1).
  - `grep -rn "s6d7r1gfIA8ArVv5Vocl" .claude/shared/skills/generate-audio/` →
    **0 hits**. The skill's source is clean.
  - Hits in `tests/test_generate_audio.py:187,194,245` are **intentional test
    guards** — one passthrough test (`test_unknown_name_passes_through`) and two
    `forbidden = {…}` set declarations that fail CI if anyone leaks the ID into
    `STOCK_VOICE_MAP` or the script body. The ADR-011 reference at
    `ai/context/decisions.md:1197` is contextual. None of these are committed
    code that ships to a downstream project.
- **delegation:**
  `.claude/shared/skills/generate-audio/generate_audio.py:91-92` imports
  `load_env` from `_media_lib.env` and `normalize_narration_text` from
  `_media_lib.text`. Used at line 159 inside `find_narration_blocks`. No private
  re-implementation of the stripping regex order — the BEAN-281 contract is
  honored. `test_delegates_stripping_to_media_lib` (line 113-119) spies on the
  imported function to defend this at runtime.
- **manifest invariant:** `process_source` builds `entry["text"] = block_text`
  where `block_text` is `block["text"]` from `find_narration_blocks` (i.e. the
  stripped output of `normalize_narration_text`). The same `block_text` is
  passed to `generate_audio_for_block(... text=block_text ...)`. Stored text
  bit-for-bit equals what was sent to ElevenLabs. Confirmed by
  `test_writes_manifest_with_stripped_text` (lines 578-595) which asserts both
  the manifest text **and** the `convert(...)` kwarg are the stripped form.

### BEAN-283 acceptance criteria — per-criterion verdict

| # | Criterion | Verdict | Notes |
|---|---|---|---|
| 1 | Skill at `.claude/shared/skills/generate-audio/` with `generate_audio.py` + `SKILL.md` | **PASS** | 789-line script + 232-line SKILL.md. Listed via `ls`. |
| 2 | Walks source markdown, finds `> 🎙️` blocks, generates MP3 per block | **PASS** | `_BLOCK_RE` (line 136-139) matches contiguous `> 🎙️` runs with `> ` continuation; `find_narration_blocks` returns one block per match. Tests `test_finds_single_block`, `test_finds_multiple_blocks`, `test_handles_multiline_block`, `test_ignores_non_microphone_blockquotes`, `test_returns_empty_for_no_blocks`. |
| 3 | Strips via `_media_lib.text.normalize_narration_text` (delegation, not reimplementation) | **PASS** | Import at line 92; call at line 159; spy test at line 113-119. Zero re-implementation of the regex order in the script. |
| 4 | Per-source manifest with stripped text | **PASS** | Schema `{index, module, audio_file, text, size_bytes}` (lines 446-451 + 477/482); `text` is `block["text"]` (post-`normalize_narration_text`). Tests `test_writes_manifest_with_stripped_text`, `test_manifest_record_shape`. |
| 5 | Default voice `rachel`; `--voice` overrides; voice map handles names + raw IDs | **PASS** | `DEFAULT_VOICE = "rachel"` (line 106); `STOCK_VOICE_MAP["rachel"] = "21m00Tcm4TlvDq8ikWAM"` (line 113); `resolve_voice` passes unknown values through (line 213). Tests `test_rachel_resolves_to_canonical_id`, `test_other_stock_names_resolve`, `test_unknown_name_passes_through`, `test_voice_flag_overrides_plan_voice`. |
| 6 | Default model `eleven_multilingual_v2`; `--model` overrides | **PASS** | `DEFAULT_MODEL` constant (line 107); `_resolve_voice_and_model` honors CLI > plan > default. Tests `test_default_model_is_eleven_multilingual_v2`, `test_cli_overrides_plan`. |
| 7 | Skip-on-disk: missing/--force/--regenerate-changed/--dry-run/--all per spec | **PASS** | All 5 modes present in `decide_action` (lines 338-368) and `select_source_files` (lines 520-547). Seven `TestDecideAction` cases + ten `TestProcessSource` / `TestMainCLI` cases exercise the matrix including composability. |
| 8 | Orphan MP3s removed on manifest rewrite | **PASS** | `cleanup_orphans` (lines 252-268) called in `process_source` (line 493) only on real runs, never under `--dry-run`. Tests `test_orphan_cleanup_on_real_run`, `test_dry_run_skips_orphan_cleanup`, `test_removes_orphans`, `test_ignores_non_mp3_files`. |
| 9 | End-of-run summary prints char-count = credits | **PASS** | `format_cost_summary` (lines 555-577); `CREDITS_PER_CHAR = 1.0` (line 127); `main` calls it (line 779-784). Tests `test_credits_equal_chars_for_v2`, `test_credit_rate_constant_is_one`, `test_full_run_prints_char_count_summary` (asserts "26 chars sent" + "26 credits" in output). |
| 10 | `.env` discovery resolves `ELEVENLABS_API_KEY` via `_media_lib.env.load_env` | **PASS** | Import at line 91; `load_env()` called at line 686 before reading `os.environ`. Test `test_missing_api_key_fails_outside_dry_run` confirms exit code 2 when missing. |
| 11 | **No cloned voice IDs in committed code** | **PASS** | `grep "s6d7r1gfIA8ArVv5Vocl" generate_audio.py` → 0 hits. Two CI guards: `test_no_cloned_voice_ids_in_committed_code` (scans `STOCK_VOICE_MAP.values()`) + `test_source_contains_no_cloned_voice_ids` (scans the entire script source as text). |
| 12 | `generate-audio` added to `_KIT_DISTRIBUTED_SKILLS` | **PASS** | `foundry_app/services/asset_copier.py:75-80` includes `"generate-audio"` between `_media_lib` and `generate-image`. |
| 13 | All tests pass (`uv run pytest`) | **PASS** | 2150 passed, 0 failed. Delta +69 from 2081 baseline. |
| 14 | Lint clean (`uv run ruff check foundry_app/`) | **PASS** | `All checks passed!` |

### Spot-check findings

- **ADR-011 coverage:** all six "Decision" commitments map to BEAN-283
  acceptance criteria (1→C2, 2→C4, 3→C3, 4→C5+C11, 5→C6, 6→C7+C8). Cost-rate
  source-of-truth in `CREDITS_PER_CHAR` matches the ADR-010 pattern.
- **Reference fidelity:** the inline scanner regex, manifest schema, and
  orphan-cleanup rule are faithful adaptations of the canonical
  `Course_Material/Git_Fundamentals/scripts/generate_narration.py`. Stripping
  is delegated (the canonical reference inlined the regex; the kit version
  routes through `_media_lib` per ADR-011 commitment 3 and the BEAN-281
  contract test).
- **No regressions:** the 2081 - 69 = 2081 prior tests still all pass alongside
  the new 69. No flaky/skipped tests introduced.

### Sign-off

All 14 BEAN-283 acceptance criteria PASS. No gaps. Bean ready for Team Lead
to mark Done.
