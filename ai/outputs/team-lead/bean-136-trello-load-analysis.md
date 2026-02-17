# Analysis: `/trello-load` Command

**Bean:** BEAN-136 | **Date:** 2026-02-16 | **Analyst:** developer

---

## 1. Overview

The `/trello-load` skill is the automated bridge between Trello's Sprint_Backlog and the bean system. It runs fully non-interactively — connecting to Trello via MCP, pulling cards from a designated list, creating well-formed beans with Approved status, and moving processed cards to In_Progress. This makes it suitable for cron jobs and `/long-run` pipelines.

**Skill file:** `.claude/skills/trello-load/SKILL.md` (252 lines, 5 phases, 16 steps)

**Key differentiator from `/backlog-refinement`:** This skill is entirely non-interactive. It bypasses the dialogue phase, creating beans directly from card content without user clarification. This is by design — cards in Sprint_Backlog are considered pre-curated and pre-approved.

---

## 2. Phase-by-Phase Analysis

### Phase 1: Board Selection (Steps 1–3)

**What it does:** Verifies Trello MCP connectivity, resolves the target board (explicit ID, project-name match, or fallback to first board), and sets the active board.

**Strengths:**
- Three-tier board resolution is well-designed: explicit → name match → fallback. This covers both automated use (explicit ID) and discovery-based use (auto-detect).
- Health check first is defensive and correct — fails fast before any state-changing operations.
- Logging which board was selected and why provides auditability.

**Weaknesses:**
- The fallback to "first board returned" (strategy 2c) is risky. If the user has multiple boards, picking the first one arbitrarily could process cards from the wrong project. A safer approach would be to stop with an error listing available boards and asking the user to specify `--board`.
- No validation that the selected board is actually the correct one beyond name matching. There's no confirmation step even when falling back to the first board.
- The project directory name match assumes the Trello board name matches the directory name. This is fragile — common mismatches include: casing differences (handled), but also abbreviations ("Foundry App" vs "foundry"), prefixes ("[Team] Foundry"), or entirely different naming conventions.

### Phase 2: List Discovery (Steps 5–7)

**What it does:** Fetches all lists from the board, locates Sprint_Backlog and In_Progress using flexible name matching, and reports what was found.

**Strengths:**
- Flexible name matching (lowercase, normalize separators) is excellent. Handles underscores, hyphens, spaces, and mixed case — covers all common Trello naming conventions.
- Explicit examples of what matches (step 6) make the matching behavior predictable and testable.
- Reporting discovered lists with actual names and card counts gives the user confidence the right lists were found.

**Weaknesses:**
- Step numbering jumps from 3 to 5 — steps 4 is missing from the document. This appears to be a numbering error rather than a missing step.
- No handling for **multiple lists that match the same pattern**. If a board has both "Sprint_Backlog" and "Sprint Backlog Archive", both normalize the same way. The skill should either match the first one found or report ambiguity.
- The matching algorithm normalizes separators to "a single common separator" but doesn't specify which separator. This is an implementation detail that could cause subtle bugs if implemented inconsistently.
- No validation that the Sprint_Backlog and In_Progress lists are different lists. If they somehow resolve to the same list ID, cards would be "moved" to their current location.

### Phase 3: Card Loading (Steps 9–14)

**What it does:** Fetches all cards from Sprint_Backlog, gathers full details (description, checklists, comments) for each card, compiles card text, logs a summary, and handles dry runs.

**Strengths:**
- Comprehensive card detail gathering — name, description, checklists (with completion state), and comments are all captured. This ensures no data is silently dropped during bean creation.
- The compiled text format is clean and well-structured (heading, description, checklists as checkboxes, comments with attribution).
- Omitting empty sections is a good touch — avoids cluttering beans with blank sections.
- Dry run support is well-placed before any state changes.
- Progress logging ("Found N cards") provides visibility into the pipeline.

