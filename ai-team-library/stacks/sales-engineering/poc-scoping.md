# POC Scoping and Success Criteria

Frameworks for defining, executing, and evaluating proof-of-concept engagements
that advance deals without becoming unpaid consulting projects. A POC should
answer one question: "Does this solution solve our specific problem?" Everything
in the POC — scope, timeline, success criteria — should serve that answer.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Duration** | 2 weeks (10 business days) | 1 week for simple integrations; 4 weeks for enterprise with complex data migration |
| **Scope** | 2–3 use cases directly tied to the prospect's top pain points | Single use case for focused validation; 5+ use cases only with dedicated PS resources |
| **Success criteria** | 3–5 measurable, binary (pass/fail) criteria agreed before start | Weighted scorecard for competitive bake-offs with multiple vendors |
| **Environment** | Prospect's sandbox or staging environment with real (anonymized) data | Vendor-hosted demo environment for faster setup when prospect infra is slow |
| **Participants** | SE lead + prospect technical champion + 1–2 prospect end users | Joint team with dedicated PM and engineering support for strategic deals |
| **Exit criteria** | Written evaluation against success criteria within 3 business days of POC end | Formal presentation to prospect's evaluation committee |
| **Agreement** | Lightweight POC agreement defining scope, timeline, IP, and data handling | Full MSA/SOW for POCs requiring significant vendor engineering investment |

---

## POC Scoping Framework

### Discovery Questions (Pre-POC)

Ask these before agreeing to a POC:

| Question | Why It Matters |
|----------|---------------|
| What specific problem are you trying to solve? | Focuses the POC on value, not features |
| What does success look like for this evaluation? | Surfaces the real decision criteria |
| Who are the decision-makers and what are their priorities? | Identifies stakeholders you must convince |
| What is your timeline for a purchase decision? | Gauges deal urgency and POC priority |
| Have you evaluated other solutions? What was the result? | Reveals competitive landscape and objections |
| What data and systems will the POC integrate with? | Scopes technical effort and identifies blockers |
| Who is the technical champion who will participate daily? | Ensures prospect commitment, not just vendor effort |

### Scope Definition Template

```yaml
poc_scope:
  prospect: "[Company Name]"
  sponsor: "[Name, Title]"
  technical_champion: "[Name, Title]"
  start_date: "YYYY-MM-DD"
  end_date: "YYYY-MM-DD"

  use_cases:
    - id: UC-1
      title: "[Use case name]"
      description: "[What the prospect wants to validate]"
      data_requirements: "[What data is needed]"
      integration_points: "[Systems involved]"

    - id: UC-2
      title: "[Use case name]"
      description: "[What the prospect wants to validate]"
      data_requirements: "[What data is needed]"
      integration_points: "[Systems involved]"

  success_criteria:
    - id: SC-1
      criterion: "[Measurable, binary statement]"
      measurement: "[How it will be measured]"
      target: "[Pass/fail threshold]"

    - id: SC-2
      criterion: "[Measurable, binary statement]"
      measurement: "[How it will be measured]"
      target: "[Pass/fail threshold]"

  out_of_scope:
    - "[Explicitly excluded items]"
    - "[Features not being evaluated]"

  assumptions:
    - "[Prospect provides X by date Y]"
    - "[Network access is available]"

  risks:
    - risk: "[Potential blocker]"
      mitigation: "[Plan to address]"
```

---

## Success Criteria Design

Good success criteria are specific, measurable, and agreed in writing before
the POC begins. Vague criteria lead to "the POC went well but we need more
time" — which means you lost.

| Bad Criterion | Good Criterion |
|--------------|----------------|
| "The system should be fast" | "Search queries return results in < 500ms for datasets up to 10M records" |
| "Integration should work" | "Bi-directional sync with Salesforce completes within 60 seconds of a record update" |
| "Users should like the UI" | "3 out of 5 test users complete the core workflow without assistance in under 5 minutes" |
| "It should handle our data" | "System ingests the provided 50GB dataset without errors and all records are queryable" |
| "Security must be adequate" | "SSO via customer's Azure AD is configured and functional; audit logs capture all admin actions" |

### Weighting for Competitive Bake-Offs

