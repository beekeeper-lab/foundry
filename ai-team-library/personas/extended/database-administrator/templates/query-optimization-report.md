# Query Optimization Report

| Field | Value |
|-------|-------|
| **Report ID** | QOR-NNN |
| **Date** | YYYY-MM-DD |
| **Author** | Database Administrator |
| **Severity** | Critical / Major / Minor |
| **Status** | Identified / In Progress / Resolved |
| **Affected System** | _Application or service name_ |

## Problem Statement

_Describe the performance issue. Include how it was detected (monitoring alert, user report, Developer request)._

## Original Query

```sql
-- The underperforming query
SELECT ...
```

**Context:** _Where this query is called, how often, and under what conditions._

## Current Execution Plan

```
-- EXPLAIN ANALYZE output
...
```

**Key observations:**
- _e.g., Full table scan on `orders` (2.1M rows)_
- _e.g., Nested loop join with no index on `user_id`_
- _e.g., Sort operation spilling to disk_

## Root Cause Analysis

_Explain why the query is slow. Reference specific execution plan nodes._

## Proposed Optimizations

### Option 1: _Description_

```sql
-- New index, query rewrite, or configuration change
...
```

**Expected improvement:** _e.g., Rows scanned reduced from 2.1M to 450_
**Trade-offs:** _e.g., Index adds ~50MB storage, marginal write overhead_
**Effort:** Low / Medium / High

### Option 2: _Description_ (if applicable)

```sql
...
```

**Expected improvement:** _..._
**Trade-offs:** _..._
**Effort:** Low / Medium / High

## Recommendation

_Which option to implement and why._

## Before/After Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Execution time | _ms_ | _ms_ | _% reduction_ |
| Rows scanned | _count_ | _count_ | _% reduction_ |
| I/O cost | _units_ | _units_ | _% reduction_ |
| Buffer hits | _count_ | _count_ | _change_ |

## Side Effects

_Document any impact on other queries, write performance, or storage._

## Implementation Steps

1. _Step-by-step instructions for applying the fix_
2. _..._
