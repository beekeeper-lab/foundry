# Task 02: Tech-QA Verify Product Strategy Stack

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | Task 01 |
| **Status** | Done |
| **Started** | 2026-02-20 19:58 |
| **Completed** | 2026-02-20 19:58 |
| **Duration** | < 1m |

## Goal

Verify that all product-strategy stack files meet quality standards and follow the established template pattern.

## Inputs

- Task 01 output: `ai-team-library/stacks/product-strategy/*.md`
- `ai-team-library/stacks/clean-code/principles.md` (template pattern reference)
- Bean acceptance criteria

## Verification Checks

1. **File existence:** All 6 required files exist in `ai-team-library/stacks/product-strategy/`
2. **Template compliance:** Each file has: Defaults table with alternatives, Do/Don't lists, Common Pitfalls, Checklist
3. **Content quality:** Guidance is specific, actionable, and production-ready (not generic filler)
4. **Topic coverage:** OKRs, RICE, MoSCoW, user story mapping, competitive analysis, GTM planning, feature lifecycle — all covered
5. **Tests pass:** `uv run pytest` — all pass
6. **Lint clean:** `uv run ruff check foundry_app/` — no errors

## Example Output

A verification summary noting pass/fail for each check, with specific issues if any.

## Definition of Done

- [ ] All 6 files verified for template compliance
- [ ] Content quality confirmed (no generic placeholder text)
- [ ] All tests pass
- [ ] Lint clean
- [ ] Verification summary documented
