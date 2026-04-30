# BEAN-251 / Task 02: Verify Scope/Permission Consistency

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01-developer-consistency-test |
| **Status** | Done |
| **Started** | 2026-04-30 09:15 |
| **Completed** | 2026-04-30 09:15 |
| **Duration** | < 1m |

## Goal

Independently verify all BEAN-251 acceptance criteria.

## Inputs

- ai/beans/BEAN-251-clarify-agent-permission-scope/bean.md — acceptance criteria
- ai/context/decisions.md — ADR-007 cross-reference
- foundry_app/services/compiler.py — Scope section in `_build_lean_claude_md`
- ai-team-library/claude/settings/settings.local.json — Edit allow list
- tests/test_compiler.py — generator tests (existing + new consistency test)

## Acceptance Criteria

- [ ] ADR-007's `Bean` field names both BEAN-251 and BEAN-253.
- [ ] Generated CLAUDE.md (after running `compile_project` in a test or
      smoke generation) contains a `## Scope` section in the first third
      of the document.
- [ ] Scope section names `ai/` as the agent-editable tree.
- [ ] `settings.local.json` retains `Edit(ai/**)` (not expanded).
- [ ] New consistency test runs: `uv run pytest -k consistency` (or
      whatever the test name is) and passes.
- [ ] `uv run pytest` — full suite passes.
- [ ] `uv run ruff check foundry_app/` — clean.

## Definition of Done

- All checks PASS. Verification report at
  `ai/outputs/tech-qa/bean-251-verification.md`.
