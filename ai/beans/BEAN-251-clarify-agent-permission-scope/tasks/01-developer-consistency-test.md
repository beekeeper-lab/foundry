# BEAN-251 / Task 01: ADR Cross-Reference + Scope/Permission Consistency Test

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-30 09:13 |
| **Completed** | 2026-04-30 09:14 |
| **Duration** | 1m |

## Goal

Land the small remainder of BEAN-251 — the larger Scope-section work
already shipped under BEAN-253. Specifically:

1. Update ADR-007 to credit BEAN-251 alongside BEAN-253 (these decisions
   were paired from the start; the bean field should reflect that).
2. Add a generator test that asserts the directory roots named in the
   generated CLAUDE.md Scope section match the `Edit` allow list in the
   generated `settings.local.json`. Today's tests assert each side
   independently; the missing assertion is *consistency*.

## Inputs

- ai/beans/BEAN-251-clarify-agent-permission-scope/bean.md — acceptance criteria (lines 44-50)
- ai/context/decisions.md — ADR-007 lives at line 285
- foundry_app/services/compiler.py — `_build_lean_claude_md` (line 450), Scope block at lines 476-498
- ai-team-library/claude/settings/settings.local.json — Edit allow list (`Edit(ai/**)`)
- tests/test_compiler.py — existing Scope-section tests at lines 1410-1450 (TestLeanClaudeMd class or similar)

## Acceptance Criteria

- [ ] ADR-007 in `ai/context/decisions.md` lists both `BEAN-251` and `BEAN-253`
      in its `Bean` field. (It currently lists only BEAN-253; the ADR's body
      already says "Paired with ADR-relevant work in BEAN-251".)
- [ ] A new test in `tests/test_compiler.py` asserts that the directory roots
      named in the generated CLAUDE.md Scope section (`ai/`) match the
      directory roots in the generated `settings.local.json` `Edit` allow list.
      The test should fail if either side drifts: e.g. if Scope mentions
      `src/` but Edit only allows `ai/**`, or if Edit gains `app/**` but
      Scope still names only `ai/`.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Definition of Done

- ADR-007 cross-reference added.
- Consistency test added and passing.
- Full test suite + lint pass.
