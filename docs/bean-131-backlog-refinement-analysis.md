# Analysis: `/backlog-refinement` Command

**Bean:** BEAN-131 | **Date:** 2026-02-16 | **Analyst:** developer

---

## 1. Overview

The `/backlog-refinement` skill is the primary intake mechanism for converting raw user ideas into well-formed beans. It implements a 4-phase process: Analysis → Dialogue → Creation → Summary. The skill is owned by the Team Lead persona and depends on `/new-bean` for bean creation and on `_index.md` / `_bean-template.md` for backlog state.

**Skill file:** `.claude/skills/backlog-refinement/SKILL.md` (159 lines)

---

## 2. Phase-by-Phase Analysis

### Phase 1: Analysis (Steps 1–4)

**What it does:** Receives raw text, reads the existing backlog, identifies natural work boundaries, and drafts bean proposals using working titles (no IDs).

**Strengths:**
- Deferred ID assignment is well-designed — avoids collisions in multi-agent environments by using working titles until creation time.
- Work-unit identification criteria are comprehensive: separate features, infra vs. app concerns, dependencies, personas, independent deliverables.
- Explicit instruction to read `_index.md` for duplicate avoidance.

**Weaknesses:**
- No guidance on how to handle **extremely large inputs** (e.g., a 2000-word vision document). There's no chunking strategy or max-bean-count recommendation.
- The "initial priority guess" in step 4 has no heuristic guidance — the agent must infer priority from "context clues" without any rubric. Compare with `/backlog-consolidate` which provides detailed heuristics for its analysis checks.
- No instruction to read **Done beans** during analysis. The duplicate check only reads `_index.md` (titles and statuses) but doesn't compare against Done beans' Problem Statements. The `/backlog-consolidate` skill explicitly loads Done beans for reference (Check 6: Done Duplication). This means `/backlog-refinement` could create a bean that duplicates already-completed work.

### Phase 2: Dialogue (Steps 5–7)

**What it does:** Presents proposed beans to the user, asks clarifying questions in batches, iterates until user confirms.

**Strengths:**
- Question categories are well-structured: Priority, Scope, Dependencies, Missing context, Acceptance criteria, Splitting, Merging.
- Batch size guidance (2–4 questions at a time) prevents overwhelming the user.
- Clear iteration loop with explicit completion signals ("Looks good", "Yes, create those", etc.).
- The presentation format (numbered list with title, one-line description, priority) is scannable.

**Weaknesses:**
- No guidance on **maximum iteration rounds**. In theory, the dialogue could loop indefinitely if the user keeps refining. A soft limit (e.g., "after 3 rounds, present the current state and ask for final confirmation") would improve predictability.
- No instruction to **re-read `_index.md`** between dialogue iterations. If another agent creates beans during a long dialogue, the duplicate check from Phase 1 becomes stale. The `/backlog-consolidate` skill explicitly re-reads before every write; refinement should at least re-read before creation.
- Missing guidance on handling **user requests to add entirely new beans** during the dialogue (not just refine the existing proposals). The skill assumes the input is fixed and only refined — but users often think of new ideas during the conversation.
- No mention of the **Category** field (App/Process/Infra) during the dialogue. The draft proposals in step 4 include priority but not category. Category should be proposed and confirmed during dialogue since it affects `/long-run` filtering.

### Phase 3: Creation (Steps 8–11)

**What it does:** Creates each bean sequentially with deferred ID assignment, fixes cross-references, handles duplicates.

**Strengths:**
- Sequential creation with fresh `_index.md` reads is the correct approach for multi-agent safety. This matches the bean-workflow.md specification exactly.
- Cross-reference fixup pass (step 10) correctly handles the deferred-ID problem — beans that reference each other by title get updated to use actual IDs.
- Duplicate handling (step 11) with explicit user confirmation is the right UX.

**Weaknesses:**
- The skill says to create beans using steps described inline but **does not explicitly invoke `/new-bean`**. The description says "Creates a new bean" but the process describes the creation steps manually (re-read index, assign ID, create directory, write bean.md, append to index). This duplicates the `/new-bean` skill's process. Two possible issues:
  1. If `/new-bean` is updated (e.g., new fields added to template), `/backlog-refinement`'s inline creation steps won't pick up the change.
  2. The outputs table says "One or more `bean.md` files created via `/new-bean`" — but the process doesn't actually call `/new-bean`. This is a documentation inconsistency.
