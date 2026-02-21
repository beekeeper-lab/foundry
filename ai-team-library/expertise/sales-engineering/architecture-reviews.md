# Customer Architecture Reviews

Structured methods for conducting architecture reviews with prospects and
customers. An architecture review is both a sales tool and a technical
service — it demonstrates your team's expertise while mapping how your solution
integrates into the customer's environment. Done well, it builds trust,
surfaces integration requirements early, and positions you as a partner rather
than a vendor.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Timing** | Post-discovery, pre-POC — before committing to an evaluation | Post-POC, pre-contract for enterprise deals with complex integration requirements |
| **Duration** | 90-minute working session with whiteboarding | Half-day workshop for enterprise with multiple integration points; 30-minute overview for SMB |
| **Participants** | SE + prospect's lead architect + relevant system owners | SE + solutions architect + prospect's architecture review board for large enterprises |
| **Deliverable** | Architecture diagram (current state + proposed integration) + written summary | Full architecture decision record (ADR) for enterprise; informal sketch for SMB |
| **Tooling** | Diagramming tool (Miro, Lucidchart, draw.io) with shared access | Whiteboard photo + cleanup for in-person meetings |
| **Follow-up** | Deliver finalized diagram and summary within 48 hours | Detailed integration specification document for complex deployments |
| **Depth** | Integration-focused — how your solution connects to their ecosystem | Full platform review including infrastructure, security, data flows, and DR |

---

## Architecture Review Framework

### Phase 1: Current State Discovery

Map the prospect's existing environment before proposing how your solution fits.

| Domain | Questions | Capture |
|--------|----------|---------|
| **Applications** | What core systems run the business? Which are custom-built vs. COTS? | Application inventory with owners and criticality |
| **Data** | Where does the relevant data live? What format, volume, and freshness? | Data sources, schemas, ETL/ELT pipelines |
| **Integration** | How do systems communicate? APIs, message queues, batch files, ETL? | Integration patterns, middleware, API gateways |
| **Infrastructure** | Cloud, on-prem, hybrid? What orchestration and deployment tools? | Infrastructure topology, cloud providers, deployment pipelines |
| **Security** | What are the authentication, authorization, and network security models? | SSO provider, network segmentation, data classification |
| **Compliance** | What regulatory requirements apply? SOC 2, HIPAA, GDPR, PCI-DSS? | Compliance framework, audit schedule, data residency requirements |

### Phase 2: Integration Design

Design how your solution integrates with the prospect's environment.

```
┌─────────────────────────────────────────────────────┐
│  Customer Environment                               │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Identity │  │ Core App │  │ Data Warehouse   │  │
│  │ Provider │  │ (ERP/CRM)│  │ (Snowflake/BQ)   │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │              │                 │             │
│       │    SSO/SAML  │   REST API      │  ETL/CDC   │
│       │              │                 │             │
│  ┌────▼──────────────▼─────────────────▼─────────┐  │
│  │          Your Solution                        │  │
│  │  ┌────────┐  ┌──────────┐  ┌──────────────┐   │  │
│  │  │ Auth   │  │ Core     │  │ Data Import  │   │  │
│  │  │ Module │  │ Platform │  │ Pipeline     │   │  │
│  │  └────────┘  └──────────┘  └──────────────┘   │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Phase 3: Gap Analysis

Identify gaps between the prospect's requirements and your solution's current
capabilities.

| Integration Point | Requirement | Current Capability | Gap | Mitigation |
|------------------|------------|-------------------|-----|------------|
| SSO | SAML 2.0 + SCIM provisioning | SAML 2.0 supported; SCIM in beta | SCIM maturity | Beta access + dedicated support |
| Data import | Real-time CDC from PostgreSQL | Batch import (hourly) | Real-time gap | Webhook-based near-real-time; CDC on roadmap |
| API | GraphQL preferred | REST only | API style | REST provides equivalent functionality; GraphQL on roadmap |
| Network | VPN or private link required | Public endpoints with TLS | Network isolation | AWS PrivateLink available; VPN config supported |

---

## Architecture Review Deliverable

### Template

```markdown
# Architecture Review Summary

**Customer:** [Name]
**Date:** [YYYY-MM-DD]
**Participants:** [Names and roles]
**SE:** [Name]

