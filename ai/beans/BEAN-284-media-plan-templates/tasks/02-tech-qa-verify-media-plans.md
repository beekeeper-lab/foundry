# Task 02: Verify BEAN-284 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-04-29 21:41 |
| **Completed** | 2026-04-29 21:42 |
| **Duration** | 1m |

## Goal

Independently verify every BEAN-284 acceptance criterion. Run the
test suite and lint. Confirm the templates carry the right
frontmatter keys (matching what BEAN-282/283 parsers actually read),
the spec field defaults to `False`, the scaffolder is overlay-safe,
and project name interpolation works. Sign off or list specific gaps.

## Inputs

- `ai/beans/BEAN-284-media-plan-templates/bean.md`
- `ai-team-library/templates/media/IMAGE-PLAN.md.j2` — Developer's output.
- `ai-team-library/templates/media/NARRATION-PLAN.md.j2` — Developer's output.
- `foundry_app/core/models.py` — confirm `include_media_skills` field exists, defaults to `False`, is Pydantic-validated.
- `foundry_app/services/scaffold.py` — confirm conditional emission + overlay-safety.
- `tests/test_scaffold_media.py` (or scaffold test file extended) — confirm coverage of all 4 test cases.
- `.claude/shared/skills/generate-image/generate_image.py` — frontmatter key names for cross-check.
- `.claude/shared/skills/generate-audio/generate_audio.py` — frontmatter key names for cross-check.

CONTEXT DIET: stay within these inputs.

## BEAN-284 Acceptance Criteria

1. `templates/media/IMAGE-PLAN.md.j2` with documented keys.
2. `templates/media/NARRATION-PLAN.md.j2` with documented keys.
3. `CompositionSpec.include_media_skills: bool = False`.
4. Scaffolder writes both plans when flag is `True`.
5. Files not overwritten when present.
6. Frontmatter interpolates project name.
7. All tests pass.
8. Lint clean.

## Verification Steps

