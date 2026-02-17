# BEAN-134: Backlog Consolidate Command — Analysis

**Bean:** BEAN-134 — Analyze Backlog Consolidate Command
**Author:** Developer (analysis), Team Lead (review)
**Date:** 2026-02-16
**Skill File:** `.claude/skills/backlog-consolidate/SKILL.md`
**Command File:** `.claude/commands/backlog-consolidate.md`

---

## 1. Executive Summary

The `/backlog-consolidate` command is the post-refinement cleanup tool that detects and resolves duplicates, scope overlaps, contradictions, missing dependencies, and merge opportunities across beans. It is designed to run after parallel `/backlog-refinement` sessions create batches of new beans that may overlap.

**Overall Assessment:** The skill is **well-designed and comprehensive**. It has a clear 4-phase structure, 8 distinct analysis checks with severity levels, and robust concurrency-safety patterns. It is the most structurally sophisticated skill in the process toolkit. However, several gaps and edge cases could be addressed to improve reliability and user experience.

**Key Strengths:** Severity-based prioritization, evidence-based findings, stale-state protection, iterative re-check after changes.

**Key Weaknesses:** No persistence of findings, high token cost for large backlogs, limited structural validation of beans, no undo mechanism.

---

## 2. Architecture Overview

### 2.1 Four-Phase Structure

| Phase | Purpose | Steps | Interactive? |
|-------|---------|-------|-------------|
| **Analysis** | Read backlog, load beans, run 8 checks | 1–7 | No |
| **Dialogue** | Present findings, get user decisions | 8–10 | Yes |
| **Execution** | Apply agreed changes to files | 11–15 | No |
| **Summary** | Report changes and suggest next steps | 16–17 | No |

This is a solid phase decomposition. The Analysis phase is pure read, the Dialogue phase is pure interaction, and Execution is pure write. This separation makes each phase independently testable in principle and prevents premature mutations.

### 2.2 Analysis Checks

| # | Check | Severity | Comparison Scope | Quality |
|---|-------|----------|-----------------|---------|
| 1 | Duplicate Detection | Critical | Target × Target | Strong |
| 2 | Scope Overlap | High | Target × Target | Strong |
| 3 | Contradictions | Critical | Target × Target | Good |
| 4 | Missing Dependencies | High | Target × Target | Good |
| 5 | Merge Candidates | Medium | Target × Target | Good |
| 6 | Done Duplication | High | Target × Done | Strong |
| 7 | Dependency Cycles | High | Graph analysis | Good |
| 8 | Priority Inconsistencies | Medium | Graph + metadata | Good |

### 2.3 Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| `/backlog-refinement` | **Upstream** — creates the beans that `/backlog-consolidate` cleans up |
| `/show-backlog` | **Complementary** — displays backlog state; consolidate modifies it |
| `/new-bean` | **Downstream** — consolidate may call merged-bean creation patterns |
| `/long-run` | **Downstream** — picks approved beans after consolidation cleans up |

---

## 3. Phase-by-Phase Analysis

### 3.1 Phase 1: Analysis (Steps 1–7)

**Strengths:**

- **Comprehensive bean loading** — Step 3 extracts all relevant sections (Problem Statement, Goal, Scope, Acceptance Criteria, Notes, Priority, Category). This gives each check enough context to reason well.
- **Done-bean reference set** — Step 4 loads Done beans but only reads the sections needed (Problem Statement, Goal, Scope), reducing token waste for the reference set.
- **Clear check definitions** — Each of the 8 checks has a defined severity, comparison methodology, and expected evidence format. This makes the agent's task unambiguous.
- **Heuristics section** — The dedicated "Analysis Heuristics" section at the bottom provides concrete guidance for the LLM on how to apply judgment (word-overlap patterns, incidental vs substantive overlap, opposing verbs).

**Weaknesses:**

