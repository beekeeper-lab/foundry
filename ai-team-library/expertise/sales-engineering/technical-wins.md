# Technical Win Documentation

Practices for documenting and leveraging technical wins throughout the sales
cycle. A technical win is the moment when the prospect's technical evaluators
confirm that your solution meets their requirements. It is a critical milestone
— but not the close. Technical wins must be documented, communicated to
stakeholders, and translated into business justification to advance the deal.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Documentation format** | Structured template in CRM (custom fields + notes) | Wiki page per deal with linked artifacts (diagrams, test results) |
| **Timing** | Document within 24 hours of the technical evaluation milestone | Real-time capture during evaluation sessions for complex multi-week POCs |
| **Audience** | SE manager, AE, sales leadership, product management | Extended to CS/onboarding team for high-confidence deals approaching close |
| **Artifacts** | Evaluation summary, test results, architecture diagram, champion quotes | Video recording of final demo, prospect's internal evaluation scorecard |
| **Win criteria** | Prospect's technical champion verbally confirms solution meets requirements | Written sign-off from technical evaluation committee |
| **Handoff** | SE provides technical context doc to implementation/CS team at close | Joint SE-CS transition call within 1 week of contract signature |
| **Retrospective** | Brief win/loss entry in CRM with key takeaways | Full retrospective with product, marketing, and SE team for strategic deals |

---

## Technical Win Documentation Template

### Deal Information

| Field | Value |
|-------|-------|
| **Account** | [Company name] |
| **Deal size** | [ARR / TCV] |
| **Deal stage** | [Current stage in pipeline] |
| **AE** | [Name] |
| **SE** | [Name] |
| **Technical champion** | [Name, title] |
| **Economic buyer** | [Name, title] |
| **Competitors evaluated** | [List] |
| **Technical win date** | [YYYY-MM-DD] |

### Evaluation Summary

| Criterion | Requirement | Result | Notes |
|-----------|------------|--------|-------|
| [Criterion 1] | [What they needed] | Pass / Partial / Fail | [Details] |
| [Criterion 2] | [What they needed] | Pass / Partial / Fail | [Details] |
| [Criterion 3] | [What they needed] | Pass / Partial / Fail | [Details] |

### What Won the Technical Evaluation

| Factor | Detail | Evidence |
|--------|--------|----------|
| **Primary differentiator** | [The capability that tipped the evaluation] | [Demo moment, test result, or champion quote] |
| **Secondary differentiator** | [Supporting strength] | [Evidence] |
| **Trust builder** | [What established credibility — reference call, architecture review, security review] | [Evidence] |

### Open Items and Risks

| Item | Owner | Status | Impact |
|------|-------|--------|--------|
| [Open technical question] | [SE/Prospect] | [Open/Resolved] | [Deal impact if unresolved] |
| [Integration dependency] | [Prospect] | [Open/Resolved] | [Timeline impact] |
| [Security review finding] | [SE] | [Open/Resolved] | [Blocker/Non-blocker] |

### Champion Quotes

Capture direct quotes from the technical champion and evaluation team.
These are gold for case studies, references, and internal storytelling.

> "[Exact quote from champion about what impressed them]"
> — [Name, Title], [Company]

> "[Quote about specific capability or experience]"
> — [Name, Title], [Company]

---

## Technical Win to Business Case

A technical win alone does not close the deal. Translate technical validation
into business justification for the economic buyer.

| Technical Win | Business Translation |
|--------------|---------------------|
| "Passed all integration tests" | "Reduces integration timeline from 6 months to 6 weeks, saving $200K in professional services" |
| "Search performance 3x faster than incumbent" | "Analyst team recovers 2 hours/day per analyst = $180K/year in productivity" |
| "SSO and audit logging met all security requirements" | "Eliminates the compliance risk flagged in last year's audit, avoiding potential $500K penalty" |
| "Users completed tasks 40% faster in usability testing" | "Faster onboarding reduces training cost by $50K and accelerates time-to-value by 3 months" |