**Weaknesses:**
- **No pagination handling.** If Sprint_Backlog has many cards, the `get_cards_by_list_id` call may return paginated results. The skill doesn't mention handling pagination or setting a limit. For large backlogs (50+ cards), this could silently miss cards.
- **No rate limiting or batching.** For each card, the skill makes 3+ API calls (get_card, get_checklist_items per checklist, get_card_comments). For N cards, this could be 3N+ API calls. Trello's API has rate limits (~100 requests per 10 seconds per key). A backlog with 30+ cards could hit rate limits.
- **No deduplication against existing beans.** Before creating beans, the skill doesn't check if a Trello card has already been imported in a previous run. If `/trello-load` is run twice and the first run failed to move some cards, those cards would be re-imported as duplicate beans.
- The compiled text format includes comments with "[Author] ([date]): [comment text]" but doesn't specify date format or handling of rich-text comments (Trello supports markdown in comments).
- **No card ordering guarantee.** The skill processes cards "in order" but doesn't specify which order — Trello's default API order, alphabetical, by creation date, by position? This matters for predictable bean ID assignment.

### Phase 4: Sequential Bean Creation (Steps 15a–15g)

**What it does:** For each card, re-reads `_index.md` for the current max bean ID, creates a well-formed bean from the card content, writes the bean, updates `_index.md`, moves the card to In_Progress, and handles errors gracefully.

**Strengths:**
- **Re-reading `_index.md` before each bean** is the correct approach for multi-agent safety. Another agent may have created beans between iterations.
- **Direct creation instead of invoking `/backlog-refinement`** is the right call — avoids the interactive dialogue that would break non-interactive operation.
- **Field mapping is comprehensive.** All bean template fields are covered with clear mapping rules:
  - Title and slug from card name
  - Problem Statement derived from description (with fallback for empty descriptions)
  - Acceptance criteria from checklists with standard criteria always included
  - Priority defaults to High with label-based hints
  - Status set to Approved (pre-approved from sprint backlog)
  - Category inferred from content
- **Trello metadata section** is well-specified with workspace, board, list, card ID, card name, and URL. This provides full traceability back to the source card.
- **Error handling per card** (log error, skip, continue) is the correct approach for batch operations — one bad card shouldn't stop the entire pipeline.
- **Cards only move to In_Progress after bean creation succeeds** — this is an important ordering guarantee that prevents orphaned cards.

**Weaknesses:**
- **No invocation of `/new-bean`.** Like `/backlog-refinement`, this skill duplicates the bean creation process inline. If `/new-bean` is updated with new fields or validation, `/trello-load` won't pick up the changes. This is the same issue flagged in BEAN-131's analysis.
- **No workspace name caching.** Step 15d says to get the workspace name from `mcp__trello__list_workspaces` but doesn't specify when. Calling this for every card is wasteful — it should be fetched once in Phase 1 and reused.
- **Slug generation is unspecified.** Step 15d says "Generate a slug from it" but doesn't define the slugification rules. Different implementations could produce different slugs from the same title (e.g., handling of special characters, max length, consecutive hyphens).
- **Category inference rules are vague.** "App for code/test/UI changes, Process for workflow/agent changes, Infra for CI/CD/git changes" — but Trello cards may not clearly indicate category. There's no fallback default or instruction to flag ambiguity.
- **No Trello label-to-bean-field mapping beyond priority.** Trello labels can carry rich metadata (custom fields, label names beyond colors). The skill only uses label colors for priority hints. Other labels are silently ignored.
- **Index append and bean creation are not atomic.** If the process crashes between writing `bean.md` and appending to `_index.md` (or vice versa), the system ends up in an inconsistent state. There's no recovery guidance for this scenario.

### Phase 5: Summary (Step 16)

**What it does:** Presents a completion report with counts (processed, moved, skipped) and a bean-to-card mapping table.

**Strengths:**
- Clear, structured summary with actionable counts (processed vs moved vs skipped).
- Bean-to-card mapping table provides full traceability.
- Distinguishing between "cards processed" and "cards moved" correctly accounts for error cases.

**Weaknesses:**
- **No suggested next steps.** After importing beans, the natural workflow is to run `/long-run` or `/pick-bean` to start work. The summary should suggest this.
- **No mention of cards that failed.** The summary shows "Cards skipped: N" but doesn't list which cards were skipped and why. For debugging failed imports, this information is essential.
- **No total duration or timing information.** For a batch operation that could take minutes, knowing the elapsed time is useful for pipeline optimization.

