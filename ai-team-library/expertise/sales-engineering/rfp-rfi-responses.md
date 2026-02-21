# RFP/RFI Response Templates

Structured approaches for responding to Requests for Proposal (RFP) and
Requests for Information (RFI) efficiently and persuasively. RFP responses are
high-stakes documents — they are often the first substantive impression a
procurement team has of your technical capability. Speed, accuracy, and
relevance determine whether you advance to the next stage.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Response ownership** | Sales Engineer leads technical sections; AE owns executive summary and pricing | Dedicated RFP team for orgs receiving 10+ RFPs/month |
| **Content library** | Centralized knowledge base (Confluence, Notion, or Git repo) with approved answers | AI-assisted retrieval from past responses (LLM-powered search) |
| **Review workflow** | SE drafts → SME review → legal review → AE final review → submit | Parallel reviews with assigned sections and merge deadline |
| **Timeline management** | Respond within 60% of the allowed timeline to leave buffer for review | Fast-track process (48h) for strategic deals with executive sponsorship |
| **Go/no-go decision** | Score against qualification criteria before committing resources | AE discretion with SE input on technical feasibility |
| **Format** | Mirror the RFP's structure exactly; use their numbering and section headers | Supplementary appendix for topics not covered by their template |
| **Version control** | Git repository with branch-per-response and PR-based review | Google Docs with suggestion mode for collaborative editing |

---

## Go/No-Go Qualification

Not every RFP deserves a response. Evaluate before committing resources.

| Criterion | Score (1–5) | Weight | Notes |
|-----------|------------|--------|-------|
| **Existing relationship** | | 3x | Do we have a champion inside? |
| **Technical fit** | | 3x | Can we meet ≥80% of requirements natively? |
| **Deal size** | | 2x | Is the contract value worth the response effort? |
| **Competitive position** | | 2x | Are we the incumbent or a credible challenger? |
| **Timeline feasibility** | | 1x | Can we produce a quality response in time? |
| **Strategic value** | | 1x | Does this open a new vertical, logo, or reference? |

**Threshold:** Total weighted score ≥ 30 → respond. Below 20 → decline politely.
Between 20–30 → escalate to sales leadership for decision.

### Decline Template

> Thank you for including [Company] in your evaluation. After careful review, we
> have determined that our current capabilities do not align closely enough with
> your stated requirements to provide a competitive response. We would welcome
> the opportunity to engage on future initiatives where our [specific strength]
> can deliver greater value. Please do not hesitate to reach out directly.

---

## Response Structure

A well-organized RFP response follows the prospect's structure while
emphasizing your strengths.

| Section | Owner | Content |
|---------|-------|---------|
| **Cover letter** | AE | Personalized summary of understanding, key differentiators, and commitment |
| **Executive summary** | AE + SE | Business value proposition mapped to stated objectives |
| **Company overview** | Marketing | History, financials, customer base, relevant certifications |
| **Technical response** | SE | Point-by-point answers to technical requirements |
| **Architecture & integration** | SE | How your solution fits their environment, integration approach |
| **Security & compliance** | SE + Security | Certifications, data handling, incident response, audit support |
| **Implementation plan** | SE + PS | Timeline, milestones, resource requirements, change management |
| **Support & SLA** | SE + Support | Tiers, response times, escalation paths, account management |
| **Pricing** | AE + Finance | Licensing model, payment terms, volume discounts |
| **References** | AE | 2–3 relevant customer references with contact information |
| **Appendices** | SE | Detailed specs, compliance matrices, integration diagrams |

---

## Technical Requirements Matrix

Use a compliance matrix to show point-by-point coverage.

