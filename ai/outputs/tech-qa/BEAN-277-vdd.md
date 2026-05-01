# Tech-QA VDD Report — BEAN-277 (Programmatic VDD Gate Skill)

**Verifier:** Tech-QA persona, Task 02
**Date:** 2026-04-30
**Branch:** `bean/BEAN-277-programmatic-vdd-gate`
**Verdict:** PASS (with one Developer fix folded in — see Notes)

This is the **human-authored** verification artifact (older naming
convention `BEAN-277-vdd.md`). The runner-generated artifact uses
`vdd-277.md`; the two are intentionally distinct.

## Test execution

| Check | Command | Result |
|-------|---------|--------|
| Full suite | `uv run pytest` | `2270 passed, 4 warnings in 12.13s` |
| Lint | `uv run ruff check foundry_app/` | `All checks passed!` |
| New tests | `uv run pytest tests/test_vdd.py` | `17 passed in 0.15s` |

`tests/test_vdd.py` (17 tests, +408 lines) covers all twelve required
test categories from Task 02 plus three sanity checks (CLI dispatch,
exit-code mapping, `normalize_bean_id` contract). Exact mapping:

| # | Required test | tests/test_vdd.py |
|---|---|---|
| 1 | Parser — recognizes prefixes | `test_parser_recognizes_each_prefix` |
| 2 | Parser — multiple criteria from real bean | `test_parser_multiple_criteria_from_real_bean` (BEAN-273 oracle) |
| 3 | Parser — empty AC section | `test_parser_empty_ac_section_returns_empty_list` |
| 4 | Runner — test evidence pass | `test_runner_test_evidence_pass` |
| 5 | Runner — test evidence fail | `test_runner_test_evidence_fail` |
| 6 | Runner — lint evidence pass | `test_runner_lint_evidence_pass_clean_file` |
| 7 | Runner — file-exists evidence | `test_runner_file_exists_match_and_no_match` |
| 8 | Runner — file-contains evidence | `test_runner_file_contains_present_and_absent` |
| 9 | Runner — manual evidence (Pending line) | `test_runner_manual_evidence_emits_pending_line` |
| 10 | Runner — aggregate verdict | `test_runner_aggregate_verdict_combinations` |
| 11 | Runner — report file written | `test_runner_writes_report_at_canonical_path` |
| 12 | Merge-bean gate refuses without PASS | `test_merge_bean_gate_refuses_without_passing_vdd` + `test_merge_bean_skill_documents_vdd_gate` |

## Dogfood — `/vdd 277`

```
$ python -m foundry_app.services.vdd 277 --repo-root /tmp/foundry-vdd-dogfood
VDD report: /tmp/foundry-vdd-dogfood/ai/outputs/tech-qa/vdd-277.md
Aggregate verdict: PARTIAL
EXIT=1
```

The runner emits a 7-row table at the canonical path. Verdict is
`PARTIAL` because BEAN-277's own AC items are legacy unprefixed
criteria (they parse, dispatch to MANUAL, and are correctly counted —
exactly the behavior the spec describes for backward compatibility).
The dogfood was performed in `/tmp/foundry-vdd-dogfood/`; the working
tree was not mutated.

## Bean AC sweep — BEAN-277 (the seven Acceptance Criteria)

| # | Acceptance Criterion | Status | Evidence |
|---|---|--------|----------|
| 1 | `/vdd <bean-id>` exists and produces `ai/outputs/tech-qa/vdd-<bean-id>.md`. | Pass | Skill `ai-team-library/claude/skills/vdd/SKILL.md` + command `ai-team-library/claude/commands/vdd.md` exist. CLI subcommand wired in `foundry_app/cli.py:75-95`. Runner `foundry_app/services/vdd.py` writes `vdd-<NNN>.md` (verified by `test_runner_writes_report_at_canonical_path` and dogfood). |
| 2 | At least three evidence types implemented: test, lint, file-exists. Manual fallback works. | Pass | All four kinds (`test`, `lint`, `file`, `file-contains`) plus manual fallback are exercised by tests #4–#9 in `tests/test_vdd.py`. Manual produces `RESULT_MANUAL`/`PARTIAL` (test #9). |
| 3 | `/merge-bean` refuses to merge without a passing VDD report; error message names the bean. | Pass | `ai-team-library/claude/skills/merge-bean/SKILL.md` Phase 1 step 2a documents the gate (VDDMissing / VDDFail / VDDEmpty / VDDPartial) and names the bean. `test_merge_bean_gate_refuses_without_passing_vdd` exercises the precondition logic (missing → refuse, PARTIAL → refuse, PASS → allow); `test_merge_bean_skill_documents_vdd_gate` is a regression catcher. |
| 4 | Bean template's Acceptance Criteria section is updated to show the evidence-type prefix convention. | Pass | `ai/beans/_bean-template.md:33-44` lists the convention blockquote and four prefixed example items (test/lint). Approval-gate `_PLACEHOLDER_BODY_LINES` and `_BOILERPLATE_CRITERIA` in `foundry_app/services/bean_approval.py` updated to keep the gate working — see Notes. |
| 5 | `vdd-policy.md` references the command. | Pass | `ai/context/vdd-policy.md:79-113` adds a "Programmatic Gate: `/vdd`" section that names the command, the runtime module, the canonical report path, the prefix table, and the EMPTY-as-hard-fail rule. |
| 6 | All tests pass (`uv run pytest`). | Pass | `2270 passed, 4 warnings in 12.13s`. |
| 7 | Lint clean (`uv run ruff check foundry_app/`). | Pass | `All checks passed!` |

## Notes

**One regression caught and fixed.** The Developer's bean-template edit
(AC #4) introduced new template lines that the bean-approval gate did
not recognize as boilerplate. As a result `test_template_rejected`
failed on this branch (the unfilled template was wrongly classified as
"approvable"). Fix folded into this verification wave:
`foundry_app/services/bean_approval.py` now lists the new template
blockquote lines and example AC lines as placeholder/boilerplate. With
the fix, all 2270 tests pass.

This is the kind of cross-file regression that programmatic VDD will
catch automatically once beans use prefixed criteria — exactly the
motivation for BEAN-277.

**Bean's own ACs are legacy (unprefixed).** Per the spec the runner
classifies them as MANUAL and reports `PARTIAL`. The merge-bean gate
will accept this bean either via Tech-QA's manual sign-off (this
report) or by re-running `/vdd 277 --manual=pass`. The Notes section
in BEAN-277's bean.md may also serve as the override path documented
in the merge-bean skill.

**No gaps requiring rework.** The bean is ready for Team-Lead to
merge.
