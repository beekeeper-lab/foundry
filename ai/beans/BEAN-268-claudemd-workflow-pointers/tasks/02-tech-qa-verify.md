# BEAN-268 / Task 02: Verify Workflow Section

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01-developer-workflow-section |
| **Status** | Done |
| **Started** | 2026-04-30 09:42 |
| **Completed** | 2026-04-30 09:42 |
| **Duration** | < 1m |

## Goal

Verify the new Workflow section meets BEAN-268's acceptance criteria.

## Inputs

- ai/beans/BEAN-268-claudemd-workflow-pointers/bean.md — acceptance criteria
- foundry_app/services/compiler.py — `_build_lean_claude_md`
- tests/test_compiler.py — new test additions

## Acceptance Criteria

- [ ] Generate a project (or run an existing test that emits CLAUDE.md) and confirm the file contains a `## Workflow` section between `## Team Orchestration Model` and `## Documentation`.
- [ ] Confirm the section names the bean workflow and includes pointers to at least: `/long-run`, `/show-backlog`, and `ai/beans/_index.md`.
- [ ] Confirm the section is ≤25 lines.
- [ ] `uv run pytest` — full suite passes.
- [ ] `uv run ruff check foundry_app/` — clean.

## Definition of Done

- All checks PASS. Verification report at
  `ai/outputs/tech-qa/bean-268-verification.md`.
