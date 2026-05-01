# Architecture Review: [Prospect Name] -- Integration Assessment

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Sales Engineer| [Name]                         |
| Prospect      | [Prospect company name]        |
| Reviewed by   | [Architect / technical reviewer] |
| Status        | Draft / Reviewed / Delivered   |

*Customer-facing architecture diagram and integration guide. Shows how the product fits into the prospect's existing environment. No internal infrastructure details.*

---

## Customer Environment Summary

- **Cloud provider:** [e.g., AWS, Azure, GCP, On-premises]
- **Application stack:** [e.g., Java/Spring, .NET, Node.js]
- **Database:** [e.g., PostgreSQL, Oracle, SQL Server]
- **Identity provider:** [e.g., Okta, Azure AD, Auth0]
- **Existing integrations:** [Key systems the product must connect to]
- **Compliance requirements:** [e.g., SOC 2, HIPAA, GDPR]

---

## Integration Architecture

```
[ASCII or Mermaid diagram showing the integration topology]

+-------------------+          +-------------------+
|  Customer App     |  REST    |  Our Product      |
|  (Spring Boot)    |<-------->|  (API Gateway)    |
+-------------------+  HTTPS   +-------------------+
        |                              |
        v                              v
+-------------------+          +-------------------+
|  Customer DB      |          |  Product DB       |
|  (PostgreSQL)     |          |  (managed)        |
+-------------------+          +-------------------+
        |
        v
+-------------------+
|  Identity (Okta)  |
|  SAML 2.0         |
+-------------------+
```

---

## Integration Points

| # | Integration | Protocol | Direction | Authentication | Data Format |
|---|-------------|----------|-----------|---------------|-------------|
| 1 | [e.g., User sync] | [e.g., REST API] | [e.g., Bidirectional] | [e.g., OAuth 2.0 client credentials] | [e.g., JSON] |
| 2 | [e.g., Event notifications] | [e.g., Webhook] | [e.g., Product → Customer] | [e.g., HMAC signature] | [e.g., JSON] |
| 3 | [e.g., SSO] | [e.g., SAML 2.0] | [e.g., Customer IdP → Product SP] | [e.g., X.509 certificate] | [e.g., XML assertion] |

---

## Data Flow

| Flow | Source | Destination | Frequency | Volume | Sensitivity |
|------|--------|-------------|-----------|--------|-------------|
| [e.g., User provisioning] | [Customer HR system] | [Our product] | [Real-time via SCIM] | [~100 users/month] | [PII -- names, emails] |
| [e.g., Activity export] | [Our product] | [Customer data warehouse] | [Daily batch] | [~10K records/day] | [Anonymized usage data] |

---

## Security Boundaries

| Boundary | Controls | Notes |
|----------|----------|-------|
| [e.g., Network ingress] | [e.g., IP allowlist, WAF, TLS 1.2+] | [Customer provides IP ranges] |
| [e.g., Data at rest] | [e.g., AES-256 encryption, customer-managed keys available] | [Meets their compliance requirement] |
| [e.g., Data in transit] | [e.g., TLS 1.2+ for all connections] | [Certificate pinning available] |

---

## Deployment Topology

| Component | Location | Configuration | SLA |
|-----------|----------|--------------|-----|
| [e.g., API Gateway] | [e.g., US-East-1] | [e.g., Multi-AZ, auto-scaling] | [e.g., 99.9% uptime] |
| [e.g., Database] | [e.g., US-East-1] | [e.g., Multi-AZ, daily backups] | [e.g., RPO 1hr, RTO 4hr] |

---

## Prerequisites & Assumptions

| # | Assumption | Impact if Wrong | Validation Step |
|---|-----------|----------------|-----------------|
| 1 | [e.g., Customer uses Okta as sole IdP] | [e.g., SSO integration needs redesign] | [e.g., Confirm in discovery call] |
| 2 | [e.g., Customer allows outbound HTTPS to our endpoints] | [e.g., Webhook integration blocked] | [e.g., Network team review] |

---

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | [e.g., Does the customer require data residency in EU?] | [Sales Engineer] | [Pending] |
