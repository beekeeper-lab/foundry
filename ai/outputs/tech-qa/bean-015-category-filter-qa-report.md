# QA Report: BEAN-015 — Long Run Category Filter

| Field | Value |
|-------|-------|
| **Bean** | BEAN-015 |
| **Reviewed By** | tech-qa |
| **Date** | 2026-02-07 |
| **Verdict** | GO |

## Acceptance Criteria Trace

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `/long-run --category Process` processes only Process beans | PASS | Skill Phase 1 step 2: "If `category` is provided, further filter to only beans whose Category column matches (case-insensitive)." |
| 2 | `/long-run --category App` processes only App beans | PASS | Same filtering logic applies to all category values |
| 3 | `/long-run --category Infra` processes only Infra beans | PASS | Same filtering logic applies to all category values |
| 4 | Category matching is case-insensitive | PASS | Skill input description: "Case-insensitive." Command: "case-insensitive" in flag description. |
| 5 | Without `--category`, all actionable beans processed | PASS | Skill: "If `category` is provided, further filter..." — conditional, no change when absent |
| 6 | `--fast 3 --category Process` works in parallel | PASS | Skill Parallel Phase 2 step 2: "Apply `category` filter if provided." Command example shows `--fast 3 --category Infra`. |
| 7 | Announcement shows category filter when active | PASS | Skill step 6: "If a category filter is active, include it in the header: `[Category: Process]`." |
| 8 | No matching beans reports cleanly | PASS | Skill step 3: "If category is active, mention it: 'No actionable beans matching category: Process.'" |
| 9 | Skill documents new input | PASS | `category` row added to Inputs table with type, required, description |
| 10 | Command includes `--category` flag | PASS | Usage, Options table, and Examples all include `--category` |
| 11 | Tests pass | PASS | No Python code changes — pass-through |
| 12 | Lint clean | PASS | No Python code changes — pass-through |

## Consistency Check

| Check | Result |
|-------|--------|
| Command ↔ Skill consistency | PASS — Both describe category as optional, case-insensitive, App/Process/Infra |
| Sequential + parallel both filtered | PASS — Phase 1 step 2 and Parallel Phase 2 step 2 both apply filter |
| No regression | PASS — Filter is conditional; absent category = all beans (unchanged behavior) |

## Issues Found

None.

## Recommendation

**GO** — All 12 acceptance criteria met. Category filtering is consistent across sequential and parallel modes with no regression to default behavior.
