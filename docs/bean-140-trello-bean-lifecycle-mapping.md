# Analysis: Trello-Bean Lifecycle Mapping

**Bean:** BEAN-140 | **Date:** 2026-02-16 | **Analyst:** Developer

---

## 1. Overview

The Foundry AI team maintains two parallel work-tracking systems: **Trello** (external, human-facing) and the **Bean system** (internal, agent-facing). Three skills form the integration bridge:

| Skill | Direction | Purpose |
|-------|-----------|---------|
| `/trello-load` | Trello → Beans | Import cards from Sprint_Backlog as Approved beans |
| `/long-run` (Phase 0.5) | Trello → Beans | Invokes `/trello-load` before each backlog processing cycle |
| `/long-run` (Phase 5.5, step 17b) | Beans → Trello | Moves source card to Completed after merge |
| `/merge-bean` | — | No direct Trello integration (hands off to `/long-run` caller) |

This document maps the complete lifecycle: how a Trello card becomes a bean, how bean state changes propagate back to Trello, what data is preserved or lost at each transition, and where the integration has gaps.

**Prior art:** This analysis synthesizes findings from BEAN-132 (long-run analysis) and BEAN-136 (trello-load analysis). BEAN-122 (Structured Trello Linkage) established the data format used for Trello↔Bean traceability.

---

## 2. Complete Lifecycle: End-to-End Flow

### 2.1 The Happy Path

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TRELLO BOARD                                      │
│                                                                          │
│  Sprint_Backlog ──────► In_Progress ──────────────────► Completed        │
│       │ (card)         │ (card moved           │ (card moved             │
│       │                │  by /trello-load)      │  by /long-run           │
│       │                │                        │  after merge)           │
└───────┼────────────────┼────────────────────────┼────────────────────────┘
        │                │                        ▲
        │ /trello-load   │                        │ /long-run step 17b
        ▼                │                        │
┌───────┼────────────────┼────────────────────────┼────────────────────────┐
│       │           BEAN SYSTEM                   │                        │
│       │                                         │                        │
│  [Created] ──► Approved ──► In Progress ──► Done ──► Merged to test     │
│   (bean.md      (status      (picked by       (verified,    (feature     │
│    written)      set by       team-lead)       committed)    branch       │
│                  /trello-                                    merged)      │
│                  load)                                                    │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Step-by-Step Lifecycle

| Step | Actor | Action | Trello State | Bean State | Notes |
|------|-------|--------|-------------|------------|-------|
| 1 | Human | Creates/curates card in Sprint_Backlog | Sprint_Backlog | — | Card is pre-approved by being in Sprint_Backlog |
| 2 | `/trello-load` | Reads card details (name, description, checklists, comments) | Sprint_Backlog | — | 3+ API calls per card |
| 3 | `/trello-load` | Creates bean directory + bean.md + appends to _index.md | Sprint_Backlog | **Approved** | Bypasses Unapproved gate — implicit trust transfer |
| 4 | `/trello-load` | Moves card to In_Progress list | **In_Progress** | Approved | Card moves AFTER bean creation succeeds |
| 5 | `/long-run` | Picks bean, creates feature branch, decomposes tasks | In_Progress | **In Progress** | Bean locked by status + owner |
| 6 | `/long-run` | Executes team wave (BA → Architect → Developer → Tech QA) | In_Progress | In Progress | No Trello interaction during execution |
| 7 | `/long-run` | Verifies acceptance criteria, commits on feature branch | In_Progress | **Done** | Tests + lint must pass for code beans |
| 8 | `/merge-bean` | Merges feature branch to test, pushes | In_Progress | Done (merged) | No direct Trello interaction |
| 9 | `/long-run` 17b | Reads bean's Trello section, moves card to Completed | **Completed** | Done | Best-effort — failure doesn't block |

---

## 3. State Mapping: Trello Lists ↔ Bean Statuses

### 3.1 Correspondence Table