## Current State
[Summary of existing environment — key systems, data flows, integration patterns]

## Proposed Architecture
[How your solution integrates — with diagram]

## Integration Points
| Point | Method | Direction | Data | Frequency |
|-------|--------|-----------|------|-----------|
| [System A] | REST API | Bi-directional | [Data type] | Real-time |
| [System B] | SFTP | Inbound | [Data type] | Daily batch |

## Gaps and Mitigations
[Summary of gaps identified and proposed mitigations]

## Prerequisites
[What the customer needs to provide or configure before implementation]

## Recommended Next Steps
1. [Next step with owner and timeline]
2. [Next step with owner and timeline]

## Open Questions
- [Unresolved item with owner]
```

---

## Do / Don't

- **Do** prepare by researching the prospect's tech stack before the meeting.
  LinkedIn engineering blog posts, job listings, and conference talks reveal
  tooling choices. Walking in cold wastes everyone's time.
- **Do** let the customer do most of the talking in phase 1. Your job is to
  understand their environment, not to pitch your product.
- **Do** draw diagrams collaboratively. Hand the marker (or the Miro cursor)
  to the customer's architect and build the picture together.
- **Do** identify integration dependencies early. A deployment that requires
  the customer's DBA, network team, and security team to coordinate can add
  months to the timeline.
- **Do** deliver the architecture summary within 48 hours. The prospect's
  memory is freshest right after the session.
- **Do** flag risks honestly. If an integration will be complex, say so. Hiding
  complexity creates surprises during implementation that erode trust.
- **Don't** turn the architecture review into a product demo. The session is
  about the customer's environment and how your solution fits, not a feature
  walkthrough.
- **Don't** assume you know the customer's environment based on their industry.
  Every environment is unique, and assumptions lead to incorrect integration
  designs.
- **Don't** gloss over security and compliance. If the customer is regulated,
  these requirements are non-negotiable and must be addressed explicitly.
- **Don't** promise integrations your product does not support. Custom
  development should be scoped and priced separately, not hand-waved as "we
  can do that."
- **Don't** skip the gap analysis. Every solution has gaps — documenting them
  proactively builds credibility and prevents post-sale surprises.

---

## Common Pitfalls

1. **Product pitch disguised as architecture review.** The SE spends 80% of the
   session presenting features and 20% on the customer's environment. Solution:
   structure the agenda so phase 1 (discovery) comes first and takes at least
   half the session.
2. **Missing stakeholders.** The architecture review happens with only the
   prospect's champion, and critical requirements from the DBA, security team,
   or network team surface later. Solution: ask the champion to identify
   all system owners who should attend.
3. **No deliverable.** The session generates great discussion but no artifact.
   Two weeks later, nobody remembers the details. Solution: assign a note-taker,
   deliver the summary within 48 hours, and get the customer's confirmation.
4. **Overcommitting on integrations.** The SE agrees to integration approaches
   that require custom engineering without consulting the product or PS team.
   Solution: document integration requests and validate feasibility before
   committing.
5. **Ignoring non-functional requirements.** The review covers features and
   integrations but skips performance, scalability, disaster recovery, and
   data residency. Solution: include non-functional requirements as a standard
   section in every review.
6. **One-time exercise.** The architecture review is done once during sales
   and never revisited. The customer's environment evolves, and the original
   design drifts. Solution: schedule a post-implementation architecture review
   at 90 days.

---

## Checklist

- [ ] Pre-meeting research is completed (tech stack, industry, regulatory requirements)
- [ ] Agenda is shared with the customer and includes discovery, design, and next steps
- [ ] All relevant stakeholders (architect, DBA, security, network) are invited
- [ ] Current state environment is mapped with applications, data, and integrations
- [ ] Proposed integration architecture is designed collaboratively
- [ ] Gap analysis identifies capability gaps with mitigations and timelines
- [ ] Security and compliance requirements are explicitly addressed
- [ ] Non-functional requirements (performance, DR, data residency) are covered
- [ ] Architecture summary deliverable is sent within 48 hours
- [ ] Customer confirms the summary accurately represents the discussion
- [ ] Open questions have assigned owners and follow-up dates
- [ ] Integration prerequisites are documented for implementation planning
