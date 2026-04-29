# Task 03: Verify BEAN-280 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01, 02 |
| **Status** | Done |
| **Started** | 2026-04-29 18:42 |
| **Completed** | 2026-04-29 18:43 |
| **Duration** | 1m |

## Goal

Independently verify every acceptance criterion in
`BEAN-280/bean.md`. Run the full test suite and lint. Confirm that a
library-copy-mode generated project actually receives the
kit-distributed skills end-to-end. Sign off on the bean or list
specific gaps.

## Inputs

- `ai/beans/BEAN-280-claudekit-canonical-skills-distribution/bean.md` — acceptance criteria to verify
- `ai/context/decisions.md` — verify the ADR from Task 01 covers everything the criteria require
- `foundry_app/services/asset_copier.py` — verify `_KIT_DISTRIBUTED_SKILLS` constant + `claude_kit_root` parameter exist
- `foundry_app/services/generator.py` — verify the parameter is wired through
- `tests/services/` — locate and run BEAN-280's new tests
- The bean's acceptance criteria checklist (transcribed below for ease)

## Acceptance Criteria (from BEAN-280)

1. ADR added to `ai/context/decisions.md` with the canonical-source rationale and the kit-distributed skill registry.
2. `_KIT_DISTRIBUTED_SKILLS` constant defined in `asset_copier.py`.
3. `copy_assets` accepts `claude_kit_root` parameter; sensible default.
4. In library-copy mode, kit-distributed skills resolve from `claude_kit_root/skills/<name>/`.
5. In subtree mode, kit-distributed skills are not double-copied.
6. Generated project (library-copy mode) ships with `.claude/skills/generate-image/` and `.claude/skills/generate-screen/`.
7. Tests cover both modes.
8. All tests pass (`uv run pytest`).
9. Lint clean (`uv run ruff check foundry_app/`).

## Verification Steps

1. **Read the ADR** — confirm presence, structure, kit-distributed registry, resolution rules, alternatives-rejected section.
2. **Read `asset_copier.py`** — confirm `_KIT_DISTRIBUTED_SKILLS` constant, `claude_kit_root` parameter, and the resolution branch in `copy_assets()`. Trace one path through manually for each mode.
3. **Read `generator.py`** — confirm the parameter is passed through.
4. **Run `uv run pytest`** — capture the count and any failures. All tests must pass.
5. **Run `uv run ruff check foundry_app/`** — must be clean.
6. **Run the BEAN-280 test set specifically** (`uv run pytest tests/services/test_asset_copier_kit_distribution.py -v` or wherever the new tests landed) — confirm both library-copy and subtree mode are exercised.
7. **End-to-end spot-check** — if the test suite includes an end-to-end test that produces a fake generated project, verify the output tree has `.claude/skills/generate-image/` and `.claude/skills/generate-screen/`. If no such test exists yet, write a small manual test or flag it as a gap.
8. **Cross-reference** — confirm the Developer's commit message follows convention (`BEAN-280 task 02: ...`) and the Architect's ADR commit follows convention (`BEAN-280 task 01: ...`).

## Acceptance Criteria (this task's own)

- [ ] Every BEAN-280 acceptance criterion verified individually.
- [ ] `uv run pytest` exit code 0; full count reported.
- [ ] `uv run ruff check foundry_app/` exit code 0.
- [ ] Verification report appended to this task file under a `## Verification Report` section: one line per BEAN criterion (PASS/FAIL/NOTES).
- [ ] Any gaps or follow-ups recorded as comments — not silently accepted.

## Definition of Done

- Verification report written.
- Bean is ready to be marked Done by the Team Lead, or specific gaps are documented.
- Commit message: `BEAN-280 task 03: tech-qa verification`.

## Verification Report

**Test suite:** `uv run pytest` — **1984 passed, 0 failed, 4 warnings** in 11.01s. Matches the expected count exactly. Delta from prior run (1984 expected): 0.

**Lint:** `uv run ruff check foundry_app/` — **All checks passed.**

**BEAN-280 specific test file:** `uv run pytest tests/test_asset_copier_kit_distribution.py -v` — **12/12 passed.** Coverage: constant shape (2), library-copy mode (5 — including kit resolution, content match, non-kit skill regression, missing-from-kit warning, and registry-overrides-library collision), subtree mode (1), default claude_kit_root resolution (2 — including a real-submodule end-to-end check), end-to-end output spot-checks for `generate-image` (1) and `generate-screen` (1).

### Per-criterion verdicts

