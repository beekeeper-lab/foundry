# Task 03: Verify BEAN-280 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01, 02 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

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
