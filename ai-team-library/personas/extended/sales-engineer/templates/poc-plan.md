# POC Plan: [Prospect Name] -- [POC Title]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Sales Engineer| [Name]                         |
| Prospect      | [Prospect company name]        |
| Opportunity   | [Deal ID or opportunity name]  |
| Status        | Planning / Active / Complete   |

*Proof-of-concept plan with defined success criteria, timeline, and decision framework. All parameters must be agreed upon before work begins.*

---

## POC Overview

- **Objective:** [What the POC will prove or evaluate]
- **Scope:** [What is included -- and explicitly what is NOT included]
- **Duration:** [e.g., 2 weeks, starting YYYY-MM-DD]
- **Decision date:** [When the prospect will make a go/no-go decision]

---

## Success Criteria

| # | Criterion | Measurement | Target | Weight |
|---|-----------|-------------|--------|--------|
| 1 | [e.g., API response time under load] | [e.g., P95 latency at 500 RPS] | [e.g., <200ms] | [e.g., Critical] |
| 2 | [e.g., Data import accuracy] | [e.g., Record match rate vs source] | [e.g., >99.5%] | [e.g., Critical] |
| 3 | [e.g., Integration with existing SSO] | [e.g., Successful login via Okta SAML] | [e.g., Pass/Fail] | [e.g., Required] |

---

## Environment Specification

| Component       | Details                                   |
|-----------------|-------------------------------------------|
| Deployment      | [e.g., Dedicated cloud instance]          |
| Region          | [e.g., US-East-1]                         |
| Configuration   | [e.g., Standard tier, 4 vCPU, 16 GB RAM] |
| Data            | [e.g., Customer-provided sample dataset]  |
| Integrations    | [e.g., Okta SSO, Salesforce API]          |
| Access          | [e.g., Customer team gets read/write via SSO] |

### Setup Steps

1. [Provision environment]
2. [Configure integrations]
3. [Load test data]
4. [Validate baseline functionality]
5. [Grant customer access]

---

## Timeline

| Week | Milestone                    | Owner          | Deliverable        |
|------|------------------------------|----------------|--------------------|
| 1    | [e.g., Environment setup]    | [Sales Engineer] | [Working environment] |
| 1    | [e.g., Customer onboarding]  | [Sales Engineer] | [Access credentials, guide] |
| 2    | [e.g., Evaluation period]    | [Customer]     | [Test execution]   |
| 2    | [e.g., Results review]       | [Sales Engineer] | [Results report]   |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [e.g., Customer data format incompatible] | [Medium] | [High] | [Pre-validate sample data in week 0] |
| [e.g., SSO integration delay] | [Low] | [Medium] | [Provide temporary local auth as fallback] |

---

## Decision Framework

| Outcome           | Criteria                                  | Next Step                    |
|-------------------|-------------------------------------------|------------------------------|
| **Proceed**       | All critical criteria met, required criteria pass | [Move to procurement / negotiation] |
| **Conditional**   | Critical criteria met, some required criteria need workaround | [Document workarounds, extend if needed] |
| **No-go**         | Critical criteria not met                 | [Document gaps, revisit on roadmap delivery] |

---

## Results (Post-POC)

| # | Criterion | Result | Target | Status |
|---|-----------|--------|--------|--------|
| 1 | [Criterion] | [Actual measurement] | [Target] | [Pass / Fail / Partial] |

### Gaps Identified

| Gap | Severity | Workaround | Reported To |
|-----|----------|------------|-------------|
| [e.g., Missing bulk export API] | [High] | [Manual CSV export available] | [Product Management] |

### Decision

**Outcome:** [Proceed / Conditional / No-go]

**Customer feedback:** [Summary of customer's assessment]
