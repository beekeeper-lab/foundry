# Prioritized Backlog

## Metadata

| Field          | Value                          |
|----------------|--------------------------------|
| **Date**       | [YYYY-MM-DD]                   |
| **Owner**      | [Product Owner name]           |
| **Last Reviewed** | [YYYY-MM-DD]               |
| **Framework**  | RICE / MoSCoW / Weighted Scoring |

## Prioritization Framework

_Document the scoring methodology used._

### RICE Scoring Scale

| Factor | Scale | Description |
|--------|-------|-------------|
| **Reach** | [Number of users/events per quarter] | How many users will this impact? |
| **Impact** | 0.25 (Minimal) / 0.5 (Low) / 1 (Medium) / 2 (High) / 3 (Massive) | How much will this impact each user? |
| **Confidence** | 50% (Low) / 80% (Medium) / 100% (High) | How confident are we in the estimates? |
| **Effort** | [Person-weeks] | How much work is required? |

_RICE Score = (Reach × Impact × Confidence) / Effort_

## Backlog

| # | Title | Type | Value Statement | Reach | Impact | Confidence | Effort | RICE | Segment | Dependencies |
|---|-------|------|-----------------|-------|--------|------------|--------|------|---------|--------------|
| 1 | [Item title] | [Feature / Enhancement / Debt / Bug] | [Why this matters] | [N] | [0.25–3] | [50–100%] | [N weeks] | [Score] | [Target users] | [Blocking items] |

## Pruning Log

_Items removed from the backlog during review._

| Date | Item | Reason |
|------|------|--------|
| [YYYY-MM-DD] | [Item title] | [Why it was removed: superseded, no longer relevant, insufficient value] |

## Definition of Done

- [ ] Every item has a documented RICE score with rationale
- [ ] Top-quarter items have clear value propositions and success metrics
- [ ] Items are categorized by type (feature, enhancement, debt, bug)
- [ ] Dependencies between items are identified
- [ ] Stale items (no movement in 2+ cycles) are reviewed and pruned or re-justified
- [ ] Effort estimates are validated with the delivery team