| Trello List | Bean Status | Transition Trigger | Direction |
|-------------|------------|-------------------|-----------|
| Sprint_Backlog | — (no bean yet) | Card exists in Trello only | — |
| Sprint_Backlog → In_Progress | **Approved** (bean created) | `/trello-load` processes card | Trello → Bean |
| In_Progress | Approved → In Progress | `/long-run` picks bean | Bean internal |
| In_Progress | In Progress → Done | `/long-run` completes wave | Bean internal |
| In_Progress → Completed | Done (merged) | `/long-run` step 17b after merge | Bean → Trello |

### 3.2 Asymmetries

The mapping is **not symmetric**. Key asymmetries:

1. **Trello has 3 relevant lists; Beans have 5 statuses.** The Trello lists (Sprint_Backlog, In_Progress, Completed) map to a subset of bean statuses. The `Unapproved` and `Deferred` statuses have no Trello equivalent — Trello-sourced beans skip `Unapproved` entirely, and there is no mechanism to move a card back to Sprint_Backlog if a bean is deferred.

2. **Trello In_Progress spans two bean states.** A card sits in Trello's In_Progress list from the moment `/trello-load` processes it until `/long-run` completes and merges the bean. During this time, the bean transitions through Approved → In Progress → Done. Trello doesn't reflect these intermediate states.

3. **Bean Done ≠ Trello Completed.** A bean can be Done (all criteria met, committed on feature branch) but the Trello card stays in In_Progress until the merge succeeds AND `/long-run` step 17b executes. If the merge fails or step 17b is skipped, the card stays in In_Progress indefinitely.

4. **Manual beans have no Trello counterpart.** Beans with `Source: Manual` in their Trello section are invisible to Trello. Their lifecycle is entirely internal to the bean system.

### 3.3 State Divergence Scenarios

| Scenario | Bean State | Trello State | Cause | Impact |
|----------|-----------|-------------|-------|--------|
| Normal operation | Done (merged) | Completed | Happy path | None |
| Merge fails | Done (on feature branch) | In_Progress | Merge conflict in `/merge-bean` | Card stuck in In_Progress |
| Trello MCP down during completion | Done (merged) | In_Progress | Step 17b fails (best-effort) | Card stuck in In_Progress |
| `/trello-load` crashes mid-run | Approved (partial) | Mixed — some In_Progress, some Sprint_Backlog | Process crash | Beans created but some cards not moved |
| Bean deferred after import | Deferred | In_Progress | Human changes bean status | Card stuck in In_Progress |
| Bean manually created from Trello card | Approved (manual) | Sprint_Backlog | Human creates bean, doesn't move card | Duplicate if `/trello-load` runs again |
| `/long-run` interrupted | In Progress | In_Progress | Agent crash, timeout | Bean locked, card stuck |
| Re-run after partial `/trello-load` failure | Approved (duplicate) | Sprint_Backlog | No deduplication check | Duplicate beans |

---

## 4. Data Transformation Analysis

### 4.1 Inbound: Trello Card → Bean (via `/trello-load`)