---

## 3. Dependency Analysis

### Direct Dependencies

| Dependency | Used In | Assessment |
|-----------|---------|------------|
| Trello MCP server | All phases | Core dependency. Health check in Phase 1 is correct. But no reconnection strategy if the connection drops mid-run. |
| `mcp__trello__get_health` | Step 1 | Used for health check. Good. |
| `mcp__trello__list_boards` | Step 2 | Used for board discovery. Good. |
| `mcp__trello__set_active_board` | Step 3 | Sets context for subsequent calls. Good. |
| `mcp__trello__get_lists` | Step 5 | Fetches lists for the board. Good. |
| `mcp__trello__get_cards_by_list_id` | Step 9 | Fetches cards from Sprint_Backlog. No pagination handling. |
| `mcp__trello__get_card` | Step 11a | Full card details with markdown. Good. |
| `mcp__trello__get_checklist_items` | Step 11b | Per-checklist item fetch. Multiple calls per card possible. |
| `mcp__trello__get_card_comments` | Step 11c | Comment history. Good. |
| `mcp__trello__move_card` | Step 15f | Moves card after bean creation. Correct ordering. |
| `mcp__trello__list_workspaces` | Step 15d | Workspace name for Trello section. Not specified when to call. |
| `ai/beans/_index.md` | Step 15b | Re-read per card. Correct for multi-agent safety. |
| `ai/beans/_bean-template.md` | Step 15d (implicit) | Listed in trigger requirements but not referenced in process steps. |

### MCP API Call Analysis

For a run with N cards, each having C checklists:

| Phase | Calls | Count |
|-------|-------|-------|
| Board selection | health + list_boards + set_active | 3 |
| List discovery | get_lists | 1 |
| Card loading | get_cards_by_list_id + N × (get_card + C × get_checklist_items + get_card_comments) | 1 + N × (2 + C) |
| Bean creation | N × move_card + list_workspaces | N + 1 |
| **Total** | | **5 + N × (3 + C) + 1** |

For 10 cards with 2 checklists each: ~56 API calls. For 30 cards: ~156 calls. This could hit Trello rate limits for larger backlogs.

### Interaction with Related Skills

| Skill | Relationship | Notes |
|-------|-------------|-------|
| `/backlog-refinement` | Alternative intake path | Refinement is interactive; trello-load is automated. Both create beans but with different approval statuses (Unapproved vs Approved). |
| `/backlog-consolidate` | Downstream consumer | Should run after trello-load to catch any overlaps between imported beans and existing backlog. Not mentioned in the skill. |
| `/long-run` | Downstream consumer | Imported Approved beans are immediately eligible for `/long-run` processing. This is the expected next step but isn't documented. |
| `/pick-bean` | Downstream consumer | Alternative to `/long-run` for manual bean selection. Not mentioned. |
| `/new-bean` | Parallel implementation | Bean creation is done inline rather than delegating to `/new-bean`. Same issue as `/backlog-refinement`. |
| `/review-beans` | Not needed | Beans are created as Approved, so review gate is skipped. This is correct for pre-curated sprint backlog items. |

---

## 4. Edge Cases

