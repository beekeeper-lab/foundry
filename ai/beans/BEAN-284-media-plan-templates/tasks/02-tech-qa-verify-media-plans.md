# Task 02: Verify BEAN-284 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

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
