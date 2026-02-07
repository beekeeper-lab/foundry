# SQL Database Operations

Day-to-day operational practices: migrations, backups, monitoring, maintenance,
and disaster recovery. PostgreSQL primary; SQL Server secondary.

---

## Defaults

- **Migrations:** Versioned, forward-only SQL files managed by a migration tool. Never apply DDL by hand.
- **Backups:** Automated daily full backups + continuous WAL archiving (PostgreSQL) or log shipping (SQL Server). Tested monthly.
- **Monitoring:** `pg_stat_activity`, `pg_stat_user_tables`, and alerting on connections, replication lag, and disk usage.
- **Maintenance:** Autovacuum enabled and tuned. Never disable it.
- **Change management:** All schema changes go through code review in a migration file. No ad-hoc DDL in production.

---

## Migration Workflow

```sql
-- migrations/0042_add_shipping_address.sql
-- Migration: Add shipping address columns to orders table
-- Author: jane.doe
-- Date: 2025-01-15

BEGIN;

ALTER TABLE app.orders
    ADD COLUMN shipping_street  text,
    ADD COLUMN shipping_city    text,
    ADD COLUMN shipping_country text NOT NULL DEFAULT 'US';

-- Backfill from customer default address (safe for < 1M rows)
UPDATE app.orders o
SET shipping_street  = c.default_street,
    shipping_city    = c.default_city,
    shipping_country = c.default_country
FROM app.customers c
WHERE c.customer_id = o.customer_id
  AND o.shipping_street IS NULL;

COMMIT;
```

```sql
-- For large tables, use batched updates to avoid long locks:
DO $$
DECLARE
    batch_size int := 10000;
    rows_updated int;
BEGIN
    LOOP
        UPDATE app.orders o
        SET shipping_street = c.default_street
        FROM app.customers c
        WHERE c.customer_id = o.customer_id
          AND o.shipping_street IS NULL
          AND o.order_id IN (
              SELECT order_id FROM app.orders
              WHERE shipping_street IS NULL
              LIMIT batch_size
              FOR UPDATE SKIP LOCKED
          );

        GET DIAGNOSTICS rows_updated = ROW_COUNT;
        RAISE NOTICE 'Updated % rows', rows_updated;
        EXIT WHEN rows_updated = 0;

        COMMIT;
    END LOOP;
END $$;
```

---

## Backup and Recovery

| Strategy              | PostgreSQL                      | SQL Server                        |
|-----------------------|---------------------------------|-----------------------------------|
| Full backup           | `pg_basebackup`                | Full database backup              |
| Point-in-time recovery| WAL archiving + `restore_command`| Transaction log backups           |
| Logical backup        | `pg_dump` / `pg_dumpall`       | `bcp` / BACPAC                    |
| Continuous archiving  | `archive_mode = on`, pgBackRest| Log shipping, Always On AG        |
| Cloud-managed         | RDS automated snapshots         | Azure SQL automated backups       |

**Rules:**
- Full backup daily. WAL archiving continuous.
- Store backups in a different region/account from the database.
- Test restores monthly. A backup you have never restored is not a backup.
- Retention: 30 days minimum, 90 days for compliance-sensitive data.
- Encrypt backups at rest.

---

## Do / Don't

- **Do** use a migration tool (`alembic`, `flyway`, `dbmate`, `sqitch`) for all schema changes.
- **Do** wrap migrations in transactions when the DDL supports it (PostgreSQL: yes, MySQL: no).
- **Do** test every migration on a copy of production data before applying to production.
- **Do** monitor autovacuum. Tables with high update/delete rates may need per-table tuning.
- **Do** set up alerting for: disk > 80%, replication lag > 30s, connections > 80% of `max_connections`, long-running queries > 5 min.
- **Do** use `CREATE INDEX CONCURRENTLY` to avoid locking the table during index creation.
- **Don't** run DDL without a migration file. No `psql` ad-hoc `ALTER TABLE` in production.
- **Don't** skip backup restore tests. Corrupt or incomplete backups are discovered only when you need them.
- **Don't** disable autovacuum to "reduce load." This causes table and index bloat, eventually making performance worse.
- **Don't** run `VACUUM FULL` in production. It takes an `ACCESS EXCLUSIVE` lock. Use `pg_repack` for online table compaction.
- **Don't** apply large data backfills inside a single transaction. Use batched updates.

---

## Monitoring Queries

```sql
-- Active long-running queries (PostgreSQL)
SELECT pid, now() - query_start AS duration, state, query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '1 minute'
ORDER BY duration DESC;

-- Table bloat and vacuum stats
SELECT
    schemaname || '.' || relname AS table_name,
    n_dead_tup,
    n_live_tup,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

---

## Common Pitfalls

1. **Locking DDL during peak hours.** `ALTER TABLE ... ADD COLUMN ... DEFAULT` rewrites the table in PostgreSQL < 11. In PG 11+ non-volatile defaults are instant, but `NOT NULL` with a backfill still locks. Schedule large DDL during low-traffic windows.
2. **WAL archiving silently failing.** If `archive_command` fails, WAL segments accumulate and fill the disk, crashing the database. Monitor `pg_stat_archiver` for `failed_count > 0`.
3. **Untested restores.** The team discovers the backup is corrupt at 3 AM during an incident. Automate monthly restore tests to a staging instance.
4. **Autovacuum too slow for high-churn tables.** Default autovacuum settings are tuned for average workloads. Tables with millions of updates/day need per-table `autovacuum_vacuum_scale_factor` tuning.
5. **Forgotten connection limits.** Default `max_connections = 100` in PostgreSQL. An application with 20 pods each opening 10 connections exhausts this. Use PgBouncer.
6. **Ignoring replication lag.** Read replicas falling behind means stale reads in the application. Alert on lag and route reads to primary if lag exceeds threshold.

### Alternatives

| Tool                | Purpose                                    |
|---------------------|--------------------------------------------|
| `pgBackRest`        | Production-grade PostgreSQL backup/restore |
| `Barman`            | PostgreSQL backup management by EnterpriseDB |
| `pg_repack`         | Online table/index compaction without locks|
| `flyway` / `dbmate` | SQL-based migration runners                |
| `Alembic`           | Python-native migrations (SQLAlchemy)      |
| `pgBouncer`         | Connection pooling for PostgreSQL          |
| `check_postgres`    | Nagios-compatible monitoring checks        |

---

## Checklist

- [ ] All schema changes applied via versioned migration files
- [ ] Migrations tested on a production-data copy before deployment
- [ ] `CREATE INDEX CONCURRENTLY` used for all production index creation
- [ ] Daily full backups + continuous WAL archiving configured
- [ ] Backup restore tested monthly on a staging instance
- [ ] Backups stored in a separate region/account, encrypted at rest
- [ ] Autovacuum running and monitored; high-churn tables tuned
- [ ] Monitoring alerts set: disk, connections, replication lag, long queries
- [ ] Connection pooling in place for applications
- [ ] Disaster recovery runbook documented and rehearsed quarterly
- [ ] No ad-hoc DDL applied to production outside the migration workflow