| Req ID | Requirement | Compliance | Details |
|--------|------------|------------|---------|
| TR-001 | SSO via SAML 2.0 | ● Full | Native SAML 2.0 support; tested with Okta, Azure AD, OneLogin |
| TR-002 | Role-based access control | ● Full | Granular RBAC with custom roles, attribute-based policies |
| TR-003 | Real-time data sync | ◐ Partial | Near-real-time (sub-second) via webhooks; true real-time on roadmap Q3 |
| TR-004 | On-premises deployment | ○ Roadmap | Cloud-native today; on-prem option planned for Q4 per customer demand |
| TR-005 | HIPAA compliance | ● Full | BAA available; SOC 2 Type II certified; annual penetration testing |

**Legend:** ● Full compliance | ◐ Partial (explain gap and mitigation) | ○ Not available (state roadmap or workaround)

**Rules:**
- Never mark something as "Full" if it requires workarounds or customization
- For partial compliance, always explain the gap and your plan to address it
- For items not available, be honest — prospects respect candor over vaporware
- Reference specific documentation or certifications, not marketing claims

---

## Do / Don't

- **Do** read the entire RFP before starting. Understand the evaluation criteria
  and weight your effort accordingly. If security is 40% of the score, that
  section gets 40% of your attention.
- **Do** answer every question, even if the answer is unfavorable. Skipping
  questions signals either incompetence or intentional evasion.
- **Do** maintain a living content library of approved answers. A good library
  makes the difference between a 2-week response and a 2-day response.
- **Do** customize every response. Reusing boilerplate verbatim is obvious to
  evaluators and signals low effort.
- **Do** include architecture diagrams and integration maps. Visual
  communication is more persuasive and easier to evaluate than paragraphs of
  text.
- **Do** quantify wherever possible. "99.9% uptime SLA" beats "highly
  reliable." "$2M savings over 3 years" beats "cost-effective."
- **Don't** promise features that do not exist. "On the roadmap" must mean it is
  actually planned and resourced, not aspirational.
- **Don't** badmouth competitors in the response. Focus on your strengths, not
  their weaknesses.
- **Don't** bury bad news. If you cannot meet a requirement, state it clearly
  with your mitigation plan. Evaluators will find the gap anyway.
- **Don't** submit without a final proofread by someone who did not write it.
  Typos, inconsistent formatting, and wrong prospect names are disqualifying.
- **Don't** miss the deadline. A perfect response submitted one hour late is
  worse than a good response submitted on time.

---

## Common Pitfalls

1. **Copy-paste blindness.** Reusing answers from a previous RFP without
   updating the prospect name, industry context, or specific requirements.
   Solution: search-and-replace is not customization — rewrite the framing
   for each prospect.
2. **Technical overload.** Writing deep technical detail that the procurement
   team cannot evaluate. Solution: match the depth to the audience — executive
   summary for leadership, technical detail in appendices.
3. **Ignoring evaluation criteria.** Spending equal effort on all sections when
   the RFP clearly weights some higher. Solution: read the scoring rubric and
   allocate effort proportionally.
4. **Solo authoring.** One SE writes the entire response without SME input,
   leading to shallow answers in specialized areas. Solution: assign sections to
   domain experts with a clear merge deadline.
5. **No go/no-go discipline.** Responding to every RFP regardless of win
   probability, burning SE bandwidth. Solution: implement a qualification
   scorecard and enforce a threshold.
6. **Last-minute scramble.** Starting the response 3 days before the deadline.
   Solution: begin within 24 hours of receipt, even if only to outline sections
   and assign owners.

---

## Checklist

- [ ] Go/no-go qualification is completed and documented
- [ ] Full RFP is read and evaluation criteria are understood
- [ ] Response outline mirrors the RFP structure with section owners assigned
- [ ] Technical requirements matrix is completed with honest compliance ratings
- [ ] Executive summary is customized to the prospect's stated objectives
- [ ] Architecture and integration diagrams are included
- [ ] Security and compliance sections reference specific certifications
- [ ] All questions are answered — no blanks or skipped sections
- [ ] Content is reviewed by SMEs for technical accuracy
- [ ] Final proofread by someone who did not write the response
- [ ] Response is submitted before the deadline with confirmation receipt
