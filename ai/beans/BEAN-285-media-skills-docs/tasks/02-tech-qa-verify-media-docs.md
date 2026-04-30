# Task 02: Verify BEAN-285 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Independently verify every BEAN-285 acceptance criterion. This is a
documentation bean, so verification is mostly grep-and-read: confirm
each section exists, says what it should, and references the right
source-of-truth. Run the test suite and lint as a regression check.

## Inputs

- `ai/beans/BEAN-285-media-skills-docs/bean.md`
- All files Developer touched in task 01 (read the commit diffs).
- Source-of-truth implementations (for cross-checking accuracy):
  - `.claude/shared/skills/generate-image/generate_image.py`
  - `.claude/shared/skills/generate-audio/generate_audio.py`
  - `foundry_app/services/asset_copier.py` (`_KIT_DISTRIBUTED_SKILLS`)
  - `foundry_app/services/scaffold.py` (`_render_readme`, `_render_media_plans`)

CONTEXT DIET: stay within these inputs.

## BEAN-285 Acceptance Criteria

1. Foundry CLAUDE.md "Media Skills" section.
2. `.claude/shared/CLAUDE.md` Available Skills + Kit-Distributed Skills.
3. Both SKILL.md files reflect implementation.
4. Foundry README mentions opt-in.
5. Generated-project README template includes media workflow guidance.
6. `decisions.md` ADR cross-references.
7. `project.md` module map updated.
8. MEMORY.md doc checklist updated.
9. `.env.example` lists all three keys.
10. Build-pipeline content-hash example exists.
11. Tests pass + lint clean.

## Verification Steps

1. **Foundry CLAUDE.md** — grep for "Media Skills" section; confirm three env vars and `.env` precedence are documented.
2. **`.claude/shared/CLAUDE.md`** — confirm `generate-image` and `generate-audio` rows; confirm "Kit-Distributed Skills" section names all four skills.
3. **`generate-image/SKILL.md`** — read; confirm coverage of plan-driven + single-shot, frontmatter keys, provider routing, `--quality` flag, sidecar JSON schema. Cross-check key names against `generate_image.py` parser.
4. **`generate-audio/SKILL.md`** — read; confirm inline-block convention, plan format, voice routing, manifest schema with **stripped text** invariant, content-hash dedup pointer.
5. **Foundry README.md** — grep for `include_media_skills`.
6. **Generated-project README template** — read `scaffold.py:_render_readme`; confirm conditional section added; render with the flag on (write a tmp test or just spot-check the code branch) and confirm the section appears.
7. **`decisions.md`** — confirm ADR cross-references; ADR-010 (image), ADR-011 (audio), kit-distributed skills ADR (from BEAN-280) all present.
8. **`project.md`** — grep for `_media_lib`, `generate-image`, `generate-audio` in module map.
9. **`MEMORY.md` checklist** — confirm new files listed.
10. **`.env.example`** — confirm three keys with comments.
11. **Build-pipeline example** — confirm `BUILD_EXAMPLE.md` (or in-SKILL.md section) exists and references `_media_lib.text.hash_text`.
12. **`uv run pytest`** — capture count; expect ≥ 2166 (no regression from BEAN-284's baseline).
13. **`uv run ruff check foundry_app/`** — expect clean.

## This Task's Acceptance Criteria

- [ ] Every BEAN-285 acceptance criterion verified.
- [ ] Verification report appended under `## Verification Report`: PASS/FAIL/NOTES per criterion.
- [ ] Pytest count + delta + lint result captured.
- [ ] Cross-checks against implementation source-of-truth done (no drift).
- [ ] Any gaps documented.

## Definition of Done

- Verification report written.
- Bean is ready for Team Lead to mark Done OR specific gaps documented.
- Commit message: `BEAN-285 task 02: tech-qa verification`.