| Trello Card Field | Bean Field | Transformation | Fidelity |
|-------------------|-----------|---------------|----------|
| Card Name | Title | Direct copy | Lossless |
| Card Name | Slug | Slugified (lowercase, hyphens, truncated) | Lossy — special chars stripped, length limited |
| Card Description | Problem Statement | Derived/expanded; empty descriptions get AI-generated expansion | Lossy — AI interpretation may alter meaning |
| Card Description | Goal | Inferred from description + checklists | Lossy — AI inference |
| Card Description + Checklists | Scope (In Scope) | Extracted from checklist items + description | Lossy — AI curation |
| — | Scope (Out of Scope) | AI-generated from context | Generated — no source data |
| Checklist Items | Acceptance Criteria | Converted to criteria + standard "tests pass"/"lint clean" added | Augmented — standard criteria always added |
| Labels (colors) | Priority | Color mapping (red=High, yellow=Medium, green=Low); default High | Lossy — only color used, label names ignored |
| — | Status | Always `Approved` | Hardcoded — trust transfer from Sprint_Backlog |
| Content analysis | Category | AI-inferred (App/Process/Infra) | Lossy — AI inference, no explicit source |
| Comments | Notes | Comment text with author/date attribution | Near-lossless — formatting may change |
| Card ID | Trello.Card ID | Direct copy | Lossless |
| Card Name | Trello.Card Name | Direct copy | Lossless |
| Card Short Link | Trello.Card URL | Constructed URL | Lossless |
| Board Name + ID | Trello.Board | Formatted as "Name (ID: xxx)" | Lossless |
| Workspace Name | Trello.Workspace | Direct copy | Lossless |
| Source List Name | Trello.Source List | Direct copy | Lossless |
| Custom Fields | — | **Silently dropped** | Total loss |
| Attachments | — | **Silently dropped** | Total loss |
| Due Dates | — | **Silently dropped** | Total loss |
| Member Assignments | — | **Silently dropped** | Total loss |
| Label Names | — | **Silently dropped** (only colors used for priority) | Total loss |

**Data loss summary:** Custom fields, attachments, due dates, member assignments, and label names are all lost during import. Card descriptions undergo AI interpretation that may alter original meaning. The most significant loss is **custom fields**, which teams often use for effort estimation, component tagging, or sprint planning metadata.

### 4.2 Outbound: Bean → Trello Card (via `/long-run` step 17b)

The outbound flow is **extremely narrow** — only one piece of data flows back to Trello:

| Bean Field | Trello Action | Transformation |
|-----------|--------------|---------------|
| Trello.Card ID | `move_card` API call | Card moved from In_Progress to Completed |

**No other bean data propagates back to Trello.** The following bean state is never reflected in Trello:

- Bean acceptance criteria completion status
- Task decomposition and individual task results
- Developer outputs and code changes
- Test results
- Telemetry data (duration, tokens, cost)
- Whether the bean was deferred or modified post-import

The outbound flow is a **binary signal**: the card moves from In_Progress to Completed. There is no partial progress, no status updates during execution, and no metadata enrichment on the Trello card.

### 4.3 The Trello Metadata Section (BEAN-122)

BEAN-122 established the structured `## Trello` section in bean.md, replacing the previous fragile free-text note approach. This section serves as the **bridge data** enabling the outbound flow:

```markdown
## Trello
| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Workspace** | [workspace name] |
| **Board** | [board name] (ID: [board ID]) |
| **Source List** | [list name] |
| **Card ID** | [card ID] |
| **Card Name** | [card name] |
| **Card URL** | [card URL] |
```

**Critical fields for the outbound flow:**
- `Source` — determines whether outbound sync should be attempted (Trello vs Manual)
- `Card ID` — used for the `move_card` API call (stable identifier)
- `Board` — contains the board ID needed to discover the Completed list

**Redundant but useful fields:**
- `Card Name` — human reference only; not used programmatically
- `Card URL` — human reference only; enables quick navigation
- `Workspace` — informational; not used in the outbound flow
- `Source List` — historical record; not used in the outbound flow

---

## 5. Integration Points: Detailed Analysis

### 5.1 Integration Point 1: `/trello-load` (Inbound)

**Trigger:** Invoked directly or by `/long-run` Phase 0.5.

**API calls per card:** ~3 + C (where C = number of checklists)
- `get_card` (with markdown)
- `get_card_comments`
- `get_checklist_items` × C checklists

**Data flow:**
```
Trello API → Card data → AI interpretation → bean.md + _index.md → move_card
```

**Strengths (from BEAN-136 analysis):**
- Flexible list name matching (handles underscores, hyphens, spaces, mixed case)
- Per-card error handling (skip and continue)
- Cards only moved after bean creation succeeds
- Re-reads `_index.md` per bean for multi-agent safety

