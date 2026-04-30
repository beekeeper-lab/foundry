# Task 01: Implement Media Plan Templates + Scaffolder Integration

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Add two Jinja2 plan templates under `ai-team-library/templates/media/`,
add a boolean opt-in flag to the composition spec, and have the
scaffolder render the templates to the generated project root when the
flag is `True`. Overlay-safe: existing user-edited plans are preserved.

## Inputs

- `ai/beans/BEAN-284-media-plan-templates/bean.md` — scope and acceptance criteria.
- `foundry_app/core/models.py` — `CompositionSpec`, `GenerationOptions`, related Pydantic models.
- `foundry_app/services/scaffold.py` — current scaffolder (look at how `_render_readme` and `_render_project_charter` are emitted at project root with overlay-safe semantics — copy that pattern for plan files).
- `ai-team-library/templates/shared/` — existing template dir layout (sibling of the new `media/` dir).
- `tests/test_scaffold.py` — existing scaffold tests to mirror for media.
- `.claude/shared/skills/generate-image/generate_image.py` lines around the IMAGE-PLAN frontmatter parser — confirm the keys the template emits match what the parser reads (`Style`, `Generator`, `Aspect ratio`, `Background`, `Text in image`, `Avoid`).
- `.claude/shared/skills/generate-audio/generate_audio.py` lines around the NARRATION-PLAN frontmatter parser — confirm `Voice`, `Model` keys.

CONTEXT DIET: stay within these inputs. Do not re-read large files
already cited in BEAN-282/283 (the audio/image skills are already
implemented; you are only verifying frontmatter key names).

## Acceptance Criteria

- [ ] `ai-team-library/templates/media/IMAGE-PLAN.md.j2` exists with documented frontmatter keys: `Style`, `Generator`, `Aspect ratio`, `Background`, `Text in image`, `Avoid`. Includes one commented-out example image entry. Title interpolates project name.
- [ ] `ai-team-library/templates/media/NARRATION-PLAN.md.j2` exists with documented frontmatter keys: `Voice`, `Model`. Includes a short explanation of the `> 🎙️` inline-block convention. Title interpolates project name.
- [ ] Default frontmatter values: `Aspect ratio: 16:9`, `Background: white`, `Text in image: minimal`, `Generator: gemini-3-pro-image-preview`, `Voice: rachel`, `Model: eleven_multilingual_v2`. Do **not** pre-fill `Style` — that is project-specific (plan-first discipline; see bean Notes).
- [ ] `CompositionSpec.include_media_skills: bool = False` added (Pydantic-validated, defaults to `False`).
- [ ] When the flag is `True`, the scaffolder renders both plan files at the generated project root.
- [ ] Files are not overwritten if they already exist (overlay-safe).
- [ ] Frontmatter title interpolates from `spec.project.name`.
- [ ] New tests in `tests/test_scaffold_media.py` (or extending `tests/test_scaffold.py`):
  - flag off → no plan files written
  - flag on → both files written with expected content
  - flag on + existing plan files → not overwritten
  - frontmatter title contains `spec.project.name`
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Definition of Done

- All acceptance criteria green.
- Commit message: `BEAN-284 task 01: media plan templates + scaffolder integration`.