| Edge Case | Current Handling | Risk |
|-----------|-----------------|------|
| Trello MCP server down | `TrelloMCPDown` — log and stop | Low — properly handled |
| No boards accessible | `NoBoards` — log and stop | Low — properly handled |
| Sprint_Backlog list missing | `ListNotFound` — show available lists, stop | Low — properly handled |
| In_Progress list missing | `ListNotFound` — show available lists, stop | Low — properly handled |
| Empty Sprint_Backlog | `EmptyBacklog` — inform and stop | Low — properly handled |
| Card with empty description | Expand card name into problem statement | Low — explicit fallback defined |
| Card with no checklists | Omit Checklists section | Low — handled by "omit empty sections" rule |
| Card with no comments | Omit Comments section | Low — handled by "omit empty sections" rule |
| **Re-running after partial failure** | **No deduplication check** | **High — duplicate beans created for cards not moved** |
| **Large backlog (50+ cards)** | **No pagination or rate limiting** | **High — could hit API limits or miss cards** |
| **Multiple lists matching "Sprint_Backlog"** | **No disambiguation** | **Medium — unpredictable list selection** |
| Card with very long description (10K+ chars) | No truncation or size limit | Medium — could create oversized beans |
| Card title with special characters | Slug generation unspecified | Medium — could create invalid directory names |
| Board with no "Foundry" match and multiple boards | Falls back to first board | Medium — could process wrong board |
| Concurrent `/trello-load` runs | Re-reads `_index.md` per bean — ID conflicts unlikely | Low — well-handled for IDs, but cards could be double-processed |
| Card move fails after bean created | Bean exists but card stays in Sprint_Backlog | Medium — creates inconsistency between systems |
| MCP connection drops mid-run | **No reconnection strategy** | Medium — remaining cards unprocessed, no partial summary |
| Card with labels but no color mapping (custom labels) | Only color-based priority mapping defined | Low — defaults to High |

---

## 5. Quality Criteria Assessment

The skill defines 8 quality criteria. Assessment of each:

| # | Criterion | Verifiable? | Gap? |
|---|-----------|------------|------|
| 1 | Every card's full context is used — no data silently dropped | Structural check | None — process explicitly gathers name, description, checklists, comments |
| 2 | List name matching is flexible and case-insensitive | Testable | None — explicit examples provided |
| 3 | Cards only moved after bean creation succeeds | Ordering check | None — explicitly stated in step 15f |
| 4 | Failed cards stay in Sprint_Backlog | Error handling check | None — covered in step 15g |
| 5 | Beans created with Approved status | Field check | None — explicitly stated |
| 6 | No user interaction required | Design check | None — core design principle |
| 7 | Clear progress logging (card N/M) | Output check | None — format specified in step 15a |
| 8 | Final summary accurately reflects what was created/moved | Consistency check | Minor — skipped cards aren't listed by name |