---

## Win Handoff to Customer Success

When the deal closes, the SE's technical knowledge must transfer to the
implementation and CS team. Lost context leads to poor onboarding and early
churn.

### Handoff Document

| Section | Content |
|---------|---------|
| **Solution architecture** | Diagram of what was evaluated, integration points, data flows |
| **Configuration decisions** | Choices made during POC (settings, customizations, workarounds) |
| **Success criteria** | What the prospect cared about most — carry these into onboarding KPIs |
| **Technical contacts** | Champion and technical team members with their roles and preferences |
| **Open items** | Unresolved questions, known limitations, future feature requests |
| **Competitive context** | Who we beat and why — helps CS reinforce value during renewals |
| **Red flags** | Any concerns surfaced during evaluation (adoption risk, integration complexity, executive sponsor changes) |

---

## Do / Don't

- **Do** document technical wins within 24 hours. Memory fades, details blur,
  and the artifacts lose fidelity.
- **Do** capture champion quotes verbatim. Their words carry more weight in
  case studies and internal reviews than your summary.
- **Do** translate technical results into business outcomes. The CFO does not
  care about API response times — they care about cost savings and risk
  reduction.
- **Do** include what almost went wrong. Near-misses reveal product gaps and
  process improvements.
- **Do** create a handoff document for CS/implementation before the deal
  closes. Waiting until after signature means the SE has moved to the next
  deal and context is lost.
- **Do** feed technical win data back to product management. Patterns across
  wins and losses inform roadmap priorities.
- **Don't** treat a technical win as a done deal. Procurement, legal,
  budget cycles, and executive changes can still derail the opportunity.
- **Don't** document only wins. Technical losses are equally valuable — they
  reveal where the product or the process needs improvement.
- **Don't** let documentation become bureaucratic. The template should take
  30 minutes to complete, not half a day. If it takes longer, the template
  is too complex.
- **Don't** skip the handoff. The number-one driver of early churn is poor
  onboarding caused by lost context between sales and CS.
- **Don't** hoard technical win intelligence within the SE team. Share it
  with product, marketing, and CS to multiply its value.

---

## Common Pitfalls

1. **Undocumented wins.** The SE moves to the next deal and the technical
   context is lost. When the deal closes months later, implementation starts
   from scratch. Solution: make documentation a required step before moving
   to the next deal.
2. **Technical win ≠ deal close.** The SE celebrates the technical win and
   disengages, but procurement stalls for 3 months. Solution: stay engaged
   through close; define SE involvement post-technical-win.
3. **No business translation.** Technical results sit in a spreadsheet that the
   economic buyer never sees. Solution: co-create a business case document with
   the AE after the technical win.
4. **Lost artifacts.** Demo recordings, test results, and architecture diagrams
   are scattered across email, Slack, and local drives. Solution: centralize
   artifacts in the CRM or a linked wiki page per deal.
5. **One-sided documentation.** Only successful criteria are documented;
   partial passes and workarounds are glossed over. Solution: document honestly —
   partial results and open items are critical for implementation planning.
6. **No feedback loop.** Technical win/loss data is captured but never analyzed
   for patterns. Solution: quarterly review of win/loss trends with product
   and SE leadership.

---

## Checklist

- [ ] Technical win is documented within 24 hours of evaluation milestone
- [ ] All evaluation criteria are scored with results and evidence
- [ ] Primary and secondary differentiators are identified with proof points
- [ ] Champion quotes are captured verbatim
- [ ] Open items and risks are logged with owners and status
- [ ] Technical results are translated into business outcomes for the economic buyer
- [ ] Handoff document is prepared for CS/implementation team
- [ ] Win/loss entry is created in CRM with key takeaways
- [ ] Artifacts (diagrams, test results, recordings) are centralized and accessible
- [ ] Product management is notified of feature gaps or enhancement requests surfaced