- **No early termination on empty results** — Step 2 validates target count (zero or one), but there is no validation that the bean files actually exist on disk. If a bean is listed in `_index.md` but its directory is missing (e.g., deleted manually), the skill would fail mid-analysis with an unclear error.
- **No size/complexity estimate** — For large backlogs (20+ target beans), the pairwise comparison produces O(n²) pairs. With 20 beans, that is 190 pairs × 5 pairwise checks = 950 comparisons. The skill does not warn the user or suggest narrowing the filter when the target set is large.
- **Heuristics are prose-only** — The duplicate detection heuristic says "compare Problem Statements and Goals word by word" and "look for high overlap in key nouns and verbs," but provides no threshold or scoring rubric. The agent must use pure judgment, which may produce inconsistent results across sessions.
- **No progress indication** — For a potentially long analysis phase, there is no guidance on providing incremental progress feedback to the user. The user sees nothing until all 8 checks are complete.

**Recommendations:**

1. **Add file-existence validation** — After loading the target list from `_index.md`, verify each bean directory and `bean.md` file exists. Report missing beans as a pre-check finding rather than failing mid-analysis.
2. **Add target-count warning** — If target beans > 15, warn the user about analysis time and suggest narrowing with `--status` or analyzing in batches.
3. **Add incremental progress** — After completing each check, emit a brief status line (e.g., "Check 1/8: Duplicate Detection — 2 issues found").

### 3.2 Phase 2: Dialogue (Steps 8–10)

**Strengths:**

- **Severity-ordered presentation** — Critical findings are shown first, ensuring the most important issues get addressed before dialogue fatigue sets in.
- **Evidence-based format** — Every finding must include "specific quotes from both beans as evidence." This prevents vague or unsubstantiated flags.
- **Batched questions** — Step 9 processes findings in batches of 2–4, which matches the backlog-refinement pattern and prevents overwhelming the user.
- **Typed action options** — The options table (Step 9) maps each finding type to 3–4 specific actions. This constrains the dialogue to actionable choices rather than open-ended discussion.
- **Re-check loop** — Step 10 explicitly re-checks for new issues after each round of decisions. This catches cascading problems (e.g., merging two beans creates a new scope overlap with a third).

**Weaknesses:**

- **No "accept all" shortcut** — For backlogs with many findings (10+), the user must respond to each batch individually. There is no option to "accept all recommendations" or "skip all Medium findings."
- **No finding persistence** — If the user aborts mid-dialogue or the session crashes, all analysis is lost. The findings are only in the agent's context window, not saved to disk.
- **Batch size is fixed at 2–4** — The skill specifies "batches of 2-4" but doesn't account for related findings that should be decided together. For example, if BEAN-A and BEAN-B are flagged as duplicates, and BEAN-B and BEAN-C are also flagged as duplicates, those findings are related and should be presented together regardless of batch boundaries.
- **No confidence level** — Some findings are clear-cut (identical Problem Statements) while others are judgment calls (marginal scope overlap). The skill doesn't guide the agent to express confidence, which would help users decide faster.

**Recommendations:**

4. **Add bulk action shortcuts** — Allow "Accept all Critical recommendations" or "Skip all Medium findings" for large result sets.
5. **Persist findings to disk** — Write findings to a temporary file (e.g., `ai/beans/_consolidation-report.md`) before starting dialogue. This survives session crashes and creates an audit trail.
6. **Group related findings** — When two findings share a bean (e.g., BEAN-B appears in both a duplicate finding and a scope overlap finding), present them together regardless of severity ordering.
7. **Add confidence indicators** — Guide the agent to mark each finding as "High confidence" (strong evidence) or "Moderate confidence" (judgment call) to help users triage faster.

### 3.3 Phase 3: Execution (Steps 11–15)

**Strengths:**

- **Stale-state protection** — The bold instruction "Before every write operation: Re-read `ai/beans/_index.md` to get the latest state" is excellent concurrency safety. This prevents overwriting changes made by parallel agents.
- **Detailed operation specs** — Each of the 6 mutation types (merge, delete, add dependency, rewrite scope, reorder priority, mark deferred) has a clear step-by-step procedure. Nothing is left to interpretation.
- **Cross-reference cleanup** — Step 13 scans all remaining beans for references to deleted or merged bean IDs and updates them. This prevents dangling references.
- **Post-change verification** — Steps 14 (cycle check) and 15 (index consistency) verify the backlog is in a valid state after all changes.

**Weaknesses:**

