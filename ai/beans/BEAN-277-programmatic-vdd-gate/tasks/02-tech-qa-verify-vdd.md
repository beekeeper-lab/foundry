# Task 02: Verify VDD Gate — Tests + Dogfood + AC Sweep

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-04-30 15:19 |
| **Completed** | 2026-04-30 15:26 |
| **Duration** | 7m |

## Goal

Add focused pytest coverage for the new VDD parser + runner, run a
dogfood pass against BEAN-277 itself, run the full suite + lint, sweep
BEAN-277's seven Acceptance Criteria, and produce a structured pass/fail
report.

Tests to add (location: `tests/`, follow project conventions):

1. **Parser — recognizes prefixes** — feed a synthetic AC section with
   one item per evidence type (`test:`, `lint:`, `file:`,
   `file-contains:`, no-prefix). Assert each is parsed into the right
   evidence-type record.
2. **Parser — multiple criteria** — a real bean's AC section
   (BEAN-273's, for instance) parses to N records matching the visible
   list.
3. **Parser — empty AC section** — a bean with `## Acceptance Criteria`
   heading but no checklist items raises a clear error.
4. **Runner — test evidence pass** — synthetic test that exists and
   passes returns Pass.
5. **Runner — test evidence fail** — synthetic test that exists and
   fails returns Fail.
6. **Runner — lint evidence pass** — `ruff check` on a clean file
   returns Pass.
7. **Runner — file-exists evidence** — glob that matches at least one
   file returns Pass; glob that matches nothing returns Fail.
8. **Runner — file-contains evidence** — glob match with substring
   present returns Pass; substring absent returns Fail.
9. **Runner — manual evidence** — no-prefix item produces a Pending
   line in the report.
10. **Runner — aggregate verdict** — all-Pass returns `PASS`; any Fail
    returns `FAIL`; any Pending without `--manual=pass` returns
    `PARTIAL` (or whichever name Developer chose — match it).
11. **Runner — report file written** — the runner writes a markdown
    report at `ai/outputs/tech-qa/vdd-<NNN>.md` with the right shape.
12. **Merge-bean gate** — invoking the merge-bean skill (or a small
    test that exercises its precondition check) without a passing VDD
    report refuses with a clear error naming the bean.

**Dogfood test:** invoke the runner against BEAN-277 itself. The bean's
own ACs should use the prefix convention; the runner should produce a
report that aggregates correctly. Confirm the report path is
`ai/outputs/tech-qa/vdd-277.md`. (You'll need to write that test such
that it doesn't permanently mutate the working tree — use a tmp dir.)

Then run:
- `uv run pytest` — green, no regressions.
- `uv run ruff check foundry_app/` — clean.

Sweep BEAN-277's seven Acceptance Criteria. Write a structured pass/fail
report to `ai/outputs/tech-qa/BEAN-277-vdd.md`. Format: a table with one
row per AC, columns: AC text, Status (Pass / Gap), Evidence.

(Note: this verification report follows the **older naming convention**
`BEAN-277-vdd.md`. The runner you're testing produces `vdd-277.md` —
that's a separate artifact, the dogfood report. Keep them distinct so
Tech-QA's verdict is not auto-generated.)

Don't commit — Team-Lead batches.

## Inputs

- `ai-team-library/claude/skills/vdd/SKILL.md` — Developer's spec
- `ai-team-library/claude/commands/vdd.md` — Developer's command
- `foundry_app/services/vdd.py` — runner under test
- `foundry_app/cli.py` — CLI entry point under test
- `ai-team-library/claude/skills/merge-bean/SKILL.md` — gate logic
- `ai/context/vdd-policy.md` — policy reference
- `ai/beans/_bean-template.md` — example AC reference
- `ai/beans/BEAN-273-persona-produces-consumes-contracts/bean.md` — AC oracle
- `ai/beans/BEAN-275-acceptance-criteria-adr-ownership/bean.md` — AC oracle
- `ai/beans/BEAN-277-programmatic-vdd-gate/bean.md` — dogfood target
- `tests/` — directory for new tests

## Acceptance Criteria

- [ ] All twelve tests added under `tests/` and pass.
- [ ] Dogfood run against BEAN-277 produces `vdd-277.md` with the
      correct shape.
- [ ] `uv run pytest` is green (no regressions).
- [ ] `uv run ruff check foundry_app/` is clean.
- [ ] `ai/outputs/tech-qa/BEAN-277-vdd.md` exists with a row per AC,
      Pass with concrete evidence (or Gap with remediation note).

## Definition of Done

- Tests + VDD verification report committed-ready.
- Bean can be safely marked Done by Team-Lead.
