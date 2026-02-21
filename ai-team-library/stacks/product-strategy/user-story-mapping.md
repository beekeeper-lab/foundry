# User Story Mapping

A visual technique for organizing user stories into a two-dimensional map that
reveals the user's journey, identifies the minimum viable product, and guides
release planning. Story mapping replaces flat backlogs with a structured view
that preserves narrative flow and user context.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Map format** | Physical sticky notes on a wall or Miro/FigJam board | Dedicated tools (StoriesOnBoard, Avion) for persistent digital maps |
| **Backbone granularity** | User activities (high-level goals) → user tasks (steps within activities) | Epics → features for teams already using epic-level planning |
| **Vertical axis** | Priority / sophistication (top = essential, bottom = nice-to-have) | Effort or sprint assignment for execution-focused teams |
| **Release slicing** | Horizontal lines drawn across the map to define release boundaries | Colored tags per release for digital maps |
| **Participation** | Cross-functional workshop (PM, design, engineering, QA) | PM-led draft with async review for distributed teams |
| **Cadence** | One mapping session per major initiative; updated as scope evolves | Quarterly refresh for long-running products |
| **Story detail level** | Title + brief acceptance criteria on the card | Full user story format ("As a… I want… So that…") for complex domains |

---

## Map Structure

```
Activities:   [Browse Catalog]      [Add to Cart]       [Checkout]        [Track Order]
               (user goal)          (user goal)         (user goal)       (user goal)
                    |                    |                   |                  |
Tasks:         Search items         Select size         Enter address     View status
               Filter results       Set quantity        Choose payment    Get notifications
               View details         Save for later      Apply coupon      Request return
                    |                    |                   |                  |
                    v                    v                   v                  v
─── Release 1 (MVP) ────────────────────────────────────────────────────────────────
               Search items         Select size         Enter address     View status
               View details         Set quantity        Choose payment
                                                        (card only)
─── Release 2 ──────────────────────────────────────────────────────────────────────
               Filter results       Save for later      Apply coupon      Get notifications
─── Release 3 ──────────────────────────────────────────────────────────────────────
               Recommendations                          Multi-payment     Request return
                                                        (PayPal, etc.)
```

---

## Process

### Step 1: Frame the Journey

1. Define the **target user persona** (who is doing the activity?)
2. Write the **user's big goal** at the top (e.g., "Purchase a product online")
3. List **activities** (high-level steps) left to right in chronological order
4. These activities form the **backbone** — the horizontal spine of the map

### Step 2: Discover Tasks

For each activity, brainstorm the **tasks** the user performs:

1. Walk through the activity step by step — "What does the user do first? Then what?"
2. Write each task on a card and place it vertically below its parent activity
3. Arrange tasks top to bottom by priority (most essential at the top)
4. Include alternative paths and edge cases lower on the map

### Step 3: Slice Releases

Draw horizontal lines across the map to define release boundaries:

1. **Walking skeleton (Release 1):** The minimum set of tasks that creates an
   end-to-end functional path. The user can complete their goal, even if roughly.
2. **Release 2–N:** Add sophistication, polish, edge case handling, and alternative
   flows in each subsequent release.

### Step 4: Validate and Iterate

1. Walk the map with stakeholders and real users
2. Challenge each card: "Is this essential for Release 1 or can it wait?"
3. Look for gaps: "What happens if the user does X instead of Y?"
4. Update the map as you learn from development and user feedback

---

## Do / Don't

- **Do** start with the user's narrative, not a feature list. The backbone is a
  journey, not a set of components.
- **Do** include the whole cross-functional team in the mapping session. Engineers
  catch technical constraints; designers catch UX gaps; QA catches edge cases.
- **Do** keep the walking skeleton ruthlessly thin. It proves the concept end-to-end
  without polish. Every additional card in Release 1 delays learning.
- **Do** use the map as a communication tool. Post it visibly. Reference it in
  sprint planning. It is the shared understanding of scope.
- **Do** revisit and update the map as scope evolves. A stale map is worse than
  no map — it creates false confidence.
- **Do** timebox the mapping workshop (2–4 hours). Diminishing returns set in quickly.
- **Don't** turn the map into a detailed specification. Cards should be conversation
  starters, not requirements documents.
- **Don't** skip the backbone step and jump straight to writing stories. Without
  the narrative structure, you get a flat backlog with no context.
- **Don't** let the map become a wish list. Every card below the first release line
  is explicitly deferred, not promised.
- **Don't** map alone. A single person's map reflects a single perspective. The
  value is in the shared discovery during the workshop.
- **Don't** confuse activities with tasks. "Checkout" is an activity (a goal).
  "Enter shipping address" is a task (a step within the goal).

---

## Common Pitfalls

1. **Backbone too granular.** Writing 20 activities when 5–7 cover the journey.
   The backbone should fit on one wall or screen. Solution: merge activities that
   are substeps of the same goal.
2. **Release 1 bloat.** Stakeholders push "must-have" features into Release 1 until
   it is no longer minimum. Solution: apply the walking skeleton test — can the
   user complete their goal end-to-end? If yes, everything else is Release 2+.
3. **Map-and-forget.** The team builds the map, takes a photo, and never looks at it
   again. Solution: make the map the primary planning artifact. Reference it in
   every sprint planning session.
4. **Mapping features instead of user tasks.** "Admin panel" and "API layer" are
   system features, not user tasks. Solution: always ask "What is the user trying
   to do?" and map from their perspective.
5. **No vertical prioritization.** All tasks under an activity are at the same level
   with no ranking. Solution: physically arrange cards top-to-bottom by necessity.
   The top card is the simplest version; cards below add sophistication.
6. **Ignoring alternative paths.** The map only covers the happy path. Real users
   encounter errors, change their mind, and use features in unexpected ways.
   Solution: explicitly add alternative and error paths as lower-priority tasks.

---

## Checklist

- [ ] Target user persona is defined before mapping begins
- [ ] Activities (backbone) are arranged left to right in chronological order
- [ ] Tasks are arranged vertically under each activity by priority
- [ ] Cross-functional team participated in the mapping session
- [ ] Walking skeleton (Release 1) is identified with a horizontal line
- [ ] Walking skeleton passes the end-to-end test (user can complete their goal)
- [ ] Subsequent releases are sliced with clear boundaries
- [ ] Alternative paths and edge cases are included (below the main flow)
- [ ] The map is posted visibly and referenced in planning sessions
- [ ] The map is updated as scope evolves during development