- **No rollback/undo mechanism** — If the agent makes a mistake during execution (e.g., merges the wrong beans), there is no way to undo short of reverting the git commit. The skill should recommend committing before execution starts.
- **Sequential execution only** — All changes are applied sequentially, which is correct for safety but could be slow for large change sets. This is acceptable but worth noting.
- **"Mark deferred" operation is undocumented in dialogue** — Step 12 includes a "Mark deferred" operation, but the dialogue options in Step 9 don't include "Defer" as a choice for any finding type. This operation exists in the execution spec but has no path to reach it.
- **Merge algorithm lacks conflict handling** — The merge procedure (Step 12, "Merge two beans") says to "union of In Scope items" and "union of all Acceptance Criteria (deduplicate)." But if two beans have contradictory In Scope items (one says "modify generator" and the other says "leave generator unchanged"), the merge procedure doesn't address how to resolve the contradiction — it just unions them.
- **No validation of merged result** — After merging two beans, the skill doesn't verify that the merged bean is well-formed (e.g., has at least 3 acceptance criteria, has a non-trivial Problem Statement). The quality criteria from `/backlog-refinement` are not applied to merged beans.

**Recommendations:**

8. **Add pre-execution checkpoint** — Before applying any changes, recommend or require a git commit so changes can be reverted if needed.
9. **Add "Defer" to dialogue options** — Include "Defer one or both beans" as an option for Merge Candidates and Priority Inconsistencies.
10. **Handle merge contradictions** — When merging beans that have conflicting scope items, flag the conflict and ask the user which version to keep rather than blindly unioning.
11. **Validate merged beans** — After merging, verify the result meets the same quality criteria that `/backlog-refinement` enforces on new beans (minimum 3 acceptance criteria, non-trivial Problem Statement, etc.).

### 3.4 Phase 4: Summary (Steps 16–17)

**Strengths:**

- **Clear change log format** — The summary provides concrete counts (merged, deleted, dependencies added, scopes rewritten) and the before/after bean count. This gives the user a clear picture of impact.
- **Dry run support** — The skill correctly handles dry-run mode by prefixing the summary and skipping execution.
- **Context-aware next steps** — Step 17 suggests different follow-up actions based on what was done (review merged beans, check dependency graph, run again).

**Weaknesses:**

- **No "before and after" comparison** — The summary shows counts but doesn't show the actual final state of modified beans. The user must manually open each bean to verify the result.
- **No summary persistence** — The change log is console output only. For audit purposes, it would be useful to append the summary to a log file.

**Recommendations:**

12. **Include a mini-diff for each modified bean** — Show the key changes (e.g., "BEAN-072: merged with BEAN-075, added 3 acceptance criteria, new title: 'User Authentication System'").
13. **Persist the summary** — Append the consolidation summary to a log file (e.g., `ai/outputs/team-lead/consolidation-log.md`) for historical tracking.

---

## 4. Cross-Cutting Concerns

### 4.1 Concurrency Safety

**Rating: Strong**

The skill explicitly addresses concurrent access:
- Re-read `_index.md` before every write (Step 12 preamble)
- `ConcurrentEdit` error condition with clear resolution (abort, re-read, report)
- Claim protocol awareness from bean-workflow.md

**Gap:** The skill only re-reads `_index.md` before writes, but doesn't re-read individual `bean.md` files before modifying them. If another agent modifies a bean's Notes section between analysis and execution, the write could overwrite their changes.

**Recommendation 14:** Re-read the specific `bean.md` before each write operation, not just `_index.md`.

### 4.2 Token Efficiency

**Rating: Moderate concern**

The skill requires loading full content for all target beans plus Done beans. For the current backlog:
- 130 Done beans × ~50 lines each = ~6,500 lines of reference content
- 10 target beans × ~70 lines each = ~700 lines of target content
- Total context needed: ~7,200 lines plus the skill itself (~270 lines)

This is within context window limits but represents significant token usage. For future backlogs with 200+ Done beans, this could become a bottleneck.

**Recommendation 15:** For the Done-bean reference set, only load Problem Statement + Goal (as already specified in Step 4), and consider a two-pass approach: first pass loads only titles and one-line summaries, second pass loads full details only for beans that look like potential matches.

### 4.3 Error Handling

**Rating: Good**

Four error conditions are defined: `NoTargetBeans`, `SingleBean`, `ConcurrentEdit`, `UserAbort`. These cover the main failure modes.

