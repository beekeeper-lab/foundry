# Task 02: `asset_copier` Extension for Kit-Distributed Skills

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Implement the kit-distributed skills resolution contract defined by
the Architect's ADR (Task 01). When `asset_copier.copy_assets()` runs
in library-copy mode (subtree mode off), it pulls a designated set of
"kit-distributed" skills from `<claude_kit_root>/skills/<name>/`
instead of from `<library_root>/claude/skills/<name>/`. In subtree
mode, these skills are skipped because the subtree already covers
them.

The change closes the existing gap where `generate-image` (and the
soon-to-be-built `generate-audio`) are present in subtree-mode
projects but absent in library-copy-mode projects.

## Inputs

- `ai/beans/BEAN-280-claudekit-canonical-skills-distribution/bean.md` — full scope and acceptance criteria
- `ai/context/decisions.md` — ADR from Task 01; the design contract this task implements
- `foundry_app/services/asset_copier.py` — file to modify
- `foundry_app/services/generator.py` — caller; needs to pass `claude_kit_root` through
- `foundry_app/core/models.py` — `CompositionSpec`, `LibraryIndex` (referenced by copy_assets signature)
- `foundry_app/services/subtree_setup.py` — read for context on subtree mode detection (so the new logic correctly skips when subtree is active)
- `tests/services/` — directory for new tests (match existing test file naming: `test_asset_copier_*.py` if pattern, otherwise add to existing test file)
- `.claude/shared/skills/` — the actual canonical location at runtime (used by tests to verify resolution)

## Changes Required

1. **Add `_KIT_DISTRIBUTED_SKILLS` constant** in `asset_copier.py`:
   ```python
   _KIT_DISTRIBUTED_SKILLS: tuple[str, ...] = ("generate-image", "generate-screen")
   ```
   Tuple, not list — these are immutable. Naming exactly matches the ADR.

2. **Extend `copy_assets()` signature** with `claude_kit_root` parameter:
   - Type: `str | Path | None`, default `None`.
   - When `None`, derive from the project's checkout: `Path(__file__).resolve().parents[2] / ".claude" / "shared"` (i.e., the Foundry repo's bundled submodule).
   - Document that callers may pass an explicit path for testing.

3. **Skill resolution logic** — in the section that copies skills:
   - For each skill referenced by `spec`/`library_index`:
     - If skill name is in `_KIT_DISTRIBUTED_SKILLS`:
       - In subtree mode (caller passes a flag, or copier infers from `output_dir/.claude/shared` existing): skip — already provided by subtree.
       - Otherwise (library-copy mode): copy from `<claude_kit_root>/skills/<name>/` to `<output_dir>/.claude/skills/<name>/`.
     - Else: existing behavior (copy from `<library_root>/claude/skills/<name>/`).
   - Apply the same overlay-safe rules as the existing copier (skip identical files, warn on conflicts).

4. **Wire through `generator.py`** — `generate_project()` (or whatever currently calls `copy_assets`) accepts an optional `claude_kit_root` and passes it through. Backwards-compatible default = `None` (auto-derive).

5. **Tests** at `tests/services/test_asset_copier_kit_distribution.py` (or extend the existing asset_copier test file):
   - `test_kit_distributed_skill_resolves_from_claude_kit_in_library_copy_mode`
   - `test_kit_distributed_skill_skipped_in_subtree_mode`
   - `test_non_kit_skill_resolves_from_library` (regression — existing behavior preserved)
   - `test_default_claude_kit_root_resolves_to_bundled_submodule`
   - `test_kit_distributed_skills_constant_includes_generate_image_and_screen`
   - `test_generated_project_has_generate_image_in_library_copy_mode` (end-to-end-ish: spin up a fake kit dir, run copy_assets, assert the skill landed in the output `.claude/skills/`)

## Acceptance Criteria

- [ ] `_KIT_DISTRIBUTED_SKILLS` constant defined in `asset_copier.py` matching the ADR's named registry.
- [ ] `copy_assets()` accepts `claude_kit_root` parameter with sensible default.
- [ ] In library-copy mode, kit-distributed skills resolve from `claude_kit_root/skills/<name>/`.
- [ ] In subtree mode, kit-distributed skills are not copied (subtree already covers them).
- [ ] Non-kit skills continue to resolve from the library (regression-safe).
- [ ] `generator.py` passes `claude_kit_root` through to `asset_copier`.
- [ ] All new tests pass; existing tests still pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Definition of Done

- Code changes committed on the feature branch.
- Tests pass; lint clean.
- A library-copy-mode generated project would now include `.claude/skills/generate-image/` and `.claude/skills/generate-screen/` (verified by the end-to-end-ish test).
- Commit message: `BEAN-280 task 02: asset_copier extension for kit-distributed skills`.
