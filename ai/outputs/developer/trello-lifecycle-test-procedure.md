# Trello Lifecycle Test Procedure

Manual verification procedure for the Trello card → bean lifecycle integration.

## Expected State Transitions

| Bean Stage | Trello Action | Expected Trello List | Trigger |
|------------|---------------|----------------------|---------|
| Pre-import | Card exists in sprint backlog | Sprint_Backlog | User creates card in Trello |
| Bean created (Approved) | Card moved during import | In_Progress | `/long-run` Phase 0.5 invokes `/internal:trello-load` |
| Bean In Progress | No Trello action | In_Progress | Team Lead picks the bean |
| Bean Done + merged | Card moved after merge | Completed | `/long-run` Phase 5.5 step 17b |

## Prerequisites

- Trello MCP server is running and authenticated
- Board: Foundry (ID: `698e9e614a5e03d0ed57f638`)
- Lists exist: `Sprint_Backlog`, `In_Progress`, `Completed`

## Test Procedure

### Step 1: Create a test card in Trello

Create a card in the `Sprint_Backlog` list on the Foundry board.

**Verify:** Card appears in Sprint_Backlog (use `mcp__trello__get_cards_by_list_id` with the Sprint_Backlog list ID `698ffaf254037d0d070d2e8f`).

### Step 2: Run `/long-run` (or `/long-run --fast N`)

The Trello sync phase (Phase 0.5) should:
1. Read cards from Sprint_Backlog
2. Create a bean directory and `bean.md` with `## Trello` section containing Card ID, Board, Source List, Card Name, Card URL
3. Append the bean to `_index.md` with status `Approved`
4. Move the Trello card to `In_Progress`

**Verify:**
- Bean directory exists at `ai/beans/BEAN-NNN-<slug>/`
- `bean.md` has `## Trello` section with `Source: Trello` and correct Card ID
- `_index.md` has the new bean
- Card is in In_Progress list (use `mcp__trello__get_cards_by_list_id` with In_Progress list ID `698ffb2c55500d7d5415f5c9`)

### Step 3: Observe bean execution

The long-run should pick the bean, decompose it, execute the wave, and mark it Done.

**Verify:**
- `bean.md` status is `Done`
- `_index.md` status is `Done`
- Feature branch was merged to `test`

### Step 4: Confirm Trello completion

After the merge, the long-run's merge captain (step 17b) should:
1. Read the `## Trello` section from `bean.md`
2. Find the Card ID
3. Call `mcp__trello__move_card` to move it to the Completed list

**Verify:**
- Card is in Completed list (use `mcp__trello__get_cards_by_list_id` with Completed list ID `698ffb28d291200db3ff61fb`)
- Card is no longer in In_Progress

## Known Gaps

1. **No automated test**: The procedure is manual. Automated testing would require mocking the Trello MCP server, which is out of scope for this bean.
2. **Card without description**: Cards imported without descriptions produce beans with `(Trello card had no description.)` in the Notes section. This is correct behavior but means the bean's Problem Statement is derived from the card title only.
3. **Best-effort Trello moves**: Both the import (card → In_Progress) and completion (card → Completed) moves are best-effort. If the Trello MCP is down, the bean lifecycle continues but the card stays in its current list. There is no retry mechanism.
4. **No In_Progress → Sprint_Backlog rollback**: If a bean fails mid-execution and stays `In Progress`, the Trello card remains in In_Progress. There is no mechanism to move it back to Sprint_Backlog.

## Validated Example

BEAN-154 (Trello Test) successfully completed the full lifecycle on 2026-02-17:
- Card created in Sprint_Backlog → imported as BEAN-154 → moved to In_Progress
- Bean processed through Developer → Tech-QA wave
- Bean marked Done → card moved to Completed

This confirms the pipeline works end-to-end.
