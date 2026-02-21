# SQL Query Performance

Diagnosing and resolving slow queries. PostgreSQL is the primary reference;
SQL Server equivalents noted where relevant.

---

## Defaults

- **Always explain before optimizing.** Run `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` to see the actual execution plan.
- **Measure, don't guess.** Slow-query logs and `pg_stat_statements` are the starting point.
- **Optimize the plan, not the syntax.** Rewriting SQL is pointless if the planner already produces the same plan.
- **Connection pooling:** Required for any application with more than 10 concurrent connections. Use PgBouncer or built-in pooling.

---

## Reading EXPLAIN Output

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT o.order_id, c.full_name, o.total_cents
FROM app.orders o
JOIN app.customers c ON c.customer_id = o.customer_id
WHERE o.status = 'pending'
  AND o.ordered_at > now() - interval '7 days';
```

**Key things to look for:**

| Indicator            | Healthy                        | Problem                          |
|----------------------|--------------------------------|----------------------------------|
| Scan type            | Index Scan, Index Only Scan    | Seq Scan on large table          |
| Rows estimated vs actual | Within 10x                 | Off by 100x+ (stale stats)      |
| Buffers shared hit   | High hit ratio                 | Lots of shared read (cache miss) |
| Sort method          | quicksort, Memory             | external merge (disk sort)       |
| Loops                | 1 (or low)                     | 10000+ (nested loop on big set)  |

---

## Common Optimization Patterns

### 1. Replace Seq Scan with Index Scan

```sql
-- Before: Seq Scan because no index on status + ordered_at
-- Cost: 85000.00  Rows: 150000  Actual time: 420ms

-- Fix: add a targeted partial index
CREATE INDEX idx_orders_pending_recent
    ON app.orders (ordered_at DESC)
    WHERE status = 'pending';

-- After: Index Scan using idx_orders_pending_recent
-- Cost: 12.50  Rows: 342  Actual time: 0.8ms
```

### 2. Eliminate N+1 with JOIN or Lateral

```sql
-- Bad: application issues 1000 separate queries (N+1)
-- SELECT * FROM orders WHERE customer_id = ?;  (repeated per customer)

-- Good: single query with JOIN
SELECT c.customer_id, c.full_name, o.order_id, o.total_cents
FROM app.customers c
JOIN app.orders o ON o.customer_id = c.customer_id
WHERE c.region = 'us-east';

-- Good: LATERAL for "top N per group"
SELECT c.customer_id, c.full_name, recent.*
FROM app.customers c
CROSS JOIN LATERAL (
    SELECT o.order_id, o.total_cents, o.ordered_at
    FROM app.orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY o.ordered_at DESC
    LIMIT 3
) recent
WHERE c.region = 'us-east';
```

---

## Do / Don't

- **Do** enable `pg_stat_statements` in every PostgreSQL instance. It is the single most valuable performance tool.
- **Do** run `ANALYZE` after bulk data loads to update planner statistics.
- **Do** use `LIMIT` with `ORDER BY` to avoid sorting the entire result set.
- **Do** use CTEs for readability but understand they are optimization fences in PostgreSQL < 12 (inlined in 12+).
- **Do** batch inserts (`INSERT INTO ... VALUES (...), (...), (...)`) instead of row-by-row.
- **Don't** use `SELECT *` in production queries. List only the columns you need.
- **Don't** wrap indexed columns in functions (`WHERE YEAR(ordered_at) = 2025`). Use range conditions instead (`WHERE ordered_at >= '2025-01-01' AND ordered_at < '2026-01-01'`).
- **Don't** use `OFFSET` for deep pagination. Use keyset pagination (`WHERE id > last_seen_id ORDER BY id LIMIT 20`).
- **Don't** rely on implicit type casts. `WHERE bigint_col = '123'` forces a cast on every row in some engines.
- **Don't** tune `work_mem` or `shared_buffers` without understanding the workload. Defaults are conservative but safe.

---

## Common Pitfalls

1. **Stale statistics.** `EXPLAIN` estimates wildly off from actual rows. Fix: `ANALYZE <table>` or check autovacuum is running.
2. **Implicit sequential scans.** `OR` conditions and functions on indexed columns prevent index use. Rewrite as `UNION ALL` or expression indexes.
3. **Correlated subqueries.** `WHERE EXISTS (SELECT ... WHERE outer.id = inner.id)` can be fine, but `SELECT (SELECT ... ) FROM ...` in the SELECT list re-executes per row. Rewrite as JOIN.
4. **Lock contention, not slow query.** A query appears slow but is actually waiting on a lock. Check `pg_stat_activity` for `wait_event_type = 'Lock'`.
5. **Connection exhaustion.** 200 application threads each opening a direct connection. Use PgBouncer in transaction mode.
6. **Deep OFFSET pagination.** `OFFSET 100000` still scans and discards 100K rows. Switch to keyset/cursor pagination.

### Alternatives

| Tool                    | Purpose                                      |
|-------------------------|----------------------------------------------|
| `pg_stat_statements`    | Top queries by total time, calls, rows       |
| `auto_explain`          | Log plans for slow queries automatically     |
| `pgBadger`              | Log analysis and report generation           |
| `PgBouncer`             | Connection pooling for PostgreSQL            |
| SQL Server Query Store  | Equivalent of pg_stat_statements for MSSQL   |

---

## Checklist

- [ ] `pg_stat_statements` enabled and reviewed weekly
- [ ] Slow query log threshold set (e.g., `log_min_duration_statement = 500ms`)
- [ ] `EXPLAIN ANALYZE` run for every query taking > 100ms
- [ ] No `SELECT *` in production application queries
- [ ] Pagination uses keyset pattern, not `OFFSET`
- [ ] Bulk operations use multi-row `INSERT` or `COPY`
- [ ] `ANALYZE` runs after bulk data loads
- [ ] Connection pooling in place (PgBouncer or equivalent)
- [ ] No functions wrapping indexed columns in `WHERE` clauses
- [ ] CTE vs subquery performance verified on PostgreSQL < 12 workloads
