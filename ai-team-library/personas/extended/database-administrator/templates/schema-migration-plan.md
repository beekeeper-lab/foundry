# Schema Migration Plan

| Field | Value |
|-------|-------|
| **Migration ID** | MIG-NNN |
| **Title** | _Imperative description of the change_ |
| **Author** | Database Administrator |
| **Date** | YYYY-MM-DD |
| **Status** | Draft / Reviewed / Approved / Deployed / Rolled Back |
| **Affects Tables** | _List of tables modified_ |
| **Breaking Change** | Yes / No |
| **Estimated Execution Time** | _Duration for production dataset_ |

## Context

_Why is this migration needed? Reference the task, story, or design decision that requires the schema change._

## Change Description

_What is being changed at a high level. Include before/after schema diagrams or table definitions if helpful._

## Forward Migration (Up)

```sql
-- Migration: MIG-NNN Up
-- Description: ...

BEGIN;

-- DDL changes
-- ...

-- Data migration (if applicable)
-- ...

COMMIT;
```

## Rollback Migration (Down)

```sql
-- Migration: MIG-NNN Down
-- Description: Reverses MIG-NNN

BEGIN;

-- Reverse DDL changes
-- ...

-- Reverse data migration (if applicable)
-- ...

COMMIT;
```

## Data Migration Notes

_If existing rows need transformation, describe the approach, expected row counts, and handling of edge cases (NULLs, duplicates, constraint violations)._

- **Rows affected:** _estimated count_
- **NULL handling:** _strategy_
- **Default values:** _what defaults are applied and why_

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| _MIG-NNN-1_ | Must run before | _Reason_ |
| _Application release X.Y_ | Must deploy after | _Reason_ |

## Breaking Changes

_If this migration is a breaking change, describe:_
- What breaks and why
- Compatibility window (how long old and new schemas can coexist)
- Phased rollout plan

## Testing

- [ ] Tested on empty database
- [ ] Tested on database with representative data
- [ ] Rollback tested successfully
- [ ] Application verified against new schema
- [ ] Performance verified (no unexpected lock times or timeouts)

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| _Long lock time on large table_ | _Medium_ | _High_ | _Run during maintenance window_ |

## Rollback Trigger

_Under what conditions should this migration be rolled back? Define the criteria._
