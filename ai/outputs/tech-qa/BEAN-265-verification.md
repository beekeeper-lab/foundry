# BEAN-265 — Tech-QA Verification Report

**Bean:** BEAN-265 Sync Library long-run Skill With New Wave Model
**Date:** 2026-04-17

## Results

| # | Acceptance Criterion | Result | Evidence |
|---|----------------------|--------|----------|
| 1 | `ai-team-library/claude/skills/long-run/SKILL.md` describes Developer → Tech-QA default with BA/Architect opt-in | PASS | Decomposition block (line ~68) and parallel-mode launcher prompt (line ~175) both reflect the new wave. Phase-4 "Skip inapplicable roles" step (line ~95) now says Tech-QA must never be skipped and BA/Architect skips get an inline tag. |
| 2 | Grep of `ai-team-library/claude/` has no mandatory 4-persona references | PASS | `rg "BA → Architect → Developer → Tech-QA" ai-team-library/claude/` returns no matches. |
| 3 | Regenerating `small-python-team.yml` yields updated long-run skill | PASS | `foundry-cli generate examples/small-python-team.yml --library ai-team-library --output /tmp/bean265-regen-*` wrote 133 files. `.claude/skills/long-run/SKILL.md:69` contains the new "Tech-QA is mandatory" sentence; `:176` contains the new wave line. No old wave wording found. |
| 4 | `uv run pytest` passes | PASS | `1886 passed, 4 warnings in 13.52s` (Qt deprecation warnings only). |
| 5 | `uv run ruff check foundry_app/` passes | PASS | `All checks passed!` |

## Files Updated

- `ai-team-library/claude/skills/long-run/SKILL.md` — decomposition wave, skip guidance, parallel-mode launcher prompt.
- `ai-team-library/claude/commands/long-run.md` — decomposition step, parallel-mode launcher prompt.
- `ai-team-library/claude/skills/new-work/SKILL.md` — feature + bug routing.
- `ai-team-library/claude/commands/new-work.md` — feature example wording.

## Notes

- `ai-team-library/claude/commands/new-work.md:75` and `:93` still show specialised wavelets (`Developer → Tech-QA` for bugs, `Architect → Developer → Tech-QA` for refactors) — these are example routings, not mandatory waves, and already align with the opt-in model.
- `ai-team-library/claude/skills/deploy/SKILL.md:50` mentions "BA", "Architect" as search synonyms for doc-audit — not a wave directive; left as-is.
- `ai-team-library/claude/commands/handoff.md:69,75` describes handoff types ("Developer to Tech-QA", "BA to Architect") — not a mandatory wave; left as-is.
- `ai-team-library/process/context/bean-workflow.md:105` still says "BA → Architect → Developer → Tech-QA" but is **out of scope** per the bean (scope limits to `ai-team-library/claude/`). Flagged for follow-up.

## Verdict

All five acceptance criteria pass. Ready to close.
