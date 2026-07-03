# Architecture Decision Records Index

## Metadata

| Field         | Value                                       |
|---------------|---------------------------------------------|
| Date          | [YYYY-MM-DD]                                |
| Owner         | [Name / role maintaining the ADR index]      |
| Related links | [ADR folder path, contributing guide]        |
| Status        | Draft / Reviewed / Approved                 |

## How to Create a New ADR

*Follow these steps when a significant architectural decision is made.*

1. Copy the ADR template from [template location]
2. Assign the next sequential number (see table below)
3. Fill in all sections: context, decision, consequences
4. Set status to **Proposed**
5. Submit for review via [PR / review process]
6. Once accepted, update status to **Accepted** and add to the table below

**When to write an ADR**: Any decision that affects system structure, technology choices, integration patterns, data models, or cross-team interfaces.

## ADR Registry

| ADR # | Title | Status | Date | Decision Maker | Summary |
|-------|-------|--------|------|----------------|---------|
| [001] | [Decision title] | Proposed / Accepted / Superseded / Deprecated | [YYYY-MM-DD] | [Name or role] | [One-sentence summary of the decision] |
| [002] | [Decision title] | [Status] | [YYYY-MM-DD] | [Name or role] | [Summary] |
| [003] | [Decision title] | [Status] | [YYYY-MM-DD] | [Name or role] | [Summary] |

## Statistics

*Update these counts when adding or changing ADRs.*

| Metric | Count |
|--------|-------|
| Total ADRs | [n] |
| Accepted | [n] |
| Proposed | [n] |
| Superseded | [n] |
| Deprecated | [n] |

## Notes

- Superseded ADRs should reference the ADR that replaces them
- Deprecated ADRs should note the reason for deprecation
- ADRs are immutable once accepted -- create a new ADR to change a prior decision

## Definition of Done

- [ ] All architectural decisions are captured as ADRs
- [ ] Each ADR has a unique sequential number
- [ ] Index table is up to date with all ADRs
- [ ] Statistics reflect current counts
- [ ] Superseded ADRs reference their replacements
