# BEAN-008: Feature Branch Workflow — QA Report

**Author:** Tech-QA | **Date:** 2026-02-07 | **Bean:** BEAN-008

## Verdict: GO

## Test Results

- **Total tests:** N/A (no Python source — markdown command/skill/workflow updates only)
- **Lint:** N/A
- **Files modified:** 5 existing files updated

## Traceability Matrix

| Bean AC | Evidence | Status |
|---------|----------|--------|
| `/pick-bean` skill updated to create feature branch | Skill step 8: creates `bean/BEAN-NNN-<slug>`. Command step 5 matches. `--no-branch` opt-out available. | PASS |
| `/long-run` skill updated with feature branches per bean | Skill step 8 (Phase 3): creates branch. Steps 15-16: commit on branch, return to main. Command steps 5, 10-11 match. | PASS |
| All bean work committed on feature branch, not main | Long-run skill step 15: "commit goes on the branch". Step 16: return to main. Command step 10 matches. | PASS |
| Branch naming convention documented in `bean-workflow.md` | New "Branch Strategy" section with naming convention, lifecycle, when-to/when-not-to branch guidance | PASS |
| Command/skill format matches existing patterns | All sections preserved, numbering updated, no missing sections | PASS |
| Team Lead agent updated if needed | Not needed — `/pick-bean` and `/long-run` already referenced in agent; branch behavior is internal to those skills | PASS |

## Consistency Check

| Pattern | bean-workflow.md | pick-bean cmd | pick-bean skill | long-run cmd | long-run skill |
|---------|------------------|---------------|-----------------|--------------|----------------|
| Branch name: `bean/BEAN-NNN-<slug>` | Yes | Yes | Yes | Yes | Yes |
| Created at `In Progress` | Yes | Yes (with --start) | Yes (step 8) | Yes (step 5) | Yes (step 8) |
| Opt-out: `--no-branch` | Yes (When NOT to Branch) | Yes | Yes | N/A (always branches) | N/A |
| Return to main after close | N/A | N/A | N/A | Yes (step 11) | Yes (step 16) |

No contradictions found. All files use the same naming convention and lifecycle.

## Additional Verification

- `bean-workflow.md` "When NOT to Branch" section provides escape hatch for doc-only beans
- `/pick-bean` only branches on `--start` (not plain pick) — correct, since `Picked` means "reviewing" not "working"
- `/long-run` always creates branches — correct, since autonomous mode should always isolate
- Step numbering in all updated files is sequential with no gaps
- No placeholder text remains

## Recommendation

**GO** — All 6 acceptance criteria met. Branch naming convention is consistent across all 5 updated files. No contradictions between command, skill, and workflow documentation.