**Gaps:**
- No handling for malformed bean files (missing sections, corrupt markdown)
- No handling for bean files that exist in `_index.md` but not on disk
- No handling for partial execution failure (e.g., successfully merged 2 beans but failed on the 3rd)

**Recommendation 16:** Add error conditions for `MalformedBean` (missing required sections) and `PartialExecutionFailure` (some changes applied, some failed — report what was done and what remains).

### 4.4 Command File Consistency

The command file (`.claude/commands/backlog-consolidate.md`) and skill file (`.claude/skills/backlog-consolidate/SKILL.md`) are **well-aligned**. The command file is a concise summary that correctly reflects the skill's process. No contradictions found.

One minor discrepancy: the command file's error handling section says `UserAbort` results in "No changes applied," but the skill file (Step 12) correctly notes that "Changes already applied remain (they were individually approved)." The command file should be updated to match.

---

## 5. Check-by-Check Evaluation

### Check 1: Duplicate Detection (Critical)

**Quality: Strong**

The heuristic guidance is clear: compare Problem Statements and Goals, look for key noun/verb overlap. The requirement for "specific quotes from both beans as evidence" ensures transparency.

**Edge case:** Two beans that solve the same problem but via completely different approaches (e.g., "Add caching via Redis" vs "Add caching via SQLite"). These share the problem but not the solution. The skill should flag these as potential duplicates but note the different approaches.

### Check 2: Scope Overlap (High)

**Quality: Strong**

The distinction between "incidental overlap" and "substantive overlap" is the key design decision and it's well-articulated. The example (both touch `_index.md` = incidental; both modify `generator.py` for the same purpose = substantive) provides clear guidance.

**Edge case:** Two beans that touch the same file but different sections (e.g., both modify `main_window.py` — one adds a sidebar method, the other adds a toolbar). This is structural overlap but not necessarily a problem. The skill should consider whether the modifications would conflict at the code level.

### Check 3: Contradictions (Critical)

**Quality: Good**

The opposing-verb patterns ("add X" vs "remove X", "consolidate" vs "split") are well-chosen. Checking both Acceptance Criteria and Scope sections covers the main locations for conflicting intent.

**Edge case:** Temporal contradictions — Bean A says "remove feature X" and Bean B says "enhance feature X," but Bean A is meant to run first (remove the old version) and Bean B creates the replacement. Without understanding execution order, this looks like a contradiction but is actually a planned sequence.

**Recommendation 17:** When flagging contradictions, check if the beans have an existing dependency relationship. If Bean A is noted as a prerequisite to Bean B, the "contradiction" may be intentional sequencing rather than a conflict.

### Check 4: Missing Dependencies (High)

**Quality: Good**

The create/modify → read/use pattern is the right heuristic. Checking both directions for each pair is thorough.

**Edge case:** Transitive dependencies — Bean A creates X, Bean B modifies X, Bean C reads X. The skill would flag A→C and B→C but might not realize that B→C implies A→B→C.

### Check 5: Merge Candidates (Medium)

**Quality: Good**

The "8 acceptance criteria" threshold for combined scope is a practical heuristic. The positive and negative examples (good merge: sequential steps; poor merge: different categories) provide clear guidance.

**Edge case:** Two beans that are individually small but, when merged, would require two different personas (e.g., one is a UI change and the other is a backend change). The merge would be technically small but organizationally awkward.

### Check 6: Done Duplication (High)

**Quality: Strong**

Comparing target beans against the full Done set is thorough. The instruction to distinguish "extends Done work" from "re-solves the same problem" prevents false positives on follow-up work.

**Edge case:** A Done bean that was only partially successful (marked Done but with known limitations noted in its bean.md). A new bean addressing those limitations would look like a duplicate but is actually a follow-up.

### Check 7: Dependency Cycles (High)

**Quality: Good**

Graph-based cycle detection is the correct approach. The evidence format (full cycle path) is clear.

**Limitation:** The check only looks at "existing dependency notes," which are freeform text in the Notes section. There is no structured dependency field in the bean template, so the agent must parse prose like "Depends on BEAN-072" from the Notes section. This is fragile — variations like "Requires BEAN-072 to be done first" or "Blocked by BEAN-072" might be missed.

