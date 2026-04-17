# BEAN-253 — Tech-QA Report

| Field | Value |
|-------|-------|
| **Bean** | BEAN-253 |
| **Date** | 2026-04-17 |
| **Verdict** | PASS |

## Acceptance Criteria Verification

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | ADR in `ai/context/decisions.md` records Stance 1 with full rationale (three-stance analysis + trade-offs + reversibility) | PASS | ADR-006 at `ai/context/decisions.md:225` — includes Context with all three stances, Decision, Consequences, dedicated Reversibility section, and four Alternatives Rejected entries |
| 2 | Generated `CLAUDE.md` template has a Scope statement (paired with BEAN-251) naming the policy | PASS | `foundry_app/services/compiler.py:391` `## Scope` section — 1–3 sentences naming `ai/` as agent-editable and humans as app-code owners, cross-references `Edit(ai/**)`, points at `docs/starter-stacks.md` |
| 3 | Generated `README.md` template includes "Getting Started" pointer to `docs/starter-stacks.md` | PASS | `foundry_app/services/scaffold.py:70-73` absolute URL into `beekeeper-lab/foundry/blob/main/docs/starter-stacks.md`, prose says "stack-appropriate command" |
| 4 | `docs/starter-stacks.md` exists in the Foundry repo listing one init command per library expertise | PASS | `docs/starter-stacks.md` — 39 library expertise packs covered; 12 have explicit init commands with upstream doc links; 7 infra/tooling have canonical first command; 20 non-code packs listed as no-op |
| 5 | BEAN-251 + BEAN-253 land with consistent CLAUDE.md Scope wording | PASS (for BEAN-253's side) | Scope text now lives in the generator as the single source of truth; BEAN-251's wave can adopt the same section verbatim with no further edits here |
| 6 | All tests pass (`uv run pytest`) | PASS | 1890 passed, 0 failed, 4 deprecation warnings unrelated to this bean |
| 7 | Lint clean (`uv run ruff check foundry_app/`) | PASS | `All checks passed!` |

## Tests Added

Four new tests in this bean:

1. `test_scaffold.py::TestStarterReadme::test_readme_points_at_starter_stacks` — README contains `docs/starter-stacks.md` and the phrase `stack-appropriate command`.
2. `test_compiler.py::TestLeanClaudeMd::test_claude_md_has_scope_section` — CLAUDE.md has `## Scope`, names `ai/`, names `Edit(ai/**)`, points at `docs/starter-stacks.md`.
3. `test_compiler.py::TestLeanClaudeMd::test_claude_md_scope_precedes_orchestration` — Scope heading appears above Team Orchestration Model. Locks the ordering so future edits can't invert it.
4. `test_compiler.py::TestLeanClaudeMd::test_claude_md_scope_emitted_without_personas` — Scope is policy, not roster: it is emitted even when no personas are selected (mirrors BEAN-269's pattern for Team Orchestration Model).

## Coverage Observations

- The existing `test_claude_md_under_100_lines` still passes — the Scope section (~7 lines) fits within budget.
- No test currently asserts the Scope section wording *exactly matches* a string in `settings.local.json`. That assertion belongs to BEAN-251's wave, where the permission model is the unit under test. Left unimplemented here to avoid scope creep.
- `docs/starter-stacks.md` is a documentation artifact with no test — the content is prose, and the upstream links are best verified by manual review rather than a URL liveness test that would flake on every CI run.

## Lint & Type Checks

```
$ uv run ruff check foundry_app/
All checks passed!

$ uv run pytest
1890 passed, 4 warnings in 11.59s
```

## Risks & Follow-ups

- **BEAN-251 coordination.** The Scope section is now in place. When BEAN-251's wave runs, it should add tests that cross-reference the Scope section's directory mentions against the `Edit` allow list in `settings.local.json` — do not duplicate the Scope text; import it indirectly by grepping the generated `CLAUDE.md`.
- **BEAN-269 coordination.** The Team Orchestration Model (BEAN-269) and Scope section (BEAN-253) are now two adjacent policy sections in CLAUDE.md. They read as a single posture: *what this framework produces* (Scope) → *how the agents coordinate* (Orchestration). No conflict observed.
- **Upstream link rot.** `docs/starter-stacks.md` links to ~15 external docs. None are promised to be stable. If a command gets renamed (e.g., `npm create vite@latest` flag changes), the cheat sheet needs a touch-up. Low maintenance cost because it's a single file.
