# Escalation Workflows

Defined processes for routing customer issues that exceed the current tier's
authority, expertise, or SLA. Escalation is not failure — it is the mechanism
that ensures the right people handle the right problems at the right time.

---

## Defaults

| Setting | Default | Alternatives |
|---------|---------|--------------|
| **Escalation tiers** | 3 tiers (L1 → L2 → L3) | 2 tiers (simple), 4 tiers (enterprise) |
| **Trigger model** | SLA-based + manual | Severity-based, customer-tier-based |
| **SLA for L1 response** | 4 hours (business hours) | 1 hour (premium), 8 hours (standard) |
| **SLA for L2 response** | 2 hours | 1 hour (critical), 4 hours (standard) |
| **SLA for L3 response** | 1 hour | 30 minutes (P0/P1 incidents) |
| **Notification method** | Automated + Slack/PagerDuty | Email, ticketing system only |

---

## Escalation Tiers

### Tier 1 — Front-Line Support

Handles known issues, how-to questions, and standard troubleshooting. Equipped
with runbooks, knowledge base access, and common resolution scripts. Escalates
when the issue is outside documented procedures or exceeds the response SLA.

### Tier 2 — Specialist Support

Domain experts with deeper product and technical knowledge. Handles complex
configuration issues, integration problems, and bugs that require investigation.
Escalates when the issue requires code changes, infrastructure access, or
executive involvement.

### Tier 3 — Engineering / Executive

Engineers who can diagnose and fix code-level issues. Executive escalation for
contractual, legal, or high-severity business impact. Reserved for production
incidents, security issues, and situations where customer retention is at risk.

---

## Escalation Triggers

### Automatic Triggers (SLA-Based)

When a ticket approaches or breaches its SLA, the system automatically escalates
to the next tier. No human judgment required — the clock is the trigger.

### Manual Triggers (Judgment-Based)

The agent determines the issue exceeds their tier's capability. Criteria include:
requires access they do not have, requires knowledge outside their domain, or the
customer has explicitly requested escalation.

### Severity-Based Triggers

Certain issue types bypass lower tiers entirely. Production outages, security
incidents, and data loss go directly to Tier 3 regardless of the normal flow.

---

## Do / Don't

- **Do** define clear escalation criteria for each tier so agents do not have to
  guess whether to escalate.
- **Do** transfer context with the escalation. The receiving tier should never
  ask the customer to repeat information already provided.
- **Do** notify the customer when their issue is escalated, including the new
  expected response time.
- **Do** track escalation rates by tier, category, and agent. High escalation
  rates from L1 signal a training or tooling gap.
- **Do** conduct post-escalation reviews for L3 issues to identify patterns and
  improve lower-tier resolution capability.
- **Don't** allow "ping-pong" escalations where a ticket bounces between tiers
  without resolution. Once escalated, the receiving tier owns it.
- **Don't** use escalation as a queue dump. Every escalation must include the
  reason, context, and what has already been tried.
- **Don't** let escalation paths bypass the ticketing system. Shadow escalations
  via Slack DMs or email lose tracking and accountability.
- **Don't** set SLAs you cannot meet. Unrealistic SLAs cause teams to game
  metrics rather than improve service.

---

## Common Pitfalls

1. **No context transfer.** The customer explains their issue to L1, gets
   escalated, and L2 asks the same questions. Solution: require a structured
   escalation note (symptom, steps tried, customer impact, account context)
   attached to every escalated ticket.
2. **Escalation as avoidance.** L1 agents escalate to avoid difficult
   conversations rather than lack of capability. Solution: review escalation
   reasons monthly. Coach agents on issues they should be resolving at their
   tier.
3. **No de-escalation path.** Issues escalated to L3 stay at L3 even after the
   critical phase is resolved. Solution: define de-escalation criteria. Once the
   fix is deployed, follow-up and monitoring return to the appropriate lower
   tier.
4. **SLA clock games.** Agents close and reopen tickets to reset the SLA timer.
   Solution: track SLA compliance on original creation time, not last update.
   Audit ticket state transitions.
