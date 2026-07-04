---
id: devops
category: Infrastructure & Platforms
entry: true
last-reviewed: 2026-07
---

# DevOps Conventions

## Category
Infrastructure & Platforms

Standards for environments, CI/CD pipelines, secrets, releases, and
observability. Infrastructure is defined as code, every release is repeatable
and reversible, and no secret ever exists in source code, logs, or unencrypted
storage. Deviations require an ADR.

---

## Defaults

| Concern              | Default Tool / Approach                                  |
|----------------------|----------------------------------------------------------|
| Environments         | `dev` (continuous deploy) → `staging` (pre-prod mirror) → `prod` (gated approval) |
| IaC tool             | Terraform, remote state (S3/GCS) with state locking      |
| CI/CD platform       | GitHub Actions (self-hosted runners for builds > 10 min) |
| Artifact format      | Container images tagged with git SHA + semver            |
| Promotion            | Build once, promote the same artifact — never rebuild per environment |
| Versioning           | Semantic Versioning; annotated git tags from `main` trigger prod releases |
| Changelog            | Auto-generated from conventional commits                 |
| Rollback             | Redeploy previous known-good artifact within 5 minutes   |
| Secrets store        | HashiCorp Vault (app secrets), GitHub Secrets (CI/CD)    |
| CI cloud auth        | OIDC federation — no static cloud credentials            |
| Secret rotation      | Scheduled, 90 days max; immediate on compromise          |
| Telemetry            | OpenTelemetry (traces, metrics, logs), OTLP export       |
| Health checks        | `/healthz` (liveness) + `/readyz` (readiness) on every service |
| Alerting             | Alert on symptoms (error rate, latency), not causes; every alert links a runbook |

---

## 1. Environments

- Define every environment in Terraform (or equivalent IaC). No ClickOps;
  manual environment changes are forbidden.
- Staging mirrors production in topology, network rules, and resource sizing
  (scaled down where cost-prohibitive). It is a production rehearsal, not a
  testing playground.
- Parameterize environment-specific values (URLs, scaling, feature flags)
  through variables, not code branches.
- Each environment owns its own data stores and credentials. No production
  database access from non-production environments.
- Use ephemeral preview environments per PR with automated teardown (TTL +
  reaper job); no long-lived feature environments.
- Detect drift with scheduled `terraform plan` in CI (daily minimum).

Full detail: `environments.md`

---

## 2. CI/CD Pipelines

- Pipeline definitions live in the repo alongside the code they build. PRs run
  build + test; push to `main` deploys staging; `v*` tags deploy production.
- Pin action versions to a full commit SHA, not a mutable tag.
- Separate lint, unit test, build, integration test, and deploy into distinct
  jobs with explicit `needs:` dependencies. Recommended order:
  `checkout → install → lint → unit-test → build → integration-test → publish → deploy`.
- Every job has an explicit `timeout-minutes` (default cap 15 min); use
  `concurrency` groups to cancel superseded runs.
- Cache dependencies (pip/npm/Docker layers). Deploy jobs use GitHub
  Environments with protection rules; never run deploy steps in a PR pipeline.
- Quarantine flaky tests with a label and fix within one sprint or delete —
  never mask instability with `retry`.

Full detail: `pipelines.md`

---

## 3. Releases and Rollback

- Enforce conventional commits (`feat:`, `fix:`, `chore:`, `breaking:`);
  automate version calculation and changelog generation from commit history.
- Tag releases from `main` only, with annotated tags. Retain at least the last
  10 container image versions for rollback.
- Deploy production with canary or blue-green strategy; run smoke tests
  automatically after every deployment.
- Rollback deploys the previous known-good artifact — it does not revert
  commits or cherry-pick fixes under pressure. Test rollback in staging before
  every production release.
- Database migrations follow expand → migrate → contract so code can always
  roll back without schema conflicts. Never combine infrastructure changes and
  application changes in one release.
- Hotfixes still go through staging, with expedited approval.

Full detail: `release-runbook.md`

---

## 4. Secrets Management

- Application runtime secrets come from a secrets manager (Vault, AWS Secrets
  Manager, Azure Key Vault) — fetched at runtime, never baked into images.
- CI/CD authenticates to cloud providers via OIDC federation; prefer
  short-lived tokens and dynamic secrets over long-lived API keys.
