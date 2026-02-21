# Demo Environment Management

Practices for building, maintaining, and delivering technical demonstrations
that win deals. A demo environment is not a staging server — it is a curated
experience designed to prove value in a prospect's specific context. Treat demo
infrastructure with the same rigor as production, because a crashed demo loses
more revenue than a crashed staging server.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Environment type** | Dedicated per-prospect sandbox with seeded data | Shared multi-tenant demo instance with tenant isolation |
| **Infrastructure** | Containerized (Docker Compose) on cloud VMs, spun up on demand | Kubernetes-based ephemeral namespaces; local laptop demo for offline scenarios |
| **Data strategy** | Synthetic data tailored to prospect's industry vertical | Anonymized production data subset; auto-generated via Faker/factories |
| **Lifecycle** | Spin up 24h before demo, tear down 48h after unless follow-up scheduled | Persistent always-on instance for high-value, long-cycle deals |
| **Reset mechanism** | One-click reset script restoring database snapshots and config | Infrastructure-as-code full redeploy; database migration rollback |
| **Access control** | Time-limited credentials shared via secure link (1Password, Doppler) | SSO integration with prospect's IdP for extended evaluations |
| **Monitoring** | Basic health checks (HTTP 200, DB connectivity) with Slack alerts | Full observability (metrics, logs, traces) for complex enterprise demos |

---

## Environment Architecture

A well-structured demo environment separates concerns and enables rapid
customization per prospect.

```
┌─────────────────────────────────────────────┐
│  Demo Environment                           │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Frontend │  │ Backend  │  │ Database │  │
│  │ (branded)│→ │  (API)   │→ │ (seeded) │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                             │
│  ┌──────────┐  ┌──────────┐                 │
│  │ Mock     │  │ Config   │                 │
│  │ Services │  │ (YAML)   │                 │
│  └──────────┘  └──────────┘                 │
│                                             │
│  Provisioned via: Terraform / Docker Compose│
│  Data seed: industry-specific fixtures      │
│  Reset: ./scripts/reset-demo.sh             │
└─────────────────────────────────────────────┘
```

### Data Seeding Strategy

| Industry | Sample Data | Key Scenarios |
|----------|------------|---------------|
| **Financial services** | Mock portfolios, transactions, compliance alerts | Risk dashboard, audit trail, regulatory reporting |
| **Healthcare** | Synthetic patient records (HIPAA-safe), appointment schedules | Care coordination, HL7/FHIR integration, analytics |
| **Retail/E-commerce** | Product catalogs, order histories, customer segments | Recommendation engine, inventory management, analytics |
| **SaaS/Technology** | User accounts, usage metrics, billing records | Onboarding flow, usage analytics, admin console |

---

## Demo Runbook

Execute this checklist before every demo:

| Step | Action | Timing |
|------|--------|--------|
| 1 | Provision environment (or verify existing) | T-24h |
| 2 | Seed prospect-specific data | T-24h |
| 3 | Customize branding (logo, colors, terminology) | T-24h |
| 4 | Run smoke tests against all demo scenarios | T-4h |
| 5 | Verify network/VPN connectivity from demo location | T-2h |
| 6 | Prepare fallback (screenshots, recorded video) | T-2h |
| 7 | Clear browser cache, close unrelated tabs | T-15min |
| 8 | Test screen sharing and audio | T-10min |

---

## Do / Don't

- **Do** build demo environments from infrastructure-as-code so they are
  reproducible. A demo that works only on one engineer's laptop is a liability.
- **Do** seed data that mirrors the prospect's domain. Generic placeholder data
  ("Acme Corp", "John Doe") signals that you did not prepare.
- **Do** maintain a library of industry-specific data sets. Reuse saves hours
  and improves quality over time.
- **Do** have a one-click reset script. Demos go sideways; recovery speed
  determines whether the deal survives.
- **Do** record every demo session (with prospect consent). Recordings feed
  win/loss analysis and onboard new SEs faster.
- **Do** test the exact demo flow end-to-end the day before. "It worked
  yesterday" is not a test plan.
- **Don't** demo on production. One accidental data mutation can create a
  customer-facing incident during your sales call.
- **Don't** leave demo environments running indefinitely. Orphaned instances
  accumulate cost and security risk.
- **Don't** hard-code credentials or API keys in demo scripts. Rotate secrets
  and use environment variables.
- **Don't** skip the fallback plan. Network failures, API outages, and browser
  crashes happen. Have screenshots or a recorded walkthrough ready.
- **Don't** over-customize. A demo that takes 2 days to set up for every
  prospect does not scale. Build a configurable template, not bespoke instances.

---

## Common Pitfalls

1. **"It works on my machine" syndrome.** The SE demos from a local laptop with
   cached state and the prospect cannot reproduce the experience. Solution: use
   cloud-hosted, reproducible environments provisioned from code.
2. **Stale data.** The demo database has not been updated since the product
   added new features, so new screens show empty states. Solution: version data
   seeds alongside the application and update them with each release.
3. **Environment drift.** Demo environments diverge from the actual product
   because they are not kept in sync with mainline. Solution: build demo
   environments from the same CI/CD pipeline as staging.
4. **Over-scoped demo.** The SE tries to show every feature in 60 minutes and
   rushes through what matters. Solution: limit demo scenarios to the 3–5 use
   cases from the discovery call.
5. **No recovery plan.** A feature breaks mid-demo and the SE freezes.
   Solution: practice graceful recovery — acknowledge the issue, pivot to
   another scenario, and follow up with a fix.
6. **Credential sprawl.** Demo accounts accumulate across prospects with no
   tracking or rotation. Solution: automate credential lifecycle — create on
   provision, rotate weekly, destroy on teardown.

---

## Checklist

- [ ] Demo environment is provisioned from infrastructure-as-code
- [ ] Data is seeded with prospect-relevant, industry-specific content
- [ ] Branding and terminology are customized for the prospect
- [ ] One-click reset script is tested and functional
- [ ] Smoke tests cover all planned demo scenarios
- [ ] Fallback materials (screenshots, video) are prepared
- [ ] Credentials are securely shared and time-limited
- [ ] Environment teardown is scheduled post-demo
- [ ] Demo flow is rehearsed end-to-end within 24 hours of the call
- [ ] Recording consent is obtained and session is captured
