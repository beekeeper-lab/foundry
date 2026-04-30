# BEAN-268 Verification Report

**Date:** 2026-04-30
**Bean:** BEAN-268 — Add Workflow Pointers Section to Generated CLAUDE.md

## Verification Table

| Check | Status | Evidence |
|---|---|---|
| `## Workflow` section emitted | PASS | Smoke generation of `examples/small-python-team.yml` produced a CLAUDE.md with `## Workflow` at line 46 |
| Section between `## Team Orchestration Model` and `## Documentation` | PASS | Section ordering: Orchestration (37) → Workflow (46) → Documentation (61) |
| Names the bean workflow | PASS | Section text: "Work is tracked using the **bean workflow**: each unit of work … is a bean stored under `ai/beans/BEAN-NNN-<slug>/`" |
| Pointer to `ai/beans/_index.md` | PASS | "The backlog index is `ai/beans/_index.md`" |
| Pointer to `ai/context/bean-workflow.md` | PASS | "See `ai/context/bean-workflow.md` for the full lifecycle" |
| 6 default slash commands listed (≥5, ≤7) | PASS | `/long-run`, `/show-backlog`, `/pick-bean`, `/new-bean`, `/spawn-task`, `/review-beans` |
| Each command has one-line description + file pointer | PASS | All 6 follow the pattern: `\`/cmd\` — description (\`.claude/commands/cmd.md\`)` |
| Section ≤25 lines | PASS | 15 lines (between heading and next `##`, exclusive of trailing blank) |
| `uv run pytest` | PASS | 2197 passed (was 2194; +3 new workflow tests) |
| `uv run ruff check foundry_app/` | PASS | "All checks passed!" |

## Verdict

**OVERALL: PASS** — Ready to mark Done.

## Notes

The 15-line section honors the bean's "signposts are cheap, full docs
are expensive" principle. It re-adds discoverability that BEAN-164 /
BEAN-233 over-pruned, without re-expanding to pre-prune size.
