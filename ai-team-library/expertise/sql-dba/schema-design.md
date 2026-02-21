# SQL Schema Design

Principles and patterns for relational database schema design. PostgreSQL is the
primary reference; SQL Server differences noted where significant.

---

## Defaults

- **Naming:** `snake_case` for all identifiers. Plural table names (`orders`, not `order`).
- **Primary keys:** `bigint` identity/generated columns. UUID only when distributed ID generation is required.
- **Foreign keys:** Always defined. Always indexed on the referencing (child) side.
- **Timestamps:** `timestamptz` (PostgreSQL) / `datetimeoffset` (SQL Server). Never store local time without a timezone.
- **Nullability:** Columns are `NOT NULL` by default. Allow `NULL` only with documented justification.
- **Schema:** Use named schemas (`app.`, `audit.`) to organize tables. Do not dump everything in `public`/`dbo`.

---

## Normalization vs Denormalization

Normalize first. Denormalize only when you have measured proof that read performance
requires it, and document the trade-off.

```sql
-- Normalized: separate tables, single source of truth
CREATE TABLE app.customers (
    customer_id  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email        text   NOT NULL UNIQUE,
    full_name    text   NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app.orders (
    order_id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  bigint NOT NULL REFERENCES app.customers (customer_id),
    total_cents  bigint NOT NULL CHECK (total_cents >= 0),
    status       text   NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'confirmed', 'shipped', 'cancelled')),
    ordered_at   timestamptz NOT NULL DEFAULT now()
);

-- Index on FK column for join performance
CREATE INDEX idx_orders_customer_id ON app.orders (customer_id);
```

```sql
-- Denormalized: only when read pattern demands it and you accept write complexity
-- Example: materialized view for a dashboard that queries millions of rows
CREATE MATERIALIZED VIEW reporting.customer_order_summary AS
SELECT
    c.customer_id,
    c.full_name,
    count(o.order_id)         AS order_count,
    coalesce(sum(o.total_cents), 0) AS lifetime_value_cents
FROM app.customers c
LEFT JOIN app.orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name;

-- Refresh on a schedule, not on every write
-- REFRESH MATERIALIZED VIEW CONCURRENTLY reporting.customer_order_summary;
```

---

## Do / Don't

- **Do** use `CHECK` constraints for domain validation (status enums, positive amounts).
- **Do** add `created_at` and `updated_at` columns on every mutable table.
- **Do** use `text` over `varchar(n)` in PostgreSQL unless a hard length limit is a business rule.
- **Do** define foreign keys. They are documentation, correctness enforcement, and query planner hints.
- **Do** put related tables in the same schema and grant permissions per schema.
- **Don't** use `serial` in new PostgreSQL code. Use `GENERATED ALWAYS AS IDENTITY`.
- **Don't** store money as `float`/`double`. Use `bigint` (cents) or `numeric(19,4)`.
- **Don't** create an `is_deleted` soft-delete column without also adding a partial index and filtering it in every query. Prefer an `archived_at` timestamp.
- **Don't** use EAV (Entity-Attribute-Value) unless you are building a truly dynamic schema. JSONB is almost always better.
- **Don't** create tables without a primary key. Ever.

---

## Common Pitfalls

1. **Missing FK indexes.** PostgreSQL does not auto-index foreign keys. Every `REFERENCES` column needs a manual index or joins on that column do sequential scans.
2. **Over-indexing.** Every index slows writes. Add indexes based on measured query patterns, not "just in case."
3. **Nullable unique columns.** PostgreSQL treats each `NULL` as distinct in unique indexes. Use a partial unique index if you want `UNIQUE WHERE col IS NOT NULL`.
4. **Implicit casting.** Comparing `bigint` column to `text` input silently casts and prevents index use. Match types exactly.
5. **Premature denormalization.** Adding computed columns and summary tables before measuring creates maintenance burden with no proven benefit.
6. **Timezone-naive timestamps.** `timestamp` (without tz) combined with application servers in different zones leads to data corruption.

---

## Checklist

- [ ] All tables have an explicit primary key
- [ ] All foreign keys are defined and indexed on the child side
- [ ] Money stored as `bigint` (cents) or `numeric`, never float
- [ ] Timestamps use `timestamptz` / `datetimeoffset`
- [ ] `NOT NULL` is the default; nullability is justified in comments
- [ ] `CHECK` constraints enforce domain rules (status values, positive amounts)
- [ ] Tables organized into named schemas with per-schema grants
- [ ] `created_at` / `updated_at` present on mutable tables
- [ ] Denormalization documented with the query pattern that justifies it
- [ ] Naming is consistent: `snake_case`, plural tables, `_id` suffix on keys
