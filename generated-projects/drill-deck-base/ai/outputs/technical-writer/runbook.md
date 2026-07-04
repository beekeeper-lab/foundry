# Runbook: [Service Name]

## Metadata

| Field         | Value                                       |
|---------------|---------------------------------------------|
| Date          | [YYYY-MM-DD]                                |
| Owner         | [On-call team / service owner]               |
| Related links | [Architecture docs, monitoring dashboards]   |
| Status        | Draft / Reviewed / Approved                 |

## Service Overview

- **Service name**: [Name]
- **Owner / On-call**: [Team or rotation name]
- **Purpose**: [One-sentence description of what the service does]
- **Architecture**: [Brief description of components, dependencies, and data flow]

## Health Checks

| Endpoint / Check | Method | Expected Response | Notes |
|-----------------|--------|-------------------|-------|
| [/health] | [GET] | [200 OK with body] | [What a healthy response looks like] |
| [/ready] | [GET] | [200 OK] | [Readiness vs. liveness distinction] |

## Common Operations

*Procedures for routine tasks. Include the exact steps so anyone on-call can execute them.*

| Operation | When to Use | Steps |
|-----------|-------------|-------|
| [Restart service] | [Service unresponsive after health check failure] | [1. Step one 2. Step two 3. Verify with health check] |
| [Scale up] | [High latency or resource saturation] | [1. Step one 2. Step two 3. Monitor metrics] |
| [Rotate credentials] | [Scheduled rotation or suspected compromise] | [1. Generate new credentials 2. Update config 3. Restart 4. Verify] |
| [Clear cache] | [Stale data causing incorrect behavior] | [1. Step one 2. Step two 3. Confirm fresh data] |

## Troubleshooting

*Common issues and their resolutions.*

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| [Service returns 503] | [Downstream dependency unavailable] | [1. Check dependency status 2. Verify network connectivity 3. Restart if dependency recovered] |
| [High memory usage] | [Memory leak or cache overflow] | [1. Check recent deployments 2. Restart service 3. Escalate if recurring] |
| [Slow response times] | [Database query performance] | [1. Check slow query logs 2. Verify index health 3. Scale read replicas if needed] |
| [Authentication failures] | [Expired credentials or misconfiguration] | [1. Verify credential validity 2. Check config for drift 3. Rotate if expired] |

## Escalation Path

*Who to contact when the on-call cannot resolve an issue.*

| Escalation Level | Contact | When to Escalate |
|-----------------|---------|-----------------|
| Level 1 | [On-call engineer] | [First responder for all alerts] |
| Level 2 | [Senior engineer / Tech lead] | [Issue not resolved within 30 minutes] |
| Level 3 | [Engineering manager / Architect] | [Service-wide outage or data loss risk] |

## Monitoring and Dashboards

- **Primary dashboard**: [URL or name]
- **Logs**: [Where to find logs and how to query them]
- **Metrics**: [Key metrics to watch and their normal ranges]
- **Traces**: [How to find distributed traces for a request]

## Alert Response Procedures

| Alert Name | Severity | Meaning | Response Steps |
|-----------|----------|---------|---------------|
| [HighErrorRate] | [P1 / Critical] | [Error rate exceeds 5% for 5 minutes] | [1. Check error logs 2. Identify failing endpoint 3. Roll back if caused by recent deploy] |
| [HighLatency] | [P2 / Warning] | [p99 latency above threshold] | [1. Check resource utilization 2. Review slow queries 3. Scale if needed] |
| [DiskSpaceLow] | [P2 / Warning] | [Disk usage above 85%] | [1. Identify large files or logs 2. Archive or clean up 3. Increase volume if recurring] |

## Definition of Done

- [ ] All common operations have step-by-step procedures
- [ ] Troubleshooting section covers known failure modes
- [ ] Escalation path is current with real contacts
- [ ] Dashboard and log links are working
- [ ] Alert response procedures match configured alerts
- [ ] Runbook tested by someone other than the author