- **No rollback strategy.** If creation fails partway through a batch (e.g., 3 of 5 beans created, then an error), there's no guidance on cleanup. The `/backlog-consolidate` skill has a `ConcurrentEdit` error condition for this scenario; refinement has no equivalent.
- Step 10 (fix cross-references) says "do a single pass" but doesn't specify **which files** to scan. It should explicitly say: scan all bean.md files created in this batch.
- The dry run check (step 8) skips to step 11, but step 11 is the duplicate handling step. This means dry runs would still trigger duplicate warnings with "Create it anyway?" prompts. Dry runs should skip to step 12 (the summary) instead.

### Phase 4: Summary (Steps 12)

**What it does:** Presents a summary table of created beans with IDs, titles, priorities, and dependencies.

**Strengths:**
- Clean tabular format is easy to scan.
- Suggests running `/bean-status` as the next step.

**Weaknesses:**
- No mention of **what to do next** beyond `/bean-status`. For a batch of newly created Unapproved beans, the natural next step is `/review-beans` for the approval gate. This should be suggested.
- The summary doesn't include **Category** in the table columns, but Category is an important field for `/long-run` filtering.
- No summary of **how many questions were asked** or **how many iterations** the dialogue took. This would be useful for telemetry and workflow improvement.

---

## 3. Dependency Analysis

### Direct Dependencies

| Dependency | Used In | Assessment |
|-----------|---------|------------|
| `ai/beans/_index.md` | Steps 2, 9a, 9d | Correctly reads fresh before each write. Well-handled. |
| `ai/beans/_bean-template.md` | Step 9c (implicit) | Listed in Dependencies section but not mentioned in Process steps. The process describes filling fields directly without referencing the template read step from `/new-bean`. |
| `/new-bean` | Listed in Dependencies | **Not actually invoked in the process.** The Outputs table says "created via `/new-bean`" but the process steps describe manual creation. Inconsistency. |

### Interaction with Related Skills

| Skill | Relationship | Notes |
|-------|-------------|-------|
| `/backlog-consolidate` | Downstream consumer | Consolidation is meant to run after refinement to clean up duplicates and overlaps. Refinement should mention this as a suggested next step. |
| `/review-beans` | Downstream consumer | New Unapproved beans need review. Not mentioned in the summary phase. |
| `/long-run` | Downstream consumer | Only picks Approved beans. Refinement creates Unapproved beans — the approval gate sits between refinement and long-run. This chain is correct but not documented in the skill. |
| `/show-backlog` | Complementary | Shows the full backlog state. Mentioned indirectly via `/bean-status`. |

---

## 4. Edge Cases

| Edge Case | Current Handling | Risk |
|-----------|-----------------|------|
| Empty input | `EmptyInput` error condition defined | Low — properly handled |
| Single-sentence input producing one bean | No special handling | Low — works naturally, but the dialogue phase may be unnecessarily heavy for simple inputs |
| Very large input (20+ potential beans) | No chunking or limit guidance | Medium — could produce an unwieldy dialogue with too many proposals |
| User provides structured input (numbered list) | No special parsing guidance | Low — the agent can handle this naturally |
| Duplicate of a Done bean | Not detected (only checks `_index.md` titles) | **High — could create redundant work** |
| Concurrent refinement sessions | Deferred ID assignment handles this | Low — well-designed |
| User cancels mid-dialogue | `UserAbort` error condition defined | Low — properly handled |
| User cancels mid-creation (after some beans created) | **No rollback guidance** | Medium — partial state left behind |
| Bean references external system (Trello card, GitHub issue) | No guidance on linking to external sources | Low — Trello section defaults to `Source: Manual` |
| Input contains contradictory requirements | No specific handling in Analysis phase | Medium — should flag contradictions before creating beans |

---

## 5. Quality Criteria Assessment

The skill defines 7 quality criteria. Assessment of each:

| # | Criterion | Verifiable? | Gap? |
|---|-----------|------------|------|
| 1 | Non-trivial Problem Statement | Subjective — "non-trivial" is vague | Minor — could define minimum length or content requirement |
| 2 | At least 3 acceptance criteria per bean | Objective, countable | None |
| 3 | Scope distinguishes In/Out of Scope | Structural check | None |
| 4 | Dependencies noted in Notes sections | Checkable | None |
| 5 | No duplicates without approval | Process check | Gap — only checks against `_index.md` titles, not Done beans' Problem Statements |
| 6 | At least one clarifying question before creating | Countable | None |
| 7 | Sequential IDs, no collisions | Objective | None |

