# SQL Indexing

Indexing strategies for relational databases. PostgreSQL is the primary reference;
SQL Server equivalents noted where they differ.

---

## Defaults

- **Every foreign key column** gets a B-tree index.
- **Every column in a `WHERE` clause** that filters large tables is an index candidate.
- **Composite indexes** follow the left-prefix rule: put the most selective column first.
- **Covering indexes** (`INCLUDE` columns) preferred over wide composite indexes when only a few extra columns are needed.
- **Partial indexes** used for filtered queries on a subset of rows.

---

## Index Types

| Type       | PostgreSQL         | SQL Server        | Best For                          |
|------------|--------------------|-------------------|-----------------------------------|
| B-tree     | Default            | Default (clustered/nonclustered) | Equality, range, ORDER BY |
| Hash       | `USING hash`       | N/A               | Equality only, rarely used        |
| GIN        | `USING gin`        | N/A               | JSONB, full-text, arrays          |
| GiST       | `USING gist`       | Spatial index      | Geometric, range types, PostGIS   |
| BRIN       | `USING brin`       | N/A               | Large, naturally ordered tables   |
| Filtered   | `WHERE` clause     | `WHERE` clause    | Subset of rows                    |

---

## Practical Examples

### Composite Index (Left-Prefix Rule)

```sql
-- Query: find active orders for a customer, sorted by date
-- WHERE customer_id = ? AND status = 'active' ORDER BY ordered_at DESC

CREATE INDEX idx_orders_customer_status_date
    ON app.orders (customer_id, status, ordered_at DESC);

-- This index serves:
--   WHERE customer_id = ?                                  (uses first column)
--   WHERE customer_id = ? AND status = ?                   (uses first two)
--   WHERE customer_id = ? AND status = ? ORDER BY ordered_at DESC (uses all three)
-- It does NOT efficiently serve:
--   WHERE status = ?                                       (skips first column)
```

### Covering Index with INCLUDE

```sql
-- Query fetches customer_id, total_cents, ordered_at for a list page
-- Avoid heap lookups by including non-key columns

CREATE INDEX idx_orders_status_covering
    ON app.orders (status)
    INCLUDE (customer_id, total_cents, ordered_at);

-- PostgreSQL 11+ / SQL Server 2005+
-- The INCLUDE columns are stored in the leaf pages but not in the tree,
-- so they don't affect sort order but do enable index-only scans.
```

### Partial Index

```sql
-- Only 2% of orders are 'pending'. Full index wastes space on the other 98%.
CREATE INDEX idx_orders_pending
    ON app.orders (ordered_at)
    WHERE status = 'pending';

-- Queries MUST include the matching WHERE clause to use this index:
-- SELECT * FROM app.orders WHERE status = 'pending' ORDER BY ordered_at;
```

---

## Do / Don't

- **Do** check `EXPLAIN (ANALYZE, BUFFERS)` output before and after adding an index.
- **Do** use partial indexes for columns with skewed value distributions.
- **Do** use `INCLUDE` columns to enable index-only scans on frequently queried fields.
- **Do** drop unused indexes. Query `pg_stat_user_indexes` for `idx_scan = 0`.
- **Do** rebuild bloated indexes periodically (`REINDEX CONCURRENTLY` in PostgreSQL 12+).
- **Don't** index every column. Each index adds write overhead and storage.
- **Don't** create overlapping indexes (e.g., `(a)` and `(a, b)` -- the composite covers single-column lookups on `a`).
- **Don't** use hash indexes for anything other than exact equality on large values.
- **Don't** forget that `NULL` values are indexed in B-tree. A partial index excluding nulls saves space.

---

## Common Pitfalls

1. **Missing FK indexes.** This is the single most common performance problem in PostgreSQL databases. Add them at table creation time.
2. **Wrong column order in composite index.** The left-prefix rule means `(a, b, c)` cannot serve `WHERE b = ?`. Put the equality columns first, range columns last.
3. **Over-indexing OLTP tables.** More than 5-6 indexes on a write-heavy table causes noticeable insert/update slowdowns. Measure before adding.
4. **Expression indexes forgotten.** If you query `WHERE lower(email) = ?`, a plain index on `email` is useless. Create `CREATE INDEX ... ON ... (lower(email))`.
5. **Index bloat after bulk deletes.** Dead tuples in indexes are not reclaimed until `VACUUM` or `REINDEX`. Monitor `pg_stat_user_indexes` for bloat.
6. **Covering index too wide.** Including many large columns in `INCLUDE` defeats the purpose. Only include columns actually returned by the query.

### Alternatives

| Tool                        | Purpose                                  |
|-----------------------------|------------------------------------------|
| `pg_stat_user_indexes`      | Find unused indexes (idx_scan = 0)       |
| `pgstatindex()`             | Measure index bloat                      |
| `EXPLAIN (ANALYZE, BUFFERS)`| Verify index is used and effective        |
| `hypopg`                    | Hypothetical indexes without creating them|
| SQL Server DMVs             | `sys.dm_db_index_usage_stats` for usage  |

---

## Checklist

- [ ] All foreign key columns have B-tree indexes
- [ ] Composite indexes follow left-prefix rule (equality columns first)
- [ ] Partial indexes used for skewed distributions (e.g., `WHERE status = 'pending'`)
- [ ] Covering indexes (`INCLUDE`) used for high-frequency read queries
- [ ] No overlapping/redundant indexes
- [ ] Unused indexes identified and dropped (check `pg_stat_user_indexes`)
- [ ] Expression indexes created for queries using functions (`lower()`, `jsonb_extract_path()`)
- [ ] `EXPLAIN ANALYZE` run for every new index to verify it is used
- [ ] Index count per table reviewed: 5-6 max on write-heavy tables
- [ ] Index maintenance scheduled (`REINDEX CONCURRENTLY` or equivalent)
