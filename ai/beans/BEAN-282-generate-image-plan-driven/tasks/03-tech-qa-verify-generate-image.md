# Task 03: Verify BEAN-282 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01, 02 |
| **Status** | Done |
| **Started** | 2026-04-29 20:07 |
| **Completed** | 2026-04-29 20:09 |
| **Duration** | 2m |

## Goal

Independently verify every BEAN-282 acceptance criterion. Run the
test suite and lint. Confirm the rewritten generate-image works for
both plan-driven and single-shot modes. Confirm `generate-screen`
hasn't broken. Sign off or list specific gaps.

## Inputs

- `ai/beans/BEAN-282-generate-image-plan-driven/bean.md`
- `ai/context/decisions.md` — ADR-010 (verify it covers what BEAN-282 requires)
- `.claude/shared/skills/generate-image/generate_image.py` — Developer's rewrite
- `.claude/shared/skills/generate-image/SKILL.md` — Developer's rewritten doc
- `tests/test_generate_image.py` — Developer's new tests
- `.claude/shared/skills/generate-screen/SKILL.md` — verify the caller still works
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_images.py` — reference; spot-check rate-limiter constant and 429 retry behavior match

CONTEXT DIET: stay within these inputs.

## BEAN-282 Acceptance Criteria

1. `--plan IMAGE-PLAN.md` mode generates only missing images, skipping existing ones.
2. `--prompt "..."` mode generates one image (single-shot path).
3. `Generator:` frontmatter routes Gemini vs OpenAI correctly, including the regex-tolerant dispatch.
4. Default OpenAI model is `gpt-image-2`; falls back to `gpt-image-1.5` on org-verification error with a warning.
5. `--quality` flag behaves per the mapping table; default is `high`.
6. Sidecar JSON contains every documented field for each successful generation.
7. Gemini rate limiter caps at ~18 req/min; honors `retryDelay` on 429.
8. `--filter`, `--force`, `--dry-run` behave as documented.
9. End-of-run summary prints provider, count, and estimated cost.
10. `.env` discovery walks cwd → parents → `$HOME`.
11. `generate-screen` smoke test still works (single-shot mode unbroken).
12. All tests pass (`uv run pytest`).
13. Lint clean (`uv run ruff check foundry_app/`).

## Verification Steps

1. **ADR-010 review** — read it; confirm it covers all six "Decision" commitments and the alternatives section.
2. **Read the generator** — trace the dispatch regex and quality mapping manually. Confirm Stonewaters' `MIN_INTERVAL_SECONDS = 60.0/18` is preserved (not 60.0/20 or anything close).
3. **Read the new tests** — confirm they cover frontmatter parsing, plan parsing, provider dispatch (with the tolerant containment check), skip-on-disk, --filter, --force, --dry-run, quality mapping, OpenAI fallback (mocked), rate limiter (mocked clock), and cost summary.
4. **Run `uv run pytest`** — capture count and any failures. Report delta from prior baseline (2016).
5. **Run `uv run ruff check foundry_app/`** — must be clean.
6. **Run BEAN-282's specific tests**: `uv run pytest tests/test_generate_image.py -v` — confirm all pass and count assertions per criterion.
7. **`generate-screen` smoke check** — read its SKILL.md to identify how it invokes generate-image. If the call shape changed, confirm generate-screen was updated in lockstep.
8. **`--dry-run` walk-through** — read `generate_image.py`'s plan-mode entry point; confirm `--dry-run` short-circuits before any HTTP call (or that the test for this behavior is meaningful).
9. **Sidecar schema** — read the sidecar-writer code; confirm every field listed in the bean's spec is present.
10. **Cost table** — confirm `_COST_TABLE` (or equivalent) is in the script with current rates. End-of-run summary uses it.
11. **Commit message** — confirm `BEAN-282 task NN: ...` style.

## This Task's Acceptance Criteria

- [ ] Every BEAN-282 acceptance criterion verified.
- [ ] Verification report appended under `## Verification Report`: PASS/FAIL/NOTES per criterion.
- [ ] Pytest count + delta + lint result captured.
- [ ] `generate-screen` smoke-tested (or impossible-to-test reason documented).
- [ ] OpenAI fallback path verified via the mocked test specifically (not just by inspection).
- [ ] Rate-limiter constant matches Stonewaters reference exactly.
- [ ] Any gaps documented; not silently accepted.

## Definition of Done

- Verification report written.
- Bean is ready for Team Lead to mark Done OR specific gaps documented.
- Commit message: `BEAN-282 task 03: tech-qa verification`.

## Verification Report

**Verdict: PASS — 13/13 acceptance criteria met. Sign-off granted.**

### Test & Lint Evidence

