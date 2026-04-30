# Task 01: Build VDD Skill, Command, and Merge-Bean Integration

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-30 15:14 |
| **Completed** | 2026-04-30 15:19 |
| **Duration** | 5m |

## Goal

Implement the four artifacts BEAN-277 specifies:

1. **`ai-team-library/claude/skills/vdd/SKILL.md`** — canonical skill spec
   describing how to parse a bean's `## Acceptance Criteria` section, run
   each criterion's evidence type programmatically, and emit a structured
   pass/fail report. Follow the conventions of other library skills
   (e.g., `merge-bean/SKILL.md`, `long-run/SKILL.md`): Description,
   Trigger, Inputs, Process (numbered phases), Outputs, Quality Criteria,
   Error Conditions, Dependencies. Aim for clarity over brevity (~150–250
   lines).

2. **Criterion-prefix convention** — codify in `vdd-policy.md` AND in the
   bean template's AC section. The convention: each AC checklist item
   may carry an evidence-type prefix in parentheses *immediately* after
   the checkbox, e.g.
   `- [ ] (test:tests/test_foo.py::test_bar) Foo behaves correctly`.
   Recognized prefixes:
   - `test:<pytest-pattern-or-path>` — runs `uv run pytest -k <pattern>`
     or against the path; pass = exit 0.
   - `lint:<path>` — runs `uv run ruff check <path>`; pass = "All checks
     passed!" in output.
   - `file:<glob>` — pass when at least one path matches the glob.
   - `file-contains:<glob>::<substring>` — pass when at least one matched
     file contains the substring.
   - (no prefix) → manual: emit a `[MANUAL]` line in the report; aggregate
     verdict counts manual as `Pending` rather than Pass or Fail unless
     `--manual=pass` is passed.

3. **`ai-team-library/claude/commands/vdd.md`** — thin command file
   (≤30 lines per BEAN-249). Triggers the skill with `<bean-id>` arg.

4. **Update `ai-team-library/claude/skills/merge-bean/SKILL.md`** — add a
   pre-merge gate: refuse to merge if `ai/outputs/tech-qa/vdd-<bean-id>.md`
   is missing OR its aggregate verdict is `FAIL`. Naming convention:
   the VDD report at the canonical path `ai/outputs/tech-qa/vdd-<NNN>.md`
   (zero-padded NNN to match bean ID).

5. **Update `ai/context/vdd-policy.md`** — reference the new `/vdd`
   command and the criterion-prefix convention.

6. **Bean template AC convention update** — add a one-line example AC
   showing the prefix to `ai/beans/_bean-template.md` AC section.

7. **Implementation language and location.** The skill is library-canonical
   (markdown spec in `ai-team-library/`). The runtime executor can be a
   small Python module:
   - Place at `foundry_app/services/vdd.py` (a small parser + runner).
   - Add a CLI entry point so `uv run foundry-cli vdd <bean-id>` invokes
     it. Wire it through `foundry_app/cli.py`. (If the existing CLI does
     not have a clean extension point, prefer a module-level `main()`
     function callable from a thin script.)
   - The Claude-side `/vdd` command can either shell out to the CLI or
     direct-invoke the runner; the SKILL.md spec should describe both
     paths so callers in different contexts work.

Constraints:
- No new third-party deps. PyYAML / stdlib only for the runner.
- The runner MUST handle "no acceptance criteria found" gracefully —
  produce a report with status `EMPTY` and exit non-zero so merge-bean
  can refuse.
- The runner MUST NOT shell-inject — use `subprocess.run` with arg lists,
  not strings.
- Idempotent: re-running `/vdd <bean-id>` overwrites the previous report.
- Don't run `uv run pytest` as part of this task — Tech-QA will. You
  may run `uv run ruff check foundry_app/` as a sanity check on your
  Python changes.
- Don't commit — Team-Lead batches.

## Inputs

- `ai/beans/BEAN-277-programmatic-vdd-gate/bean.md` — bean spec
- `ai/context/vdd-policy.md` — existing policy text to update
- `ai-team-library/claude/skills/merge-bean/SKILL.md` — skill to extend
- `ai-team-library/claude/skills/long-run/SKILL.md` — convention reference
- `ai/beans/_bean-template.md` — AC section to update with prefix example
- `foundry_app/cli.py` — CLI extension site
- `ai/beans/BEAN-273-persona-produces-consumes-contracts/bean.md` — sample
  AC section (a real bean to test the parser against)
- `ai/beans/BEAN-275-acceptance-criteria-adr-ownership/bean.md` — sample
  AC section (a real bean to test the parser against)

## Acceptance Criteria

- [ ] `ai-team-library/claude/skills/vdd/SKILL.md` exists with the full
      Process / Inputs / Outputs / Errors / Dependencies structure.
- [ ] `ai-team-library/claude/commands/vdd.md` exists, ≤30 lines.
- [ ] `foundry_app/services/vdd.py` exists with a parser and a runner;
      handles all four evidence types + manual fallback; raises a clear
      error when ACs are absent.
- [ ] `foundry_app/cli.py` exposes the new command (or equivalent entry
      point — document if you go a different way).
- [ ] `merge-bean/SKILL.md` adds the pre-merge VDD gate.
- [ ] `vdd-policy.md` references the new command and the prefix
      convention.
- [ ] Bean template's AC section has a one-line example with the prefix.
- [ ] `uv run ruff check foundry_app/` is clean.

## Definition of Done

- All artifacts created / updated.
- Tech-QA's task can verify by running the runner against this bean
  (BEAN-277) — its own ACs use the prefix convention as a dogfood test.