**Weaknesses (from BEAN-136 analysis):**
- No idempotency — re-running after partial failure creates duplicate beans
- No pagination handling for large backlogs
- No rate limiting (56+ API calls for 10 cards)
- Unsafe first-board fallback
- Inline bean creation (doesn't delegate to `/new-bean`)

### 5.2 Integration Point 2: `/long-run` Phase 0.5 (Inbound Trigger)

**Trigger:** Automatic, at the start of every `/long-run` cycle.

**Behavior:** Invokes `/trello-load` non-interactively. Best-effort — failures don't block the run.

**Design rationale (from BEAN-132 analysis):** Making Trello sync optional prevents a third-party service from blocking autonomous operation. The one-way flow (Trello → Beans) is simple and predictable.

**Observation:** Every `/long-run` iteration re-invokes `/trello-load`, which re-reads the Sprint_Backlog list. If `/trello-load` previously moved cards to In_Progress successfully, the re-invocation finds an empty Sprint_Backlog and exits quickly. This is wasteful but harmless. However, if cards were added to Sprint_Backlog between iterations, they get picked up automatically — a useful feature for continuous integration.

### 5.3 Integration Point 3: `/long-run` Phase 5.5, Step 17b (Outbound)

**Trigger:** After successful merge of a bean's feature branch to `test`.

**Process:**
1. Read the bean's `## Trello` section
2. Parse the `Source` field — if `Manual`, skip
3. If `Trello`, extract `Card ID` and `Board` (parse board ID from "Name (ID: xxx)" format)
4. Call `get_lists` with board ID to find the Completed list (flexible name matching)
5. Call `move_card` with Card ID and Completed list ID
6. Log the move; if failure, log warning and continue

**API calls:** 2 per Trello-sourced bean (`get_lists` + `move_card`). For Manual beans: 0.

**Strengths (from BEAN-132 analysis):**
- Uses stable Card ID (not fuzzy name matching) since BEAN-122
- Best-effort design doesn't block the merge pipeline
- Same flexible list matching as `/trello-load`

**Weaknesses:**
- `get_lists` is called for every bean — the Completed list ID could be cached per board
- The board ID parsing ("Name (ID: xxx)") is format-dependent — if the Trello section format changes, parsing breaks
- No verification that the card is still in In_Progress before moving (edge case: card manually moved by human)

### 5.4 Integration Point 4: Parallel Mode (Outbound, Orchestrator)

In parallel mode, the Trello card completion logic is identical to sequential mode but executed by the orchestrator (not the worker). The orchestrator handles merges and Trello card moves centrally.

**Duplication risk (from BEAN-132 analysis):** Steps 17b (sequential) and Parallel Phase 5 step 12 both describe the Trello card movement logic. Changes to one must be manually mirrored in the other.

---

## 6. Failure Mode Inventory

### 6.1 Inbound Failures (Trello → Bean)

| # | Failure Mode | Probability | Detection | Impact | Recovery |
|---|-------------|-------------|-----------|--------|----------|
| F1 | Trello MCP server unreachable | Medium | Health check in Phase 1 | No cards imported | Retry `/trello-load` when MCP is back |
| F2 | Board not found / wrong board selected | Low | No detection for wrong board | Wrong cards processed | Manual cleanup; use `--board` flag |
| F3 | Sprint_Backlog list not found | Low | Explicit error with available lists | No cards imported | Rename list to match expected pattern |
| F4 | Card detail fetch fails | Low | Per-card error handling | Single card skipped | Card stays in Sprint_Backlog for next run |
| F5 | Bean creation fails (write error) | Low | Per-card error handling | Single card skipped | Card stays in Sprint_Backlog for next run |
| F6 | Card move fails after bean created | Medium | Logged as warning | Bean exists but card stays in Sprint_Backlog | **Duplicate on next run** (no dedup) |
| F7 | Re-run after partial failure | High (when F4-F6 occur) | **No detection** | Duplicate beans created | Manual deletion of duplicates |
| F8 | MCP connection drops mid-batch | Low | **No detection until next API call** | Remaining cards unprocessed, no partial summary | Re-run; duplicates possible for processed cards |
| F9 | Rate limit hit (large backlog) | Medium | **No detection** (Trello returns 429) | Subsequent API calls fail | Reduce batch size; add rate limiting |
| F10 | Concurrent `/trello-load` runs | Low | Re-read `_index.md` per bean | Bean ID conflicts unlikely, but cards could be double-processed | Status file protocol prevents in parallel mode |

### 6.2 Outbound Failures (Bean → Trello)

| # | Failure Mode | Probability | Detection | Impact | Recovery |
|---|-------------|-------------|-----------|--------|----------|
| F11 | Trello MCP unavailable at completion | Medium | Caught as best-effort failure | Card stays in In_Progress | Manual move in Trello UI |
| F12 | Completed list not found on board | Low | `get_lists` returns no match | Card stays in In_Progress | Create Completed list; re-run or manual move |
| F13 | Card ID invalid (deleted card) | Low | API error from `move_card` | Move fails silently | No recovery needed (card already gone) |
| F14 | Card manually moved by human | Low | **No detection** | `move_card` may fail or be a no-op | Harmless — card already in correct place |
| F15 | Board ID parsing fails | Low | **No detection** (malformed Trello section) | Card stays in In_Progress | Fix Trello section format; manual move |
| F16 | Merge fails before step 17b | Medium | Merge conflict detection in `/merge-bean` | Card stays in In_Progress; bean stays Done | Fix conflicts; re-merge; card move doesn't retry |
| F17 | Agent crash after merge but before 17b | Low | **No detection** | Bean merged but card not moved | Manual move in Trello UI |

### 6.3 Cross-Cutting Failures

| # | Failure Mode | Probability | Detection | Impact | Recovery |
|---|-------------|-------------|-----------|--------|----------|
| F18 | Bean deferred after Trello import | Low | **No mechanism to update Trello** | Card stuck in In_Progress indefinitely | Manual move back to Sprint_Backlog |
| F19 | Bean scope changed significantly | Low | **No mechanism to update Trello card** | Trello card content no longer matches bean | Accept divergence or update card manually |
| F20 | Trello card edited after import | Low | **No detection** | Bean content doesn't reflect card edits | Accept divergence — bean is source of truth after import |

---

## 7. Gap Analysis

### 7.1 Critical Gaps

| # | Gap | Severity | Description | Recommendation |
|---|-----|----------|-------------|----------------|
| G1 | **No idempotency on inbound** | High | Re-running `/trello-load` after a partial failure creates duplicate beans. The most operationally dangerous gap. | Check existing beans' Trello sections for matching Card IDs before creating new beans. (Also flagged in BEAN-136.) |
| G2 | **One-way data flow only** | Medium | Bean state changes (Deferred, scope changes, task progress) never propagate to Trello. Humans checking Trello see stale information. | At minimum, add a comment to the Trello card when bean status changes. Full sync is out of scope. |
| G3 | **No intermediate status updates** | Medium | Trello card stays in In_Progress from import until completion. For multi-day beans, there is no progress visibility on the Trello side. | Add Trello card comments at key milestones (bean picked, 50% tasks done, bean done). |

### 7.2 Moderate Gaps

| # | Gap | Severity | Description | Recommendation |
|---|-----|----------|-------------|----------------|
| G4 | **No deferred-bean Trello handling** | Medium | If a bean is deferred after import, the Trello card stays in In_Progress forever. | When a bean status changes to Deferred, move its Trello card back to Sprint_Backlog (or a new "Deferred" list). |
| G5 | **Data loss on import** | Medium | Custom fields, attachments, due dates, and member assignments are silently dropped. | Log dropped fields; optionally map custom fields to bean Notes. |
| G6 | **Completed list discovery per bean** | Low | The `get_lists` API call is made for every Trello-sourced bean at completion time, even though the Completed list ID doesn't change. | Cache the Completed list ID per board during the `/long-run` session. |
| G7 | **Duplicated Trello logic across modes** | Medium | Sequential step 17b and parallel Phase 5 step 12 describe identical Trello card movement logic. | Extract into a shared section or skill fragment. (Also flagged in BEAN-132.) |

### 7.3 Minor Gaps

| # | Gap | Severity | Description | Recommendation |
|---|-----|----------|-------------|----------------|
| G8 | **No Trello card enrichment at completion** | Low | When a bean completes, the Trello card gets moved but receives no summary, link to the merge commit, or telemetry data. | Add a comment to the Trello card with the bean summary, merge commit hash, and duration. |
| G9 | **No link from Trello card to bean** | Low | Trello cards don't reference the bean ID. Humans looking at Trello can't easily find the corresponding bean. | Add a comment to the Trello card when the bean is created: "Imported as BEAN-NNN". |
| G10 | **Board ID format coupling** | Low | The outbound flow parses board ID from the format "Name (ID: xxx)". If this format changes, parsing breaks silently. | Use a dedicated `Board ID` field instead of embedding ID in the Board name field. |

---

## 8. Lifecycle Comparison: Trello-Sourced vs. Manual Beans

| Aspect | Trello-Sourced Bean | Manual Bean |
|--------|-------------------|-------------|
| **Creation path** | `/trello-load` (automated) | `/backlog-refinement`, `/new-bean`, or manual |
| **Initial status** | Approved (bypasses Unapproved gate) | Unapproved (requires human approval) |
| **Trello section** | Fully populated (7 fields) | `Source: Manual` only |
| **Approval gate** | Implicit — curated in Sprint_Backlog | Explicit — human reviews and approves |
| **Execution** | Identical | Identical |
| **Completion** | Trello card moved to Completed (best-effort) | No Trello interaction |
| **Traceability** | Full — Card ID links back to Trello | None — no external reference |
| **Failure recovery** | Risky — duplicate beans if `/trello-load` re-runs | Safe — no external state to diverge |

**Key insight:** Trello-sourced beans carry additional external state management burden. Every failure mode related to external state (F6, F7, F11, F16-F20) only affects Trello-sourced beans. Manual beans have a simpler, more robust lifecycle.

---

## 9. Timing and Ordering Analysis

### 9.1 Inbound Timing

```
/trello-load execution:
  ├── Phase 1: Board selection (~3 API calls, ~2-5 seconds)
  ├── Phase 2: List discovery (~1 API call, ~1 second)
  ├── Phase 3: Card loading (N × (2+C) API calls, ~2-5 seconds per card)
  ├── Phase 4: Bean creation (N × (write + index update + move_card), ~3-8 seconds per card)
  └── Phase 5: Summary (~0 seconds)

  Total for 10 cards, 2 checklists each: ~56 API calls, ~60-120 seconds
```

### 9.2 Outbound Timing

```
/long-run step 17b per bean:
  ├── Read Trello section from bean.md (~0 seconds, local file)
  ├── Parse Source, Card ID, Board ID (~0 seconds)
  ├── get_lists for board (~1 second)
  ├── Find Completed list (~0 seconds, local matching)
  └── move_card (~1-2 seconds)

  Total per Trello-sourced bean: ~2-3 seconds
  Total per Manual bean: ~0 seconds (skip)
```

### 9.3 End-to-End Lifecycle Duration

For a typical Trello-sourced bean:

| Phase | Duration | Trello State | Bean State |
|-------|----------|-------------|------------|
| Card in Sprint_Backlog | Hours to days | Sprint_Backlog | — |
| `/trello-load` processes card | 3-8 seconds | Sprint_Backlog → In_Progress | — → Approved |
| Waiting for `/long-run` to pick | Minutes to hours | In_Progress | Approved |
| Bean execution (full wave) | 5-30 minutes | In_Progress | In Progress |
| Verification + commit | 1-3 minutes | In_Progress | In Progress → Done |
| Merge to test | 30-60 seconds | In_Progress | Done (merged) |
| Trello card move | 2-3 seconds | In_Progress → Completed | Done |

**Key observation:** The Trello card spends the vast majority of its time in In_Progress (potentially hours), but this single Trello state spans three bean states (Approved, In Progress, Done-pre-merge). Any human monitoring Trello has no visibility into bean execution progress.

---

## 10. Recommendations Summary

Organized by priority, referencing gap and failure mode IDs:

### High Priority

| # | Recommendation | Addresses | Effort |
|---|---------------|-----------|--------|
| R1 | **Add idempotency to `/trello-load`** — scan existing beans for matching Card IDs before creating. | G1, F6, F7 | Medium — requires scanning all bean Trello sections |
| R2 | **Add Trello card comment on bean creation** — "Imported as BEAN-NNN" | G9, improves traceability | Low — single API call after bean creation |
| R3 | **Handle deferred beans in Trello** — move card back to Sprint_Backlog or a Deferred list when bean status changes to Deferred | G4, F18 | Medium — new skill or hook needed |

### Medium Priority

| # | Recommendation | Addresses | Effort |
|---|---------------|-----------|--------|
| R4 | **Add completion comment to Trello card** — bean summary, merge commit, duration | G8 | Low — single API call |
| R5 | **Cache Completed list ID per session** — avoid repeated `get_lists` calls | G6 | Low — store in session state |
| R6 | **Extract Trello card-move logic** — deduplicate between sequential/parallel modes | G7 | Low — text refactoring |
| R7 | **Log dropped Trello data on import** — warn about custom fields, attachments, due dates | G5 | Low — add logging |
| R8 | **Add intermediate Trello status updates** — comment when bean picked, when done | G3 | Medium — multiple integration points |

### Low Priority

| # | Recommendation | Addresses | Effort |
|---|---------------|-----------|--------|
| R9 | **Separate Board ID field** — avoid parsing "Name (ID: xxx)" format | G10, F15 | Low — template change + parser update |
| R10 | **Add rate limiting to `/trello-load`** — backoff for large backlogs | F9 | Medium — timing logic |
| R11 | **Add MCP reconnection logic** — retry on transient failures | F8, F11 | Medium — error handling |

---

## 11. Summary

The Trello-Bean lifecycle integration is **functionally complete for the happy path** — cards flow from Sprint_Backlog through bean execution to Completed with full traceability via the structured Trello section (BEAN-122). The three integration points (`/trello-load` inbound, `/long-run` Phase 0.5 trigger, `/long-run` step 17b outbound) work together to create a coherent pipeline.

**The integration's defining characteristic is asymmetry:**

1. **Rich inbound, thin outbound.** Inbound import captures card name, description, checklists, comments, and full Trello metadata. Outbound is a single `move_card` call — no bean data propagates back to Trello.

2. **Trello is fire-and-forget after import.** Once a card enters the bean system, the bean becomes the source of truth. Trello is only updated at the very end (card → Completed). There are no intermediate status updates, no progress reporting, and no mechanism to reflect bean state changes (Deferred, scope changes) back to Trello.

3. **Failure recovery is unidirectional.** Bean-side failures (test failure, merge conflict) have defined recovery paths. Trello-side failures (MCP down, card move fails) are best-effort with no retry or reconciliation mechanism.

**The single most impactful improvement is idempotency (R1)** — preventing duplicate beans on re-run after partial failure. This addresses the most likely operational failure mode and has been independently identified in both BEAN-132 and BEAN-136 analyses.

**The single most impactful architectural improvement is bidirectional status visibility (R2 + R4 + R8)** — adding Trello card comments at key lifecycle points. This doesn't require full bidirectional sync but would give Trello-side observers meaningful visibility into bean execution progress.