| Check | Result |
|---|---|
| `uv run pytest` — full suite | **2081 passed, 0 failed** (4 unrelated PySide6 deprecation warnings) |
| Pytest delta from baseline 2016 | **+65** — matches the 65 BEAN-282 tests added in `tests/test_generate_image.py` |
| `uv run pytest tests/test_generate_image.py -v` | **65 passed in 0.10s** |
| `uv run ruff check foundry_app/` | **All checks passed!** |

### Per-criterion verification

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | `--plan` mode skips existing files | PASS | `TestPlanLoop::test_skip_on_disk` — pre-existing PNG (`img-01.png` content `b"already-there"`) is left untouched while `img-02.png` is generated and gets a sidecar. `run_plan` line 844: `if file_path.exists() and not args.force: skipped += 1; continue`. |
| 2 | `--prompt` single-shot mode | PASS | `TestSingleShotMode::test_single_shot_produces_image_and_sidecar` — generates `hero-01.png` + sidecar with `assembled_prompt` + `aspect_ratio` populated. `test_single_shot_count_generates_multiple` covers `--count 3`. |
| 3 | `Generator:` tolerant dispatch | PASS | `TestProviderDispatch::test_openai_dispatch_is_tolerant` parametrized over 7 inputs covering all dispatch cases requested: empty (→ Gemini default, separate test `test_default_routes_to_gemini_with_pro_model`), `gemini-3-pro-image-preview` (→ Gemini), `nanobanana-pro` (→ Gemini), `Imagen 4` (→ Gemini), `openai-gpt-image-1.5` / `openai-gpt-image-2` / `gpt-image-1.5` / `gpt-image-2` / `OpenAI gpt-image-2` / `GPT-IMAGE-2` / bare `openai` (→ OpenAI). Regex extraction tested separately in `test_openai_model_extracted_via_regex`. |
| 4 | OpenAI default `gpt-image-2`; auto-fallback to `gpt-image-1.5` on org-verification error with warning + sidecar `fallback_used: true` | PASS | `DEFAULT_OPENAI_MODEL = "gpt-image-2"` (line 120). `TestOpenAIFallback::test_org_verification_error_falls_back_to_1_5` calls `_generate_openai` with `model: gpt-image-2`, simulates `"Your organization must be verified..."` error, asserts `calls == ["gpt-image-2", "gpt-image-1.5"]`, `meta["fallback_used"] is True`, `meta["model"] == "gpt-image-1.5"`. Warning line printed to stderr (line 593, `file=sys.stderr`). `test_no_fallback_when_starting_with_1_5` and `test_billing_hard_limit_fails_fast` cover the negative cases. |
| 5 | `--quality low/medium/high` mapping per ADR-010; default `high` | PASS | `TestQualityMapping` parametrized: OpenAI passthrough (`low→low`, `medium→medium`, `high→high`); Gemini collapse (`low→nanobanana2/flash`, `medium→nanobanana2/flash`, `high→nanobanana-pro/pro`). `DEFAULT_QUALITY = "high"` (line 146). `TestCLI::test_parser_default_quality_is_high` confirms `--quality` defaults to `high`. `TestProviderDispatch::test_frontmatter_quality_overrides_cli_default` confirms the precedence rule. |
| 6 | Sidecar JSON has every required field | PASS | `TestSidecarShape::test_gemini_sidecar_required_fields` asserts presence of all 12 ADR-010 required fields: `timestamp`, `provider`, `model`, `assembled_prompt`, `output_file`, `generation_time_ms`, `usage`, `fallback_used`, `aspect_ratio`, `background`, `text_in_image`, `negative_constraints`. `test_openai_sidecar_includes_quality_and_size` covers OpenAI-only `quality`/`size`. `negative_constraints` parsed from `Avoid:` correctly. |
| 7 | Gemini rate limiter caps ~18 req/min; honors `retryDelay` on 429 | PASS | `MIN_INTERVAL_SECONDS = 60.0 / 18` literal at line 126 — **exact match** with Stonewaters reference (`/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_images.py` line 46). `TestRateLimiter::test_min_interval_constant_is_60_over_18` is a guard test asserting equality. `test_plan_loop_sleeps_between_gemini_calls` mocks `time.sleep`/`time.time` and confirms a sleep ≤ `MIN_INTERVAL_SECONDS+0.01s` is recorded between iterations. `test_extract_retry_delay_from_gemini_429_body` confirms `retryDelay: '5s'` → 7s with jitter. `MAX_RETRIES_ON_429 = 3` (line 127). |
| 8 | `--filter`, `--force`, `--dry-run` behave as documented | PASS | `TestPlanLoop::test_filter_substring` (only `img-02.png` generated when `--filter img-02`); `test_force_regenerates_existing` (existing file overwritten); `test_dry_run_makes_no_api_calls` (mock `generate_image` never called, "WOULD GENERATE" printed). `--dry-run` short-circuit verified at line 855 — runs before API key load and before any provider call. |
| 9 | End-of-run summary prints provider + count + estimated cost | PASS | `TestEndOfRunSummaryPrinted::test_summary_prints_in_plan_loop` asserts `"Generated: 1"`, `"gemini"`, `"Estimated cost:"` all appear. `format_run_summary` (lines 737–755) emits provider, model, count, and `Estimated cost: ${total_cost_usd:.2f}`. `_COST_TABLE` (lines 157–178) populated for all 18 OpenAI (model, quality, size) combos; `_GEMINI_USD_PER_TOKEN = 0.00007` for Gemini. `TestCostSummary::test_openai_cost_lookup` and `test_gemini_cost_from_tokens` exercise both paths. |
| 10 | `.env` discovery via `_media_lib.env.load_env` | PASS | Line 103 imports `from _media_lib.env import load_env`. Line 1129 in `main()` calls `load_env()` before dispatch. `TestEnvDiscovery::test_load_env_is_imported_from_media_lib` confirms `gi.load_env.__module__` ends with `_media_lib.env`. `test_main_loads_env_then_dispatches` confirms `main()` runs `load_env()` and then dispatches. The walk semantics (cwd → parents → `$HOME`) live in BEAN-281's `_media_lib`. |
| 11 | `generate-screen` smoke test still works | PASS | `generate-screen/SKILL.md` lines 290–299 invoke `generate_image.py` with `--prompt`, `--style`, `--aspect-ratio`, `--output-dir`, `--asset-name`. All five flags preserved in `build_parser` (lines 1076, 1099, 1101, 1114, 1116). Single-shot mode prints JSON to **stdout** (line 1040) — required for generate-screen's parser. Cost summary goes to **stderr** (line 1057) — keeps stdout JSON-clean. `TestSingleShotMode` exercises the exact single-shot path generate-screen uses. |
| 12 | All tests pass | PASS | 2081/2081 in 15.07s. |
| 13 | Lint clean | PASS | `All checks passed!` |

