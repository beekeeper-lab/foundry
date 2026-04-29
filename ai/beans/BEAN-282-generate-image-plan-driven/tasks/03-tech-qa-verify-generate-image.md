# Task 03: Verify BEAN-282 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01, 02 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

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