When the POC is a head-to-head evaluation against competitors, use a weighted
scorecard:

| Criterion | Weight | Vendor A | Vendor B | Notes |
|-----------|--------|----------|----------|-------|
| Data ingestion performance | 30% | | | |
| Integration completeness | 25% | | | |
| User experience (task completion) | 20% | | | |
| Security and compliance | 15% | | | |
| Implementation effort | 10% | | | |
| **Weighted Total** | **100%** | | | |

---

## POC Execution Timeline

| Day | Activity | Owner |
|-----|----------|-------|
| 1 | Kickoff call — confirm scope, success criteria, access | SE + Champion |
| 1–2 | Environment setup, data ingestion, basic configuration | SE |
| 3–5 | Use case 1 implementation and validation | SE + Champion |
| 6–8 | Use case 2 implementation and validation | SE + Champion |
| 8–9 | End-user testing sessions (2–3 users) | Champion + Users |
| 9 | Issue resolution and final adjustments | SE |
| 10 | Results review — measure against success criteria | SE + Champion |
| 10+3 | Written evaluation delivered to decision-makers | SE + AE |

---

## Do / Don't

- **Do** get success criteria in writing before the POC starts. Verbal
  agreements shift; documents do not.
- **Do** require a technical champion from the prospect who commits time daily.
  A POC where only the vendor works is a free trial, not a proof of concept.
- **Do** limit scope ruthlessly. Two use cases done well beat five done poorly.
  The prospect is evaluating quality, not quantity.
- **Do** document blockers immediately and escalate. A POC stalled on
  missing API credentials or network access is wasted time for everyone.
- **Do** schedule the results review meeting at kickoff. This creates urgency
  and prevents the POC from drifting.
- **Do** capture lessons learned after every POC, win or lose. Patterns across
  POCs reveal product gaps and process improvements.
- **Don't** agree to a POC without a clear path to purchase. Ask: "If the POC
  meets all success criteria, what happens next?" If there is no answer, the
  POC is research, not a sales process.
- **Don't** expand scope during the POC. New requirements go into a "phase 2"
  list. Scope creep is the leading cause of POC overruns.
- **Don't** let the POC run past the agreed end date without a formal extension
  decision. Open-ended POCs signal low prospect commitment.
- **Don't** confuse a POC with an implementation. POCs prove value; they do not
  deliver production-ready systems.
- **Don't** hide limitations. If your product cannot do something, say so early.
  A surprise failure on day 9 is far worse than an honest disclosure on day 1.

---

## Common Pitfalls

1. **Scope creep.** The prospect keeps adding "just one more thing" until the
   POC is an unpaid implementation. Solution: document scope in writing and
   require formal change requests for additions.
2. **No champion.** The prospect designates a contact who is too busy to
   participate. The SE works alone, and the prospect has no ownership of the
   results. Solution: make champion participation a prerequisite.
3. **Vague success criteria.** "It should work well" is not measurable. The POC
   ends with ambiguity instead of a decision. Solution: use the bad-to-good
   criteria translation table above.
4. **Moving goalposts.** Success criteria change mid-POC to include new
   requirements. Solution: lock criteria at kickoff; new items go to a backlog.
5. **No executive access.** The technical team loves the product, but the
   decision-maker never saw the results. Solution: schedule a stakeholder
   readout at kickoff and protect that calendar slot.
6. **POC-to-production gap.** The POC uses shortcuts (hard-coded config, manual
   steps) that do not translate to production. Solution: document what is
   POC-only and what carries forward.

---

## Checklist

- [ ] Discovery questions are answered and documented
- [ ] POC scope is defined with 2–3 use cases and explicitly listed exclusions
- [ ] Success criteria are measurable, binary, and agreed in writing
- [ ] Technical champion is named and has committed daily participation
- [ ] POC agreement is signed covering scope, timeline, data handling, and IP
- [ ] Environment access and data are confirmed available before kickoff
- [ ] Results review meeting is scheduled at kickoff
- [ ] Path to purchase is confirmed ("If POC succeeds, then what?")
- [ ] Daily or every-other-day check-ins are scheduled with the champion
- [ ] Lessons learned are captured within 1 week of POC completion
