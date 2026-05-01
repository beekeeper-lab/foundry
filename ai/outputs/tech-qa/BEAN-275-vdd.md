# BEAN-275 — Verification & Defect Detection (VDD) Report

**Bean:** Resolve Acceptance Criteria & ADR Boundary Ownership
**Branch:** `bean/BEAN-275-acceptance-criteria-adr-ownership`
**Verifier:** Tech-QA (Task 03)
**Verdict:** **All AC Pass** — bean is ready to mark Done.

## Gaps

None. Every Acceptance Criterion has concrete passing-test or
file-content evidence below.

> Note: a side-effect regression in `test_bean_approval::test_template_rejected`
> surfaced when Task 02 added the new `> Authored by:` blockquote to
> `ai/beans/_bean-template.md` (the AC subnote made the AC section look
> "filled in" to the approval gate). Fixed in this task by adding the
> subnote string to `_PLACEHOLDER_BODY_LINES` in
> `foundry_app/services/bean_approval.py`. Full suite is green
> (2253 passed) with the fix in place.

## Acceptance Criteria Sweep

| # | AC text | Status | Evidence |
|---|---------|--------|----------|
| 1 | All 5 core persona files (library + Foundry kit copies) have a "Scope Boundaries" subsection covering both AC ownership and the ADR/dev-decision rule as relevant to that role. | Pass | `tests/test_scope_boundaries_partition.py::TestScopeBoundariesPresent::test_library_persona_has_subsection` (5 parametrized cases) and `::test_kit_agent_has_subsection` (5 cases) — all 10 pass. Verified files: `ai-team-library/personas/{ba,architect,developer,tech-qa,team-lead}/persona.md` and `.claude/shared/agents/{ba,architect,developer,tech-qa,team-lead}.md`. Tech-QA library file uses `## Scope Boundaries (AC and ADR/dev-decision)` to coexist with the pre-existing CQR-partition section. |
| 2 | Team-Lead orchestration rules name the AC owner per wave configuration. | Pass | `ai-team-library/personas/team-lead/persona.md` (under `## Orchestration Rules`) and `.claude/shared/agents/team-lead.md` (lines 292-310) both contain the rule paragraphs "Acceptance-criteria author per wave configuration" and "ADR-threshold escalation path". Asserted indirectly by `test_team_lead_owns_by_default` (wording "by default") and by the partition tests that confirm Team-Lead's Owns block claims `acceptance-criteria`. |
| 3 | Bean template AC section heading names the author. | Pass | `tests/test_scope_boundaries_partition.py::TestBeanTemplateSubnote::test_template_has_authored_by_blockquote` passes. Direct read of `ai/beans/_bean-template.md` line 35: `> Authored by: BA (when activated) \| Team-Lead (default)` immediately under `## Acceptance Criteria`. |
| 4 | A grep of all 5 persona files for "acceptance criteria" finds no language that contradicts the ownership rule. | Pass | `tests/test_scope_boundaries_partition.py::TestNoContradictions::test_no_forbidden_phrase_in_any_file` passes — sweeps all 10 files (library + kit) for 12 forbidden phrases such as "developer writes acceptance criteria", "tech-qa authors acceptance criteria", "architect defines acceptance criteria"; zero hits. |
| 5 | Tests verify the Scope Boundaries subsections exist and partition cleanly (no overlap, no gap). | Pass | `tests/test_scope_boundaries_partition.py::TestPartitionCleanliness` — 8 passing tests: `test_role_only_claims_allowed_artifacts` (5 parametrized roles), `test_acceptance_criteria_authors_are_exactly_ba_and_team_lead`, `test_adr_author_is_exactly_architect`, `test_dev_decision_author_is_exactly_developer`. Confirms AC authorship is exactly `{ba, team-lead}`, ADR exactly `{architect}`, dev-decision exactly `{developer}`. |
| 6 | All tests pass (`uv run pytest`). | Pass | Final line: `2253 passed, 4 warnings in 11.96s`. 36 new tests in `test_scope_boundaries_partition.py` plus 1 module-modification fix to `test_bean_approval.py`'s template fixture (no test change required — the bean_approval source was updated to recognize the new template line as placeholder). |
| 7 | Lint clean (`uv run ruff check foundry_app/`). | Pass | Final line: `All checks passed!`. |

## Implementation Notes for Team-Lead

- **Files added:** `tests/test_scope_boundaries_partition.py` (36 tests, ~330 lines).
- **Files modified:** `foundry_app/services/bean_approval.py` — added the
  Authored-by subnote to `_PLACEHOLDER_BODY_LINES` so the approval gate
  still rejects the unfilled template. This was necessary because the
  Task 02 template change otherwise made the bare template pass the AC
  content check (regression caught by `test_template_rejected`).
- **Files NOT modified:** the five library persona files, the five kit
  agent files, the bean template, and the BA policy text were already in
  place before Task 03 started (Task 02 produced them).
- **Test coverage breakdown:**
  - `TestScopeBoundariesPresent` — 10 cases (verification points 1, 2)
  - `TestAcceptanceCriteriaOwnershipRule` — 10 cases (verification point 3)
  - `TestAdrThresholdRule` — 6 cases (verification point 4)
  - `TestNoContradictions` — 1 case (verification point 5)
  - `TestBeanTemplateSubnote` — 1 case (verification point 6)
  - `TestPartitionCleanliness` — 8 cases (verification point 7)

## Recommendation

Mark BEAN-275 **Done**. All seven AC pass with concrete test or file
evidence; full suite (2253 tests) is green; lint is clean. The
side-effect fix to `bean_approval.py` is small and well-scoped — the
new test file pins the template subnote in place so the regression
cannot recur silently.