1. **Templates present** — `ls ai-team-library/templates/media/`.
2. **Frontmatter shape** — read each `.j2`. Confirm key names match what BEAN-282/283 parsers read (`Style`, `Generator`, `Aspect ratio`, `Background`, `Text in image`, `Avoid` for image; `Voice`, `Model` for narration). Confirm defaults match the bean's Notes (`16:9`, `white`, `minimal`, `gemini-3-pro-image-preview`, `rachel`, `eleven_multilingual_v2`). Confirm `Style` is **not** pre-filled.
3. **Spec field** — grep `models.py` for `include_media_skills`. Confirm `bool = False` default, on `CompositionSpec` (or wherever Developer placed it — verify the placement is reasonable and consistent with sibling fields).
4. **Scaffolder change** — read the new emission code. Confirm overlay-safety (don't overwrite existing plan files) using the same pattern as `_render_readme` / `_render_project_charter`.
5. **Project name interpolation** — render a template with a known spec and verify the project name appears in the title.
6. **Tests** — read the new test file. Confirm all 4 cases (flag off, flag on, flag on + existing files, interpolation) are present and assert the right things.
7. **Run `uv run pytest`** — capture count and any failures. Report delta from prior baseline (2150).
8. **Run `uv run ruff check foundry_app/`** — must be clean.
9. **Run targeted tests**: `uv run pytest tests/test_scaffold_media.py -v` (or whichever file holds the new tests).
10. **Commit message** — confirm `BEAN-284 task NN: ...` style.

## This Task's Acceptance Criteria

- [ ] Every BEAN-284 acceptance criterion verified.
- [ ] Verification report appended under `## Verification Report`: PASS/FAIL/NOTES per criterion.
- [ ] Pytest count + delta + lint result captured.
- [ ] Frontmatter keys cross-checked against parsers (no drift).
- [ ] Overlay-safety confirmed (existing plan files preserved).
- [ ] Any gaps documented; not silently accepted.

## Definition of Done

- Verification report written.
- Bean is ready for Team Lead to mark Done OR specific gaps documented.
- Commit message: `BEAN-284 task 02: tech-qa verification`.

## Verification Report

**Verdict: 8/8 PASS — ship it.**

### Evidence

- **pytest:** `uv run pytest --quiet` → `2166 passed, 4 warnings in 10.61s`. Delta from prior baseline of 2150: **+16** (matches the new `tests/test_scaffold_media.py` count).
- **lint:** `uv run ruff check foundry_app/ tests/test_scaffold_media.py` → `All checks passed!`
- **targeted:** `uv run pytest tests/test_scaffold_media.py -v` → 16/16 passed in 0.11s.
- **frontmatter cross-check (image):** `generate_image.py` parser at lines 193–200 reads `Style`, `Aspect ratio`, `Background`, `Text in image`, `Avoid`, `Generator` (all bold-prefixed `**Key:**`). `IMAGE-PLAN.md.j2` emits all six with the correct bold-prefixed shape. No drift.
- **frontmatter cross-check (audio):** `generate_audio.py` `parse_plan_frontmatter` at line 179 reads `**Voice:**` and `**Model:**`. `NARRATION-PLAN.md.j2` emits both with the bold-prefixed shape. No drift.

### BEAN-284 acceptance criteria — per-criterion verdict

| # | Criterion | Verdict | Notes |
|---|---|---|---|
| 1 | `templates/media/IMAGE-PLAN.md.j2` with documented keys | **PASS** | All six keys present (`Style`, `Generator`, `Aspect ratio`, `Background`, `Text in image`, `Avoid`). Defaults match bean Notes (`16:9`, `white`, `minimal`, `gemini-3-pro-image-preview`). `Style` is **not** pre-filled (intentional — plan-first discipline). One commented-out example entry inside `<!-- -->`. |
| 2 | `templates/media/NARRATION-PLAN.md.j2` with documented keys | **PASS** | `Voice: rachel`, `Model: eleven_multilingual_v2`. Includes the `> 🎙️` inline-block convention explanation. |
| 3 | `CompositionSpec.include_media_skills: bool = False` | **PASS (with placement note)** | Field added at `models.py:385` on `GenerationOptions` (accessed as `spec.generation.include_media_skills`), not directly on `CompositionSpec`. This is consistent with sibling toggles (`seed_tasks`, `write_manifest`, `write_diff_report`, `claude_kit_url`) and matches Foundry conventions. Default is `False` and Pydantic-validated. |
| 4 | Scaffolder writes both plan files when flag is `True` | **PASS** | `scaffold.py` adds `_render_media_plans()` (line 174) called from `scaffold_project` (line 319) when `spec.generation.include_media_skills` is True. `generator.py:183` passes `library_root` so the templates can be located. |
| 5 | Files not overwritten when present | **PASS** | `_render_media_plans` skips `dest` if `dest.exists()` (line 199 area). Confirmed by `TestOverlaySafety::test_existing_image_plan_preserved` and `test_existing_narration_plan_preserved`. |
| 6 | Frontmatter interpolated with project-spec values (title at minimum) | **PASS** | Templates use `{{ project_name }}`. Context passed in `_render_media_plans` is `{"project_name": spec.project.name}`. Confirmed by `TestProjectNameInterpolation` (both files). |
| 7 | All tests pass (`uv run pytest`) | **PASS** | 2166 passed, 0 failed. |
| 8 | Lint clean (`uv run ruff check foundry_app/`) | **PASS** | All checks passed! |

### Spot-check findings

- **Library root signature change:** `scaffold_project` gained an optional `library_root: str | Path | None = None` parameter. All ~30 existing callers in `tests/test_scaffold.py` continue to work (they pass only `spec` + `output_dir`), confirmed by the green full suite. When the flag is True but `library_root` is `None`, the scaffolder warns and skips — covered by `TestLibraryRootMissing`.
- **Generator wiring:** `generator.py:183` was updated to pass `library_root` to the scaffold stage. No other callers of `scaffold_project` in production code.
- **Overlay safety identical to README/charter pattern:** `_render_media_plans` follows the exact `if dest.exists(): skip` pattern used by `_render_readme` (scaffold.py:251-255) and `_render_project_charter` (scaffold.py:259-263).

### Sign-off

All 8 BEAN-284 acceptance criteria PASS. The placement of `include_media_skills` on `GenerationOptions` rather than directly on `CompositionSpec` is the only deviation from the bean wording — flagged for Team Lead but recommended as the cleaner choice (consistent with existing toggles). Bean ready for Team Lead to mark Done.
