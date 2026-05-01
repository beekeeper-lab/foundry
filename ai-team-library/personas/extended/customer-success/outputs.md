# Customer Success / Solutions Engineer -- Outputs

This document enumerates every artifact the Customer Success / Solutions Engineer
is responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. Customer Onboarding Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Customer Onboarding Plan                           |
| **Cadence**        | One per customer engagement                        |
| **Template**       | `personas/customer-success/templates/onboarding-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A structured plan that guides a customer from initial kickoff
through full adoption of the product. The plan defines milestones, timelines,
success criteria, and ownership for each phase of onboarding. It is tailored to
the customer's technical environment, business goals, and team capacity.

**Quality Bar:**
- Every milestone has a specific completion date, owner, and measurable success
  criterion -- "Customer can authenticate via SSO" not "SSO is set up."
- Technical prerequisites are identified with validation steps, not assumed.
- The plan accounts for common failure modes: integration delays, data migration
  issues, stakeholder availability. Contingency timelines are included.
- Customer-specific configuration and environment details are documented.
- The plan includes an explicit "go-live" definition that both parties agree on.
- A communication cadence (weekly syncs, milestone reviews) is defined.

**Downstream Consumers:** Customer (for alignment and tracking), Team Lead (for
resource planning), Developer (for integration support scheduling), Architect
(for technical prerequisite awareness).

---

## 2. Implementation Guide

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Implementation Guide                               |
| **Cadence**        | One per customer integration pattern               |
| **Template**       | `personas/customer-success/templates/implementation-guide.md` |
| **Format**         | Markdown                                           |

**Description.** A technical guide tailored to the customer's environment that
walks through product integration step by step. The guide covers prerequisites,
configuration, API integration, data migration, testing, and go-live procedures.
It supplements generic product documentation with customer-specific context.

**Quality Bar:**
- Every step has been validated against the customer's actual environment, not
  just internal documentation.
- Prerequisites are listed with specific versions, configurations, and
  verification commands.
- Common integration issues and their resolutions are documented based on
  experience from prior implementations.
- The guide distinguishes between required and optional configuration steps.
- Code examples use the customer's language/framework where applicable.
- A troubleshooting section covers the most common failure modes encountered
  during implementation.

**Downstream Consumers:** Customer technical team (for implementation execution),
Developer (for escalation context when issues arise), Technical Writer (for
product documentation improvement based on customer-specific patterns).

---

## 3. Customer Health Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Customer Health Report                             |
| **Cadence**        | Monthly or per reporting period                    |
| **Template**       | `personas/customer-success/templates/customer-health-report.md` |
| **Format**         | Markdown                                           |

**Description.** A periodic assessment of a customer's adoption, engagement, and
satisfaction with the product. The report tracks quantitative health metrics,
identifies risk signals, documents recent interactions, and recommends actions to
improve or maintain the customer relationship. It serves as the primary input for
stakeholder reviews and expansion planning.

**Quality Bar:**
- Health metrics are quantitative: adoption rate, active user count, feature
  utilization, support ticket volume and resolution time, NPS or CSAT scores.
- Risk signals are specific and evidence-based: "API call volume dropped 40% in
  the last 30 days" not "customer seems less engaged."
- Action items have owners, deadlines, and expected outcomes.
- The report includes trend data (current period vs. prior period) for key
  metrics.
- Expansion opportunities are grounded in usage data and customer conversations,
  not speculation.
- Open issues and escalations are listed with current status and next steps.

**Downstream Consumers:** Team Lead (for prioritization and resource decisions),
Stakeholders (for account strategy and expansion planning), Developer (for
awareness of customer-impacting issues).

---

## 4. Feedback Summary

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Feedback Summary                                   |
| **Cadence**        | Per product cycle or quarterly                     |
| **Template**       | `personas/customer-success/templates/feedback-summary.md` |
| **Format**         | Markdown                                           |

**Description.** A synthesized analysis of customer feedback collected across
multiple accounts and interactions. The summary identifies patterns, prioritizes
themes by frequency and business impact, and translates raw customer input into
actionable product recommendations. It bridges the gap between what customers say
and what the product team needs to hear.

**Required Sections:**
1. **Executive Summary** -- Top 3-5 feedback themes with recommended priority.
2. **Theme Analysis** -- For each theme: customer quotes, frequency across
   accounts, business impact assessment, and recommended product action.
3. **Individual Requests** -- Notable one-off requests that do not form patterns
   but warrant visibility.
4. **Competitive Intelligence** -- Customer mentions of competitor capabilities
   or switching considerations.
5. **Recommended Priorities** -- Ranked list of product actions with rationale.

**Quality Bar:**
- Themes are supported by data from multiple customers, not anecdotes from one.
- Priority recommendations include both customer impact and estimated effort
  context.
- Customer quotes are anonymized unless permission is granted.
- The summary distinguishes between "customers are asking for X" and "customers
  need X to achieve Y" -- the latter is more useful for product decisions.
- Competitive intelligence is factual, not speculative.

**Downstream Consumers:** Team Lead (for roadmap input), Business Analyst (for
requirements elaboration), UX/UI Designer (for usability improvement planning),
Stakeholders (for strategic product direction).

---

## 5. Case Study

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Case Study                                         |
| **Cadence**        | As customer engagements produce measurable outcomes |
| **Template**       | `personas/customer-success/templates/case-study.md` |
| **Format**         | Markdown                                           |

**Description.** A structured narrative documenting a customer's journey from
problem to solution to measurable outcome using the product. The case study
serves both as a sales enablement asset and as an internal reference for
replicating successful implementation patterns.

**Required Sections:**
1. **Customer Profile** -- Industry, size, technical environment, and business
   context.
2. **Challenge** -- The specific problem the customer needed to solve, with
   business impact of the status quo.
3. **Solution** -- How the product was implemented, including integration
   approach, configuration decisions, and timeline.
4. **Results** -- Quantitative outcomes with specific metrics, timeframes, and
   before/after comparisons.
5. **Lessons Learned** -- What worked well, what was challenging, and what the
   team would do differently.
6. **Customer Quote** -- A direct quote from the customer (with approval)
   endorsing the outcome.

**Quality Bar:**
- Results include specific, verifiable metrics: "Reduced API integration time
  from 12 weeks to 3 weeks" not "significantly faster integration."
- The challenge section quantifies the business impact of the problem, not just
  describes it.
- The solution section is detailed enough that another CS engineer could
  replicate the approach.
- Customer approval has been obtained for all quotes and identifying details.
- The case study is honest about challenges encountered, not a pure marketing
  narrative.

**Downstream Consumers:** Stakeholders (for sales enablement and marketing),
Team Lead (for implementation pattern replication), Customer Success peers (for
onboarding playbook improvement).

---

## 6. Escalation Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Escalation Report                                  |
| **Cadence**        | As needed when customer issues require engineering escalation |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A structured report that packages a customer-reported issue for
engineering escalation with full context. The report enables the receiving team
to understand the customer impact, reproduce the issue, and prioritize
appropriately without requiring a back-and-forth information gathering cycle.

**Required Sections:**
1. **Customer Context** -- Account name, tier, contract details relevant to SLA.
2. **Issue Summary** -- Clear description of the problem in technical terms.
3. **Business Impact** -- How the issue affects the customer's operations,
   revenue, or timeline.
4. **Reproduction Steps** -- Step-by-step instructions to reproduce the issue.
5. **Environment Details** -- Customer's technical environment, versions,
   configuration.
6. **Attempted Resolutions** -- What has already been tried and the results.
7. **Recommended Priority** -- Suggested severity with justification.

**Quality Bar:**
- Reproduction steps are verified -- the CS engineer has confirmed the issue can
  be reproduced.
- Business impact is quantified where possible: "Blocking production deployment
  for 200-person team" not "important customer is affected."
- Environment details are specific: versions, configurations, relevant logs.
- Attempted resolutions are documented to prevent duplicate troubleshooting.
- The recommended priority is calibrated to actual impact, not customer volume.

**Downstream Consumers:** Developer (for bug investigation and fix), Tech-QA
(for test case creation), Team Lead (for prioritization decisions).

---

## Output Format Guidelines

- All deliverables are written in Markdown and stored in the project repository
  under the designated customer success documentation folder.
- Customer-identifying information is handled according to data privacy policies.
  Use anonymized identifiers in shared documents unless customer consent is
  obtained.
- Health reports use consistent metric definitions across all customer accounts
  to enable cross-account comparison.
- Feedback summaries aggregate across accounts; individual customer details are
  in separate, access-controlled documents.
- Case studies require explicit customer approval before external publication.
- All deliverables include a date, author, and the customer engagement context
  to prevent misapplication of advice.
