# SQL Database Security

Security practices for relational databases covering access control, encryption,
auditing, and defense against common attacks. PostgreSQL primary; SQL Server secondary.

---

## Defaults

- **Principle of least privilege.** Every role gets the minimum permissions needed. No application connects as a superuser.
- **Authentication:** `scram-sha-256` (PostgreSQL) or Windows Authentication / Azure AD (SQL Server). Never `trust` or `md5` in production.
- **Encryption in transit:** TLS required for all connections. Reject plaintext.
- **Encryption at rest:** Transparent Data Encryption (TDE) or volume-level encryption on all production instances.
- **Secrets management:** Connection strings with credentials stored in a vault (HashiCorp Vault, AWS Secrets Manager), never in application config files.

---

## Role and Privilege Design

```sql
-- 1. Create application-specific roles, not individual user logins
CREATE ROLE app_readonly;
CREATE ROLE app_readwrite;
CREATE ROLE app_admin;

-- 2. Grant schema-level permissions
GRANT USAGE ON SCHEMA app TO app_readonly, app_readwrite;

GRANT SELECT ON ALL TABLES IN SCHEMA app TO app_readonly;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO app_readwrite;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app TO app_readwrite;

-- 3. Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA app
    GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA app
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

-- 4. Create login roles and assign to groups
CREATE ROLE myapp_service LOGIN PASSWORD 'rotated-by-vault';
GRANT app_readwrite TO myapp_service;

CREATE ROLE analyst_jane LOGIN PASSWORD 'rotated-by-vault';
GRANT app_readonly TO analyst_jane;
```

---

## Row-Level Security (RLS)

```sql
-- Tenants can only see their own data
ALTER TABLE app.orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON app.orders
    USING (tenant_id = current_setting('app.current_tenant')::bigint);

-- Force RLS even for table owners (critical for multi-tenant)
ALTER TABLE app.orders FORCE ROW LEVEL SECURITY;

-- Set the tenant context at connection time (in the application)
-- SET app.current_tenant = '42';
```

---

## Do / Don't

- **Do** use parameterized queries / prepared statements exclusively. This is the single most important defense against SQL injection.
- **Do** rotate database passwords on a schedule (90 days max) via automated secrets management.
- **Do** restrict network access to the database port (5432/1433) with firewall rules. No public internet exposure.
- **Do** enable audit logging (`pgAudit` for PostgreSQL, SQL Server Audit).
- **Do** use `ALTER DEFAULT PRIVILEGES` so new tables automatically inherit role grants.
- **Do** separate read and write roles. Reporting tools get read-only access.
- **Don't** grant `SUPERUSER` or `sysadmin` to application roles. Ever.
- **Don't** store plaintext passwords in application config or environment variable files committed to version control.
- **Don't** use `SECURITY DEFINER` functions without explicit `SET search_path`.
- **Don't** disable TLS for "convenience" in staging. Staging should mirror production security.
- **Don't** grant `CREATE` on `public` schema in PostgreSQL (revoked by default in PG 15+).

---

## Common Pitfalls

1. **SQL injection via string concatenation.** Even in admin scripts and migrations, use parameterized queries. Concatenating user input into DDL statements is a common backdoor.
2. **Over-privileged migration runner.** The migration role needs `CREATE TABLE` / `ALTER TABLE`, but should NOT have `SUPERUSER`. Use a dedicated migration role with schema-level DDL grants.
3. **Forgotten `ALTER DEFAULT PRIVILEGES`.** Granting `SELECT` on all current tables misses future tables. Always add default privilege grants.
4. **`pg_hba.conf` allows `trust` locally.** Local socket connections with `trust` mean any OS user can connect as any DB user. Use `scram-sha-256` for all entries.
5. **Backup files unencrypted.** `pg_dump` output sitting on an unencrypted volume is a data breach waiting to happen. Encrypt backups at rest and in transit.
6. **Search path manipulation.** A malicious user creates a function in `public` schema with the same name as a system function. Set `search_path` explicitly in functions and roles.

### Alternatives

| Tool / Feature     | Purpose                                          |
|--------------------|--------------------------------------------------|
| `pgAudit`          | Detailed audit logging for PostgreSQL            |
| HashiCorp Vault    | Dynamic database credential rotation             |
| AWS Secrets Manager| Managed secrets for RDS connections               |
| `pg_hba.conf`      | Connection authentication rules (PostgreSQL)     |
| SQL Server TDE     | Transparent data encryption at rest              |
| `sslmode=verify-full` | Strongest TLS verification for PostgreSQL clients |

---

## Checklist

- [ ] Application connects with a dedicated, least-privilege role (not superuser)
- [ ] Authentication uses `scram-sha-256` (PG) or integrated auth (SQL Server)
- [ ] TLS required for all connections; plaintext rejected in `pg_hba.conf`
- [ ] Credentials stored in a secrets vault, not config files
- [ ] Passwords rotated on schedule (90 days max)
- [ ] `ALTER DEFAULT PRIVILEGES` set for all application schemas
- [ ] Read-only and read-write roles separated
- [ ] Row-level security enabled for multi-tenant tables
- [ ] Audit logging enabled (`pgAudit` or SQL Server Audit)
- [ ] Database port not exposed to the public internet
- [ ] Backups encrypted at rest and in transit
- [ ] `SECURITY DEFINER` functions use explicit `SET search_path`
- [ ] All application queries use parameterized statements (no string concatenation)