**Missing quality criteria:**
- Every bean should have a **Category** assigned (App/Process/Infra).
- Every bean's **Goal** section should be filled in (not just Problem Statement).
- Cross-references between beans in the same batch should be verified after the fixup pass.

---

## 6. Comparison with `/backlog-consolidate`

Both skills operate on the backlog and follow the same 4-phase pattern (Analysis → Dialogue → Execution → Summary). Comparing their design reveals patterns and inconsistencies:

| Aspect | Refinement | Consolidation | Better? |
|--------|-----------|---------------|---------|
| Analysis heuristics | Implicit ("look for natural boundaries") | Explicit (6 named checks with severity levels, evidence requirements) | Consolidation — more structured and repeatable |
| Multi-agent safety | Deferred IDs, fresh reads before creation | Re-read before every write, `ConcurrentEdit` error | Consolidation — more defensive |
| Dialogue batching | 2–4 questions at a time | 2–4 findings at a time | Equivalent |
| Iteration control | "Continue until user confirms" (no limit) | "Re-check after changes, repeat until clean" (bounded by finding count) | Consolidation — naturally bounded |
| Dry run support | Yes (step 8) | Yes (step 11) | Equivalent |
| Done-bean awareness | No | Yes (Check 6) | Consolidation — prevents done duplication |
| Error handling | 4 error conditions | 4 error conditions | Equivalent, but refinement lacks `ConcurrentEdit` |
| Summary next steps | Only `/bean-status` | Context-dependent suggestions | Consolidation — more helpful |

**Key takeaway:** `/backlog-consolidate` was written after `/backlog-refinement` and incorporates lessons learned. Several patterns from consolidation should be backported to refinement.

---

## 7. Improvement Recommendations

### Priority: High

1. **Add Done-bean duplicate detection.** Before proposing new beans, read Done beans' Problem Statements and Goals. Flag when a proposed bean substantially overlaps completed work. This prevents creating redundant beans that `/backlog-consolidate` would later catch.

2. **Delegate creation to `/new-bean`.** Instead of duplicating the creation process inline, explicitly invoke `/new-bean` for each bean. This ensures consistency when `/new-bean` is updated and eliminates the documentation inconsistency in the Outputs table.

3. **Add Category to the workflow.** Include Category (App/Process/Infra) in step 4 (draft proposals), step 5 (presentation format), and step 12 (summary table). This is important for downstream filtering by `/long-run`.

4. **Fix dry-run skip target.** Step 8 says "skip creation and go to step 11" but step 11 is duplicate handling. It should skip to step 12 (Summary). Alternatively, renumber so summary is immediately after the dry-run check.

### Priority: Medium

5. **Add a `ConcurrentEdit` error condition.** Match the pattern from `/backlog-consolidate`: if `_index.md` has been modified by another agent between reads, report the conflict and ask the user how to proceed.

6. **Suggest `/review-beans` and `/backlog-consolidate` as next steps.** After creating Unapproved beans, the natural workflow is: review → approve → pick. The summary should guide users toward this.

7. **Add heuristics for priority guessing.** Provide a rubric similar to `/backlog-consolidate`'s analysis heuristics. For example: "High = blocks other work or addresses a user-facing issue; Medium = improves existing functionality; Low = nice-to-have or cosmetic."

8. **Add partial-creation rollback guidance.** If creation fails after N of M beans are created, the skill should state: "Created beans remain valid. Report the error and resume creation from the next bean."

### Priority: Low

9. **Add Category to quality criteria.** "Every created bean has a Category field set to App, Process, or Infra."

10. **Add a soft iteration limit.** After 3 dialogue rounds, present the current proposal as final and ask for explicit confirmation or explicit continuation.

11. **Support additive ideas during dialogue.** Add guidance: "If the user introduces a new idea not in the original input, add it as an additional proposed bean and re-present the updated list."

12. **Mention template read in process steps.** Step 9c should explicitly say "Read `_bean-template.md` and populate fields" rather than just listing the fields to fill.

---

## 8. Summary

The `/backlog-refinement` skill is well-structured and handles the core workflow correctly. Its strongest aspects are the deferred ID assignment for multi-agent safety and the iterative dialogue phase. The most significant gaps are: (1) no detection of duplicates against Done beans, (2) inline creation that duplicates `/new-bean` instead of delegating to it, and (3) missing Category field throughout the workflow. These gaps represent concrete improvement opportunities for future Process beans.