5. **Executive escalation used as first resort.** Customers learn that
   threatening to escalate gets faster service, so they always do it. Solution:
   ensure L1 and L2 response times are fast enough that executive escalation is
   rarely needed. Reserve it for genuinely severe situations.

---

## Escalation Workflow Configuration

```yaml
# Escalation Workflow Definition
escalation:
  tiers:
    - level: 1
      name: "Front-Line Support"
      team: support-generalists
      capabilities:
        - known_issues
        - how_to_questions
        - account_management
        - password_resets
      sla:
        first_response: 4h
        resolution_target: 24h
      escalation_criteria:
        - "Issue not in runbook or knowledge base"
        - "Resolution requires backend access"
        - "Customer requests escalation"
        - "SLA at 75% elapsed without resolution path"

    - level: 2
      name: "Specialist Support"
      team: support-specialists
      capabilities:
        - complex_configuration
        - integration_troubleshooting
        - bug_investigation
        - data_queries
      sla:
        first_response: 2h
        resolution_target: 8h
      escalation_criteria:
        - "Issue requires code change"
        - "Production environment impact"
        - "Security-related issue"
        - "SLA at 75% elapsed without resolution path"

    - level: 3
      name: "Engineering / Executive"
      team: engineering-oncall
      capabilities:
        - code_fixes
        - infrastructure_changes
        - incident_management
        - executive_communication
      sla:
        first_response: 1h
        resolution_target: 4h

  severity_overrides:
    - severity: P0
      description: "Production outage affecting all customers"
      route_to: 3
      notification: pagerduty
    - severity: P1
      description: "Production degradation or data integrity issue"
      route_to: 3
      notification: slack_oncall
    - severity: P2
      description: "Feature broken for subset of customers"
      route_to: 2
      notification: slack_channel
```

---

## Escalation Note Template

```yaml
# Required fields when escalating a ticket
escalation_note:
  ticket_id: "SUP-12345"
  escalated_from: L1
  escalated_to: L2
  escalated_by: "agent@company.com"
  timestamp: "2026-02-15T14:30:00Z"

  customer_context:
    account: "Acme Corp"
    tier: enterprise
    health_score: 72
    arr: "$120,000"
    primary_contact: "jane@acme.com"

  issue:
    summary: "SSO login fails intermittently with SAML assertion error"
    symptoms:
      - "Users see 'Invalid SAML response' error 30% of login attempts"
      - "Started after customer updated their IdP certificate"
    customer_impact: "50+ users unable to reliably access the platform"
    business_impact: "Customer has executive review next week, threatening churn"

  steps_taken:
    - "Verified customer IdP metadata is current"
    - "Checked SAML assertion logs — certificate mismatch on some requests"
    - "Asked customer to re-upload certificate — issue persists"
    - "Consulted runbook SSO-003 — no matching resolution"

  escalation_reason: "Requires backend investigation of SAML certificate caching"
  suggested_next_step: "Check if platform is caching the old IdP certificate"
```

---

## Alternatives

| Approach | When to consider |
|----------|-----------------|
| Swarming model | Replace tiered escalation with collaborative, real-time resolution |
| Customer-tier routing | Route enterprise customers directly to L2, skip L1 |
| AI-assisted triage | Use ML to classify and route tickets before human review |
| Follow-the-sun support | Global teams hand off by timezone instead of escalating |
| Self-service escalation portal | Let customers set severity and trigger escalation directly |

---

## Checklist

- [ ] Escalation tiers defined with clear capabilities and boundaries
- [ ] SLAs set for each tier (first response and resolution target)
- [ ] Automatic escalation triggers configured for SLA breach
- [ ] Manual escalation criteria documented and trained
- [ ] Severity overrides defined (P0/P1 bypass lower tiers)
- [ ] Escalation note template enforced (context, steps tried, impact)
- [ ] Customer notification sent on escalation with updated timeline
- [ ] De-escalation criteria defined to return issues to lower tiers
- [ ] Escalation metrics tracked (rate, time-to-escalate, resolution time)
- [ ] Monthly review of escalation patterns to improve L1/L2 resolution
