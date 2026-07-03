# SPEC-013: Seeder emits VDD-verifiable acceptance criteria

- **Priority:** P1
- **Effort:** S
- **Area:** pipeline
- **Depends on:** none
- **Status:** Proposed

## Problem

A freshly generated project's starter bean can never programmatically pass its own VDD gate. The seeder writes acceptance criteria with no evidence prefixes, so `/vdd` classifies every criterion as manual and the best achievable verdict is `PARTIAL`. The very first thing a new AI team experiences is a quality gate that cannot go green — which teaches the team (and the humans watching) that the gate is ceremonial. The evidence-prefix convention already exists and is already used by `bean_approval.py`'s guidance text; the seeder just doesn't follow it.

## Evidence

- `foundry_app/services/seeder.py:225-226` — the starter bean's ACs: `- [ ] Every task under \`tasks/\` is marked Done.` and `- [ ] The Team Lead has created the next bean(s) from project requirements.` Both unprefixed → manual.
- `foundry_app/services/vdd.py:11-17` — the dispatcher: `test:<pytest-target>`, `lint:<path>`, `file:<glob>`, `file-contains:<glob>::<substring>`; unprefixed items become manual, and manual items cap the verdict at `PARTIAL`.
- `foundry_app/services/bean_approval.py:45-59` — the convention is documented and even provides prefixed boilerplate equivalents (`- [ ] (test:tests/) All tests pass (\`uv run pytest\`)`), proving the intended authoring style; the seeder predates it.
- `ai-team-library/claude/skills/merge-bean/SKILL.md:108-110` — merge path treats `PARTIAL` as requiring extra manual confirmation, so the starter bean also exercises the slow path by default.

## Proposed change

1. **Rewrite the starter bean's ACs as machine-checkable criteria.** The first AC is checkable today: task completion is observable in the task files. Emit e.g.:
   - `- [ ] (file:ai/beans/BEAN-001-bootstrap/tasks/*.md) Kickoff tasks exist for every selected persona`
   - `- [ ] (file-contains:ai/beans/BEAN-001-bootstrap/tasks/*.md::Status: Done)` — note: `file-contains` passes when *at least one* file matches (`vdd.py:17`); if per-file all-done semantics are needed, either emit one `file-contains:` criterion per seeded task file (the seeder knows the exact list at generation time — preferred, zero engine change) or extend vdd with an `all-files-contain:` prefix (engine change, keep optional).
   - Keep exactly one genuinely-human criterion, explicitly marked: `- [ ] Team Lead has drafted the next bean(s) from project requirements (manual — requires human/lead judgment)`.
2. **Seeded per-persona kickoff tasks get prefixed ACs too** where mechanical (e.g. developer kickoff: `(test:tests/)` once the project has tests; where the project has none yet, use `file:` existence checks on the artifacts the task must produce, which the seeder knows because it writes the task's Outputs section).
3. **Document the expected verdict.** The starter bean's Notes section states: "This bean is expected to reach VDD `PASS` after the manual criterion is confirmed via `/vdd --manual=pass`" (or reach `PARTIAL` with exactly one open manual item) — so the first `/vdd` run has a defined, teachable outcome instead of an ambiguous yellow.
4. **Test at the right level:** a generation test that runs the real `vdd` service against a freshly seeded project fixture and asserts the aggregate verdict is `PARTIAL` with exactly one manual item before confirmation, and `PASS` after simulated manual confirmation — this pins the seeder and the vdd engine to each other permanently.

## Out of scope

- Changing vdd verdict semantics or adding new prefixes beyond the optional `all-files-contain:` (decide during implementation; default is no engine change).
- Backfilling prefixes into Foundry's own historical beans.
- The hook that enforces VDD at Done-transition (SPEC-008).

## Acceptance criteria

- [ ] (test:tests/test_seeder.py::test_starter_bean_acs_prefixed) Seeded bean.md contains no unprefixed AC except the single documented manual one
- [ ] (test:tests/test_seeder_vdd_integration.py) Fresh seeded project: vdd verdict is PARTIAL with exactly 1 manual item; PASS after manual confirmation
- [ ] (file-contains:foundry_app/services/seeder.py::file-contains:) Seeder source carries the prefixed templates
- [ ] (lint:foundry_app/services/seeder.py) Ruff clean
- [ ] manual: Generate a project from `examples/small-python-team.yml`, run `/vdd BEAN-001` in it, observe the documented verdict

## Files to touch

- `foundry_app/services/seeder.py` (`_render_bean_md` at `:200-240`; task templates)
- `foundry_app/services/vdd.py` (only if `all-files-contain:` is chosen)
- `tests/test_seeder.py`, `tests/test_seeder_vdd_integration.py` (new)