- Scope secrets to the narrowest access possible (environment, job, repo);
  never share the same secret value across environments.
- Never commit secrets ("temporarily" included), pass them as CLI arguments,
  or log them — mask CI output with `::add-mask::`.
- Scan for leaked secrets with gitleaks (pre-commit hook + CI on every PR).
- Encrypt Terraform state at rest and restrict access — state files contain
  secret values. Audit every secret read.

Full detail: `secrets.md`

---

## 5. Observability

- Instrument with the OpenTelemetry SDK from day one; retrofitting is
  expensive. Propagate trace context (W3C headers) across service boundaries.
- Structured JSON logging in production; every log line includes `trace_id`,
  `service_name`, `environment`. INFO is the production baseline — no DEBUG.
- Define SLIs and SLOs for every user-facing service; dashboard the four
  golden signals (latency, traffic, errors, saturation) and use burn-rate
  alerts against the error budget.
- Start with three alerts per service (error rate, p99 latency, availability);
  add more only after an incident that would have been caught earlier.
- Keep metric labels low-cardinality — high-cardinality data (user IDs,
  request IDs) belongs in traces, not metrics.
- Readiness checks verify downstream dependencies (database, cache, critical
  APIs); a health check that always returns 200 checks nothing.

Full detail: `observability.md`

---

## Do / Don't

**Do:**
- Define every environment in version-controlled IaC and require manual
  approval gates for production deploys.
- Build once and promote the identical artifact through each environment.
- Pin CI action versions to commit SHAs and set explicit job timeouts.
- Use OIDC federation for CI-to-cloud auth and a secrets manager at runtime.
- Automate version bumps and changelogs from conventional commits.
- Run smoke tests automatically after every deployment.

**Don't:**
- Make manual ("ClickOps") environment changes or treat staging as a playground.
- Rebuild artifacts per environment — that is promotion by rebuilding.
- Commit secrets, log them, or pass them as command-line arguments.
- Release on Fridays or before holidays unless it is a critical hotfix.
- Use `continue-on-error: true` without a documented reason.
- Create alerts nobody acts on — every alert must have a runbook link.

---

## Common Pitfalls

1. **Environment drift.** Staging diverges from production via manual changes.
   Enforce IaC-only changes; run scheduled `terraform plan` drift detection.
2. **Promotion by rebuilding.** Per-environment builds introduce subtle
   differences. Build once, promote the identical artifact.
3. **No rollback plan.** Irreversible migrations make rollback impossible after
   a failed deploy. Use expand/migrate/contract and test rollback in staging.
4. **Secrets in git history.** A committed `.env` lives in history forever.
   `.gitignore` from day one plus gitleaks pre-commit and CI scanning.
5. **Secrets baked into Docker images.** Build args/ENV persist in layers.
   Mount secrets at runtime; use BuildKit secret mounts for build-time needs.
6. **Alert fatigue.** Too many alerts, all ignored. Start with three per
   service and expand only from real incident gaps.
7. **Metrics cardinality explosion.** `user_id` as a metric label creates
   millions of time series. High-cardinality data goes in traces.

---

## Checklist

- [ ] All environments defined in IaC; Terraform state remote with locking
- [ ] Each environment has isolated data stores and credentials
- [ ] Same artifact promoted dev → staging → prod; no per-environment rebuilds
- [ ] Production deploys require explicit manual approval
- [ ] CI runs on PRs and `main`; actions pinned to SHAs; jobs have timeouts
- [ ] Artifacts tagged with git SHA for provenance
- [ ] Conventional commits enforced; version and changelog auto-generated
- [ ] Canary or blue-green production deploys; rollback executable in 5 minutes
- [ ] Migrations backward-compatible (expand/migrate/contract)
- [ ] CI/CD uses OIDC federation; runtime secrets from a secrets manager
- [ ] Secret scanning (gitleaks) in pre-commit and CI; rotation automated
- [ ] OpenTelemetry initialized; logs carry `trace_id`, `service_name`, `environment`
- [ ] `/healthz` and `/readyz` implemented; readiness checks dependencies
- [ ] SLOs defined; alerts fire on symptoms and link to runbooks
- [ ] Smoke tests run automatically after every deployment
