---
id: sql-dba
category: Data & ML
entry: true
last-reviewed: 2026-07
---

# SQL DBA Conventions

## Category
Data & ML

These conventions cover relational schema design, indexing, query performance,
operations, and security. PostgreSQL is the primary reference; SQL Server
equivalents are noted in the sibling files where they differ.

---

## Defaults

| Concern | Default |
|---------|---------|
| Naming | `snake_case`, plural table names, `_id` suffix on keys |
| Primary keys | `bigint GENERATED ALWAYS AS IDENTITY` (not `serial`); UUID only for distributed ID generation |
| Foreign keys | Always defined, always indexed on the child side |
| Timestamps | `timestamptz` (PG) / `datetimeoffset` (SQL Server) — never timezone-naive |
| Nullability | `NOT NULL` by default; `NULL` requires documented justification |
| Money | `bigint` (cents) or `numeric(19,4)` — never float |
| Schemas | Named schemas (`app.`, `audit.`) with per-schema grants; nothing in `public`/`dbo` |
| Indexing | B-tree on every FK column; composite indexes follow the left-prefix rule |
| Migrations | Versioned, forward-only SQL files via a tool (`flyway`, `alembic`, `dbmate`); no ad-hoc DDL |
| Backups | Daily full + continuous WAL archiving; restores tested monthly |
| Connection pooling | Required above 10 concurrent connections (PgBouncer) |
| Authentication | `scram-sha-256` (PG) / integrated auth (SQL Server); TLS required |
| Queries | Parameterized statements exclusively — no string concatenation |

---

## 1. Schema Design

- Every table has an explicit primary key. No exceptions.
- Normalize first; denormalize only with measured proof and a documented
  trade-off (e.g., a scheduled materialized view for a dashboard).
- Use `CHECK` constraints for domain rules (status enums, positive amounts).
- Add `created_at`/`updated_at` to every mutable table; prefer `archived_at`
  timestamps over `is_deleted` flags.
- Prefer `text` over `varchar(n)` in PostgreSQL unless the length limit is a
  business rule; prefer JSONB over EAV for dynamic attributes.

Full detail: `schema-design.md`

---

## 2. Indexing

- Missing FK indexes are the single most common PostgreSQL performance problem —
  add them at table creation time.
- Composite indexes: equality columns first, range columns last (left-prefix
  rule — `(a, b, c)` cannot serve `WHERE b = ?`).
- Use partial indexes for skewed distributions (`WHERE status = 'pending'`) and
  `INCLUDE` columns for index-only scans; create expression indexes for queries
  like `WHERE lower(email) = ?`.
- Cap write-heavy tables at ~5-6 indexes; drop unused ones
  (`pg_stat_user_indexes` with `idx_scan = 0`) and avoid overlapping indexes.
- Verify every new index with `EXPLAIN (ANALYZE, BUFFERS)` before and after.

Full detail: `indexing.md`

---

## 3. Query Performance

- Always explain before optimizing: `EXPLAIN (ANALYZE, BUFFERS)`; start from
  `pg_stat_statements` and slow-query logs, not guesses.
- Red flags in plans: Seq Scan on large tables, estimates off by 100x+ (stale
  stats — run `ANALYZE`), external merge sorts, huge nested-loop counts.
- Never wrap indexed columns in functions — use range conditions
  (`ordered_at >= '2025-01-01' AND ordered_at < '2026-01-01'`).
- Use keyset pagination, not deep `OFFSET`; batch inserts, no row-by-row.
- No `SELECT *` in production queries; eliminate N+1 with JOIN or LATERAL.

Full detail: `query-performance.md`

---

## 4. Operations

- All schema changes go through versioned migration files with code review;
  test every migration on a production-data copy first.
- Large backfills run in batches (`LIMIT ... FOR UPDATE SKIP LOCKED`), never
  one giant transaction; use `CREATE INDEX CONCURRENTLY` in production.
- Never disable autovacuum; tune per-table for high-churn tables. Never run
  `VACUUM FULL` in production — use `pg_repack`.
- A backup you have never restored is not a backup: test restores monthly,
  store backups encrypted in a separate region/account, retain 30-90 days.
- Alert on: disk > 80%, replication lag > 30s, connections > 80% of max,
  long-running queries > 5 min, `pg_stat_archiver` failures.

Full detail: `operations.md`

---

## 5. Security

- Least privilege: application roles never get `SUPERUSER`/`sysadmin`;
  separate read-only and read-write group roles.
- Use `ALTER DEFAULT PRIVILEGES` so future tables inherit grants — granting on
  existing tables alone misses new ones.
- Credentials live in a secrets vault with scheduled rotation (90 days max),
  never in config files committed to version control.
- Enable row-level security (with `FORCE`) for multi-tenant tables; enable
  audit logging (`pgAudit` / SQL Server Audit).
- `SECURITY DEFINER` functions must set an explicit `search_path`; database
  ports are never exposed to the public internet.

Full detail: `security.md`

---

## Do / Don't

**Do:**
- Define and index every foreign key.
- Use parameterized queries everywhere, including admin scripts and migrations.
- Run `ANALYZE` after bulk loads and check plans with `EXPLAIN ANALYZE`.
- Wrap migrations in transactions where the engine supports it (PostgreSQL: yes).
- Pool connections with PgBouncer for any real application load.

**Don't:**
- Apply ad-hoc DDL to production outside the migration workflow.
- Store money as float or timestamps without timezone.
- Create tables without a primary key, or nullable columns without justification.
- Grant `CREATE` on `public`, or connect applications as superuser.
- Skip backup restore tests — corruption is discovered only when you need them.

---

## Common Pitfalls

1. **Missing FK indexes** — PostgreSQL does not auto-index `REFERENCES` columns;
   joins fall back to sequential scans.
2. **Wrong composite index order** — violating the left-prefix rule makes the
   index useless for the intended query.
3. **Locking DDL at peak hours** — `NOT NULL` backfills and table rewrites take
   heavy locks; schedule and batch them.
4. **Connection exhaustion** — many app instances × direct connections blow past
   `max_connections`; pool with PgBouncer.
5. **WAL archiving silently failing** — segments accumulate until the disk fills
   and the database crashes; monitor `pg_stat_archiver`.
6. **Implicit casts and stale statistics** — both silently disable index use;
   match types exactly and keep autovacuum/`ANALYZE` healthy.

---

## Checklist

- [ ] Every table has a PK; every FK is defined and indexed on the child side
- [ ] `timestamptz` everywhere; money as `bigint` cents or `numeric`
- [ ] `NOT NULL` default; `CHECK` constraints enforce domain rules
- [ ] Composite indexes follow the left-prefix rule; no overlapping indexes
- [ ] `pg_stat_statements` enabled; `EXPLAIN ANALYZE` for queries > 100ms
- [ ] Keyset pagination; no `SELECT *`; no functions on indexed columns in WHERE
- [ ] All DDL via versioned migrations; `CREATE INDEX CONCURRENTLY` in prod
- [ ] Daily backups + WAL archiving; restore tested monthly; encrypted at rest
- [ ] Alerts on disk, replication lag, connections, and long-running queries
- [ ] Least-privilege roles, vault-managed credentials, TLS-only connections
- [ ] RLS on multi-tenant tables; audit logging enabled
- [ ] Parameterized statements only — no string-concatenated SQL