| # | Criterion | Verdict | Notes |
|---|-----------|---------|-------|
| 1 | ADR added to `ai/context/decisions.md` with canonical-source rationale and kit-distributed registry | **PASS** | ADR-009 present (lines 504–801): full Context, Decision (6 sub-sections incl. ownership boundary, registry, resolution rules, generator wiring, library cross-reference), Consequences, 5 Alternatives Rejected, Reversibility. Registry listed verbatim. |
| 2 | `_KIT_DISTRIBUTED_SKILLS` constant defined in `asset_copier.py` | **PASS** | Defined as `tuple[str, ...]` at lines 69–72: `("generate-image", "generate-screen")`. Documented inline with ownership criteria pointer to ADR-009. |
| 3 | `copy_assets` accepts `claude_kit_root` parameter; sensible default | **PASS** | `claude_kit_root: str \| Path \| None = None` at line 91. `_default_claude_kit_root()` resolves to `<foundry_root>/.claude/shared/` via `Path(__file__).resolve().parents[2]`. Verified end-to-end by `test_default_claude_kit_root_resolves_to_bundled_submodule` and `test_copy_assets_uses_default_kit_when_param_omitted`. |
| 4 | Library-copy mode: kit-distributed skills resolve from `claude_kit_root/skills/<name>/` | **PASS** | `_copy_skills` (lines 296–394) constructs `kit_skill_path = kit_skills_root / skill_id` and registers it in `sources` for every name in the registry. Verified by `test_kit_distributed_skill_resolves_from_claude_kit_in_library_copy_mode` and `test_kit_distributed_skill_content_matches_kit_source`. Registry-overrides-library collision handled by skipping library copy at lines 343–350 and verified by `test_registry_overrides_library_when_skill_name_collides`. |
| 5 | Subtree mode: kit-distributed skills not double-copied | **PASS** | Subtree branch at `asset_copier.py:142` skips `_copy_skills` entirely. Verified by `test_kit_distributed_skill_skipped_in_subtree_mode` (asserts `.claude/skills/` directory does not exist and no "missing from kit" warning is emitted because the registry isn't consulted). |
| 6 | Generated project (library-copy mode) ships with `.claude/skills/generate-image/` and `.claude/skills/generate-screen/` | **PASS** | Bundled `<foundry_root>/.claude/shared/skills/generate-image/` exists with `SKILL.md` + `generate_image.py`; `generate-screen/` exists with `SKILL.md`. End-to-end: `test_generated_project_has_generate_image_in_library_copy_mode`, `test_generated_project_has_generate_screen_in_library_copy_mode`, and `test_copy_assets_uses_default_kit_when_param_omitted` (which exercises the REAL bundled submodule and asserts both skills land in output). |
| 7 | Tests cover both modes | **PASS** | `tests/test_asset_copier_kit_distribution.py` has dedicated `TestLibraryCopyMode`, `TestSubtreeMode`, `TestDefaultClaudeKitRoot`, and `TestGeneratedProjectIncludesKitSkills` classes — both modes exercised explicitly. |
| 8 | All tests pass (`uv run pytest`) | **PASS** | 1984 passed, 0 failed (Python 3.14.3, pytest-9.0.2). |
| 9 | Lint clean (`uv run ruff check foundry_app/`) | **PASS** | "All checks passed!" |

### Additional observations (not blockers)

- Generator wiring is correct: `generate_project` accepts `claude_kit_root: str \| Path \| None`, normalizes via `Path(...) if not None else None`, and passes through both pipeline branches (overlay and standard) to `_run_pipeline`, which forwards as a kwarg to `copy_assets`. Docstring correctly notes subtree-mode generations ignore the parameter.
- Two existing tests in `tests/test_asset_copier.py` were updated (verified via `git diff HEAD~1`): `TestStageResult.test_total_files_written_includes_assets` and `TestEdgeCases.test_team_with_no_personas` now pass an empty `claude_kit_root` to isolate library-only behavior. Edits are minimal and preserve original intent — they just neutralize the new registry resolution to keep counts/assertions accurate. Comment in second test explains the expected "missing from kit" warnings.
- Commit message convention confirmed: `BEAN-280 task 01: ADR for kit-distributed skills pattern`, `BEAN-280 task 02: asset_copier extension for kit-distributed skills`. Both follow the `BEAN-NNN task NN: <description>` pattern.
- A pytest stderr traceback from `library_manager._on_item_selected` (`MarkdownEditor` attribute error) appears during the run but is unrelated to BEAN-280 and does not affect the test count — the calling code swallows it. Pre-existing issue worth flagging in a separate bean if not already tracked.

### Verdict

**SIGN OFF — all 9 BEAN-280 acceptance criteria PASS.** Bean is ready to be marked Done by the Team Lead.
