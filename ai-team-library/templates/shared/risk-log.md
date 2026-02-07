# Risk Log

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | [YYYY-MM-DD]                   |
| Owner         | [risk log maintainer]          |
| Related links | [issue/PR/ADR URLs]            |
| Status        | Draft / Reviewed / Approved    |

## Purpose

*Track identified risks, their likelihood and impact, mitigation plans, and current status. Review this log regularly -- at minimum during sprint planning or milestone reviews.*

## Risk Register

| Risk ID | Description                    | Category       | Likelihood | Impact | Mitigation                        | Owner        | Status                    | Last Reviewed |
|---------|--------------------------------|----------------|------------|--------|-----------------------------------|--------------|---------------------------|---------------|
| R-001   | [what could go wrong]          | [category]     | H / M / L  | H / M / L | [actions to reduce or handle] | [person]     | Open / Mitigating / Closed| [YYYY-MM-DD]  |
| R-002   | [what could go wrong]          | [category]     | H / M / L  | H / M / L | [actions to reduce or handle] | [person]     | Open / Mitigating / Closed| [YYYY-MM-DD]  |
| R-003   | [what could go wrong]          | [category]     | H / M / L  | H / M / L | [actions to reduce or handle] | [person]     | Open / Mitigating / Closed| [YYYY-MM-DD]  |

## Category Reference

*Use consistent categories to make filtering and reporting easier.*

- **Technical** -- architecture, dependencies, performance, scalability
- **Schedule** -- timeline slippage, resource availability, external delays
- **Scope** -- requirements changes, feature creep, unclear acceptance criteria
- **Operational** -- deployment, infrastructure, monitoring, incident response
- **Security** -- vulnerabilities, data protection, access control
- **Compliance** -- regulatory requirements, audit findings, policy adherence
- **External** -- vendor reliability, third-party service outages, market changes

## Scoring Guide

| Rating | Likelihood                         | Impact                                  |
|--------|------------------------------------|-----------------------------------------|
| H      | Very likely to occur               | Severe: blocks delivery or causes major harm |
| M      | Could reasonably occur             | Moderate: causes delay or degraded quality   |
| L      | Unlikely but possible              | Minor: inconvenience, easily worked around   |

## Review Cadence

- **Review frequency:** [e.g., every sprint, biweekly, at each milestone]
- **Reviewer(s):** [person or role responsible for reviewing the log]
- **Escalation path:** [who to escalate high-likelihood, high-impact risks to]

## Definition of Done

- [ ] All known risks captured with category, scores, and mitigation
- [ ] Each risk has a named owner
- [ ] Log reviewed within the last review cycle
- [ ] Closed risks have documented outcomes
- [ ] High-impact risks escalated to appropriate stakeholders
