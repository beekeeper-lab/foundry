# BEAN-251 Verification Report

**Date:** 2026-04-30
**Bean:** BEAN-251 — Clarify Agent Permission Scope in Generated Projects

## Verification Table

| Check | Status | Evidence |
|---|---|---|
| Stance 1 recorded as ADR | PASS | ADR-007 in `ai/context/decisions.md` (line 285) — `Bean: BEAN-251, BEAN-253` |
| Generated CLAUDE.md has Scope section in first third | PASS | `compiler._build_lean_claude_md` emits `## Scope` immediately after the project header (line 476-498); `test_claude_md_scope_precedes_orchestration` passes |
| Scope names `ai/` as agent-editable tree | PASS | Scope text contains `Edit(ai/**)`, `under \`ai/\``, and explicit "the human initializes and implements the application source code" |
| `settings.local.json` retains `Edit(ai/**)` | PASS | `ai-team-library/claude/settings/settings.local.json` allow list includes `Edit(ai/**)` and no other `Edit(...)` directives |
| Consistency test asserts Scope ↔ Edit match | PASS | New `test_claude_md_scope_matches_settings_edit_permissions` in `tests/test_compiler.py::TestLeanClaudeMd` parses both files and verifies every Edit directory root appears in the Scope section |
| `uv run pytest` | PASS | 2169 passed in 11.34s (was 2168 before this bean) |
| `uv run ruff check foundry_app/` | PASS | "All checks passed!" |

## Verdict

**OVERALL: PASS** — Ready to mark Done.

## Notes

- The bulk of BEAN-251's deliverables (Scope section, ADR rationale,
  starter-stacks pointer) shipped under BEAN-253 because the two beans
  were paired Stance-1 outcomes. ADR-007 already captured the rationale.
  This bean's residual work was the explicit drift-guard test that
  enforces consistency between the Scope section text and
  `settings.local.json`'s `Edit` allow list — that test is the
  acceptance criterion most directly tied to BEAN-251 specifically.
- ADR-007's `Bean` field now credits both BEAN-251 and BEAN-253.
