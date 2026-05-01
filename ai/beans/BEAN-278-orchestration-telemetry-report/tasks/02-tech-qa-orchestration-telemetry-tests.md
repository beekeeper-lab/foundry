# Task 02: Verify Orchestration Telemetry — Hook Tests, Skill Walkthrough, Aggregator Smoke

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Cover the new behaviors: telemetry hook populates the new fields
without breaking existing ones, the new orchestration-report skill
is unambiguous and runnable end-to-end on the real backlog, and the
new SKILL.md additions to `/spawn-task` and `/handoff` (bounce
counter, dispatch mode) read clearly from a cold start.

## Inputs

- `ai/beans/BEAN-278-orchestration-telemetry-report/bean.md` — bean
  acceptance criteria.
- The artifacts the Developer (Task 01) just produced — read what's
  there:
  - `ai/beans/_bean-template.md` (new Orchestration Telemetry block)
  - `.claude/hooks/telemetry-stamp.py` (look at the new
    Personas-activated and Dispatch-mode logic only)
  - `ai-team-library/claude/skills/spawn-task/SKILL.md` (dispatch-mode
    + bounce-counter additions)
  - `ai-team-library/claude/skills/handoff/SKILL.md` (bounce-counter)
  - `ai-team-library/claude/skills/orchestration-report/SKILL.md`
    (new file)
  - `ai-team-library/claude/commands/orchestration-report.md` (new
    file, ≤30 lines)
- `tests/test_telemetry_*.py` (any existing telemetry tests) for
  the test idiom.
- `tests/` for placement of new tests. Use existing
  `test_telemetry_stamp.py` if it exists, otherwise create
  `test_orchestration_telemetry.py`.

## Acceptance Criteria

- [ ] Hook test: a fixture bean with a Telemetry block + the new
      Orchestration Telemetry block has its `Personas activated` and
      `Dispatch mode` populated correctly when status flips to Done.
- [ ] Hook test: a fixture bean *without* the new Orchestration
      Telemetry block is left alone (no crash, no silent injection).
- [ ] Hook test: re-running the hook on a bean with already-populated
      Orchestration Telemetry is idempotent (no duplicate entries, no
      overwrites of persona-recorded values).
- [ ] Cold-start review of `orchestration-report` SKILL.md: any
      persona reading it can run the report without supervisor
      clarification. Note any ambiguities in your report rather than
      fixing them silently.
- [ ] Smoke run: invoke the orchestration-report skill (or its core
      computation) against the real backlog and confirm the output
      file is well-formed (table headers, at least one row, the
      verdict paragraph cites at least two metrics with values).
      If the skill is markdown-only and not directly runnable from a
      test, write a unit test for the aggregator function the skill
      references; if no such function exists yet, file as a finding.
- [ ] `uv run pytest` passes (full suite).
- [ ] `uv run ruff check foundry_app/` clean.

## Definition of Done

- All hook tests added and passing.
- Cold-start review report delivered in the supervisor handback.
- Smoke confirmation that the report produces well-formed output.
- Full pytest suite green.
- Status set to `Done`.

## Notes

**Verify, don't re-implement.** If you find a Developer bug in the
telemetry hook (wrong field name, double-stamping, etc.), **stop and
report** rather than fix. The Developer owns the hook; Tech-QA verifies.

**Do not destroy real telemetry.** Hook tests should run against
fixture bean files (under `tmp_path`), never against the real
`ai/beans/` directory.

**Coverage focus.** The contract this bean adds is: "Orchestration
Telemetry is captured per bean; the report aggregator can answer
'is the orchestration paying for itself?'". Tests should make that
contract break loudly if a future change weakens it.

**Light-touch testing for skills.** No need to write Python tests
for behaviors that are *only* expressible in the markdown spec.
The hook is testable; the report skill is partially testable
(aggregator logic if it exists).