**Missing quality criteria:**
- **Idempotency:** Re-running after partial failure should not create duplicate beans. The skill should check if a Trello card has already been imported (by checking existing beans' Trello sections for matching Card IDs).
- **Rate limit awareness:** The skill should either batch API calls or include backoff logic to avoid hitting Trello's rate limits.
- **Slug validity:** Generated slugs should be valid filesystem directory names (no special characters, reasonable length).
- **Trello metadata completeness:** Every created bean should have a fully populated Trello section with all 7 fields (Source, Workspace, Board, Source List, Card ID, Card Name, Card URL).

---

## 6. Comparison with `/backlog-refinement`

Both skills create beans from external input, but with fundamentally different interaction models:

| Aspect | Trello Load | Backlog Refinement | Assessment |
|--------|------------|-------------------|------------|
| **Interaction model** | Fully non-interactive | Interactive dialogue | Complementary — different use cases |
| **Input source** | Trello API (structured) | Raw user text (unstructured) | Trello has richer metadata (checklists, comments, labels) |
| **Bean status** | Approved (pre-curated) | Unapproved (needs review) | Correct — sprint backlog is pre-approved |
| **Duplicate detection** | None | Checks `_index.md` titles | **Both are weak** — neither checks Done beans or external sources |
| **Multi-agent safety** | Re-reads `_index.md` per bean | Deferred IDs, fresh reads | Equivalent — both handle concurrent writes |
| **Error recovery** | Skip and continue | No rollback guidance | Trello load is better — designed for batch failure |
| **Bean creation** | Inline (duplicates `/new-bean`) | Inline (duplicates `/new-bean`) | **Same issue in both** — should delegate to `/new-bean` |
| **External system sync** | Moves cards to In_Progress | N/A | Trello load adds bidirectional sync complexity |
| **Trello metadata** | Full Trello section populated | `Source: Manual` | Trello load has superior traceability |
| **Dry run support** | Yes | Yes | Equivalent |
| **Next steps guidance** | None | Only `/bean-status` | **Both are weak** — should suggest next actions |

**Key takeaway:** `/trello-load` inherits the same inline-creation issue as `/backlog-refinement` but adds unique challenges around idempotency, rate limiting, and external system synchronization that the other intake skills don't face.

---

## 7. Improvement Recommendations

### Priority: High

1. **Add idempotency / deduplication.** Before creating a bean for a card, scan existing beans for a matching Trello Card ID in their `## Trello` section. If found, skip the card and log that it was already imported. This prevents duplicate beans when re-running after partial failures — the most likely operational failure mode for this skill.

2. **Fix the first-board fallback.** When no board name matches the project directory, do not silently fall back to the first board. Instead, stop with an error listing available boards and instruct the user to use `--board <id>`. The current behavior risks processing cards from an entirely unrelated project.

3. **Delegate creation to `/new-bean`.** Same recommendation as BEAN-131 — replace inline bean creation with explicit `/new-bean` invocation. This ensures consistency when `/new-bean` is updated and eliminates duplicated logic across three skills (refinement, consolidation, trello-load).

4. **Add rate limiting / backoff.** For batches larger than 10 cards, add a brief pause between card processing iterations. Document the expected API call count formula (5 + N × (3 + C) + 1) and recommend the `--board` flag for large batches to skip the discovery phase.

### Priority: Medium

5. **Cache workspace name.** Fetch `mcp__trello__list_workspaces` once during Phase 1 (after board selection) and reuse the result for all beans. This eliminates N-1 redundant API calls.

6. **Add suggested next steps to summary.** After import, suggest: "Run `/long-run --category App` to process imported beans" or "Run `/backlog-consolidate` to check for overlaps with existing backlog."

7. **Handle multiple matching lists.** If more than one list matches "Sprint_Backlog" after normalization, report the ambiguity and either pick the one with the most cards or stop with an error asking the user to rename lists.

8. **List failed cards in the summary.** Change "Cards skipped: N" to include card names and error reasons:
   ```
   Cards skipped (2):
   - "Deploy pipeline" — BeanCreateError: slug collision
   - "Fix auth bug" — MoveError: card already archived
   ```

9. **Add MCP connection resilience.** If an API call fails with a transient error (timeout, 429 rate limit), retry once with exponential backoff before skipping the card. If the MCP server becomes completely unreachable mid-run, output a partial summary of what was completed.

### Priority: Low

10. **Define slug generation rules.** Specify: lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, truncate to 50 characters, strip trailing hyphens. This ensures consistent directory naming across runs.

11. **Add card ordering specification.** State that cards are processed in Trello position order (the order they appear in the list). This makes bean ID assignment predictable and reproducible.

12. **Fix step numbering.** Phase 2 jumps from step 3 to step 5 — renumber to be sequential (steps 4–6) or clarify if step 4 was intentionally omitted.

13. **Add elapsed time to summary.** Include total processing time and average time per card. Useful for pipeline optimization and spotting rate limit throttling.

14. **Support Trello custom fields.** If cards have custom fields (e.g., "Estimated Effort", "Component"), map them to bean Notes or dedicated fields. Currently all custom field data is silently dropped.

---

## 8. Summary

The `/trello-load` skill is well-designed for its primary use case: automated, non-interactive import of pre-curated sprint backlog items. Its strongest aspects are the flexible list name matching, comprehensive card data gathering, per-card error handling, and the correct ordering of bean creation before card movement.

The most significant gaps are:

1. **No idempotency** — re-running after a partial failure creates duplicate beans, which is the most operationally dangerous issue since partial failures are the most likely failure mode for a multi-step external API pipeline.
2. **Unsafe board fallback** — silently picking the first board when no name match is found could process the wrong project's cards.
3. **Inline bean creation** — duplicates `/new-bean` logic, same issue found in `/backlog-refinement` (BEAN-131).
4. **No rate limiting** — large backlogs could exceed Trello's API rate limits without any mitigation.

These gaps represent concrete improvement opportunities for future Process beans, with idempotency being the single most impactful fix.