**Recommendation 18:** Define a standard dependency notation format (e.g., always use "Depends on BEAN-NNN" as the canonical form) and document it in the bean template. Alternatively, add a structured `Dependencies` field to the bean template.

### Check 8: Priority Inconsistencies (Medium)

**Quality: Good**

The specific scenario (High depends on unscheduled Low) is well-defined. The recommendation to promote the low bean is practical.

**Edge case:** Priority inconsistencies across status boundaries — a High-priority Approved bean depends on a Low-priority Done bean that was only partially completed. The skill wouldn't catch this because Done beans are only used in Check 6.

---

## 6. Comparison with Related Skills

### vs. `/backlog-refinement`

| Dimension | Backlog Refinement | Backlog Consolidate |
|-----------|-------------------|-------------------|
| **Input** | Raw user text | Existing beans |
| **Creates** | New beans | Modifies/deletes existing beans |
| **Dialogue** | Clarifying questions | Action decisions |
| **Risk** | Low (only adds) | High (deletes, merges, rewrites) |
| **Concurrency** | Sequential bean creation | Re-read before every write |
| **Phase count** | 4 | 4 |
| **Quality criteria** | 7 items | 8 items |

The consolidation skill is appropriately more cautious than refinement, given its destructive potential. The re-read-before-write pattern is not present in refinement (where it should also be used for `_index.md` writes).

### Design Pattern Consistency

Both skills follow the same 4-phase pattern: Analysis → Dialogue → Execution → Summary. Both use the same error-handling table format and the same batched-question dialogue approach. This consistency is a strength — users who learn one skill's interaction pattern can apply it to the other.

---

## 7. Summary of Recommendations

### High Priority

| # | Recommendation | Rationale |
|---|---------------|-----------|
| 5 | Persist findings to disk before dialogue | Session crash loses all analysis work |
| 8 | Add pre-execution git checkpoint | Destructive operations with no undo |
| 10 | Handle merge contradictions explicitly | Blind union of conflicting scope items |
| 14 | Re-read bean.md before each write, not just _index.md | Concurrency gap |
| 16 | Add MalformedBean and PartialExecutionFailure errors | Missing error conditions |

### Medium Priority

| # | Recommendation | Rationale |
|---|---------------|-----------|
| 1 | Validate bean file existence during load | Silent failure on missing files |
| 2 | Warn on large target sets (>15 beans) | O(n²) comparison cost |
| 4 | Add bulk action shortcuts | Dialogue fatigue on large finding sets |
| 6 | Group related findings across severity levels | Connected decisions split across batches |
| 9 | Add "Defer" to dialogue options | Execution spec has it, dialogue doesn't |
| 11 | Validate merged beans against quality criteria | Merged beans may not meet minimum standards |
| 17 | Check existing dependency before flagging contradiction | Intentional sequencing misread as conflict |
| 18 | Standardize dependency notation format | Fragile prose parsing for cycle detection |

### Low Priority

| # | Recommendation | Rationale |
|---|---------------|-----------|
| 3 | Add incremental progress during analysis | Better UX for long analysis runs |
| 7 | Add confidence indicators to findings | Helps users triage judgment calls |
| 12 | Include mini-diff in summary for each modified bean | Better post-change visibility |
| 13 | Persist consolidation summary to log file | Audit trail |
| 15 | Two-pass Done-bean loading for token efficiency | Future-proofing for large backlogs |

---

## 8. Conclusion

The `/backlog-consolidate` command is a well-structured, thorough post-refinement cleanup tool. Its 8 analysis checks cover the most important backlog hygiene issues, and its concurrency-safety patterns are ahead of the other skills. The 4-phase architecture (read, discuss, write, report) is clean and testable.

The primary areas for improvement are:

1. **Resilience** — Adding file-existence validation, error handling for malformed beans, and a pre-execution checkpoint would make the skill more robust against real-world messiness.
2. **Usability** — Persisting findings, adding bulk actions, and grouping related findings would improve the experience for large backlogs with many issues.
3. **Correctness** — Handling merge contradictions, validating merged beans, and re-reading `bean.md` files before writes would prevent subtle data-loss scenarios.

None of these gaps are blockers for current use. The skill works well for its designed scenario (cleaning up 15–20 beans after parallel refinement sessions). The recommendations would primarily benefit future use at larger scale or in higher-concurrency environments.