### Critical verification spot-checks

- **Rate-limiter constant** — line 126: `MIN_INTERVAL_SECONDS = 60.0 / 18`. Verbatim match with Stonewaters reference line 46. Test `test_min_interval_constant_is_60_over_18` is a guard that pins this against silent drift. **VERIFIED.**
- **OpenAI fallback path** — `test_org_verification_error_falls_back_to_1_5` exercises the full chain: simulated "Your organization must be verified" error → second call uses `gpt-image-1.5` → returned dict has `fallback_used=True` and `model=gpt-image-1.5`. Sidecar built from this dict propagates `fallback_used: true` (covered by `TestSidecarShape::test_openai_sidecar_includes_quality_and_size` with `fallback_used=True`). **VERIFIED.**
- **Tolerant dispatch coverage** — All 6 cases requested are tested: empty (→ Gemini default, separate `test_default_routes_to_gemini_with_pro_model`), `gemini-...` (→ Gemini, `test_non_openai_dispatch_routes_to_gemini[gemini-3-pro-image-preview]`), `openai-...` (→ OpenAI, `test_openai_dispatch_is_tolerant[openai-gpt-image-1.5]`), `gpt-image-1.5` (→ OpenAI), `gpt-image-2` (→ OpenAI), and `nanobanana-pro` (→ Gemini, `test_non_openai_dispatch_routes_to_gemini[nanobanana-pro]`). Plus mixed-case `OpenAI gpt-image-2`, `GPT-IMAGE-2`, and bare `openai`. **VERIFIED.**
- **Single-shot CLI shape preserved** — `--prompt`, `--style`, `--aspect-ratio`, `--output-dir`, `--asset-name` all defined in `build_parser`. `TestCLI::test_parser_accepts_single_shot_flags` asserts each parses correctly. **VERIFIED.**
- **Cost summary stdout vs stderr** — Plan mode: `format_run_summary(...)` is wrapped in a bare `print(...)` call (lines 905–917) → stdout. Single-shot mode: prints JSON to stdout (line 1040), then prints `format_run_summary(...)` with `file=sys.stderr` (lines 1045–1058). The split is intentional — generate-screen parses stdout JSON and ignores stderr. **VERIFIED.**

### ADR-010 coverage

ADR-010 covers all six "Decision" commitments (modes, dispatch, OpenAI default+fallback, unified quality, rate limiter, sidecar fields), plus the cost-table location rule, the one-provider-per-project rule, the failover use case, three Alternatives Considered (per-image override, quality-as-provider-selector, OpenAI-off-until-verified), and Consequences (positive + negative). Full alignment with what BEAN-282 requires. No ADR gaps.

### Gaps

None. All 13 acceptance criteria verified with concrete evidence. Sign-off granted.
