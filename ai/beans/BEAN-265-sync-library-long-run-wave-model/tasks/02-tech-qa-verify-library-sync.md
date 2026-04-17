# Task 02 — Tech-QA: Verify Library Sync, Regeneration, and Gates

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-265/02 |
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 19:04 |
| **Completed** | 2026-04-17 19:05 |
| **Duration** | 1m |

## Goal

Independently verify every acceptance criterion on BEAN-265:

1. Library `long-run` skill describes the new wave model.
2. Grep of `ai-team-library/claude/` has no mandatory 4-persona wave references.
3. Regenerating `small-python-team.yml` yields a long-run skill file with the updated wording.
4. `uv run pytest` passes.
5. `uv run ruff check foundry_app/` passes.

## Inputs

- Developer task output (library file edits).
- `examples/small-python-team.yml` — regeneration fixture.
- `ai-team-library/` — source library for generation.

## Verification Steps

1. **Grep** — Run `rg "BA → Architect → Developer → Tech-QA" ai-team-library/claude/` and confirm zero matches.
2. **Read updated library `long-run/SKILL.md`** — confirm the decomposition + parallel-mode launcher blocks both describe Developer → Tech-QA default with BA/Architect opt-in.
3. **Regeneration check** — Generate `small-python-team.yml` into a temp output:
   ```
   uv run foundry-cli generate examples/small-python-team.yml --library ai-team-library --output /tmp/bean265-regen
   ```
   Then read the generated `.claude/skills/long-run/SKILL.md` and confirm it contains the new wave wording and no old wording. Clean up the temp output.
4. **Tests** — `uv run pytest`.
5. **Lint** — `uv run ruff check foundry_app/`.

## Acceptance Criteria

- [ ] Grep is clean.
- [ ] Library `long-run/SKILL.md` wording matches new wave model.
- [ ] Regenerated project inherits the updated skill file.
- [ ] All tests pass.
- [ ] Lint clean.

## Definition of Done

- All five AC items verified and evidence recorded in the Tech-QA output.
- Bean acceptance criteria checkboxes flipped.
- Tech-QA output saved to `ai/outputs/tech-qa/`.
