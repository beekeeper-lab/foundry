---
id: sales-engineering
category: Business Practices
entry: true
last-reviewed: 2026-07
---

# Sales Engineering Conventions

## Category
Business Practices

Conventions for the technical side of the sales cycle: qualifying and answering
RFPs, running architecture reviews, scoping POCs, delivering demos, competing
with battle cards, and converting technical wins into closed deals. The common
thread is discipline — written scope, measurable criteria, honest gap
disclosure, and artifacts delivered fast.

---

## Defaults

| Concern | Default |
|---------|---------|
| Architecture review timing | Post-discovery, pre-POC; 90-minute working session with whiteboarding |
| Architecture review deliverable | Current-state + proposed-integration diagram + written summary within 48 hours |
| POC duration / scope | 2 weeks (10 business days); 2–3 use cases tied to top pain points |
| POC success criteria | 3–5 measurable, binary (pass/fail) criteria agreed in writing before start |
| POC exit | Written evaluation against criteria within 3 business days of POC end |
| Demo environment | Dedicated per-prospect sandbox, IaC-provisioned, industry-seeded data, one-click reset |
| Demo lifecycle | Spin up T-24h, tear down 48h after unless follow-up scheduled |
| Battle cards | One page (front/back) per top 3 competitors + "status quo"; monthly review |
| RFP go/no-go | Weighted qualification scorecard; ≥30 respond, <20 decline, 20–30 escalate |
| RFP compliance ratings | ● Full / ◐ Partial (explain gap) / ○ Not available (state roadmap) — never inflate |
| Technical win documentation | Structured CRM template within 24 hours of the evaluation milestone |
| CS handoff | Technical context doc prepared before close; joint SE-CS transition within 1 week of signature |

---

## 1. Architecture Reviews

An architecture review is both a sales tool and a technical service — the
customer's environment first, your product second.

- Three phases: **Current State Discovery** (applications, data, integration,
  infrastructure, security, compliance) → **Integration Design** (drawn
  collaboratively) → **Gap Analysis** (requirement vs. current capability vs.
  mitigation).
- Discovery comes first and takes at least half the session; the customer does
  most of the talking. Never turn the review into a product demo.
- Invite all system owners (architect, DBA, security, network) — missing
  stakeholders means requirements surface later.
- Deliver the summary (diagram, integration points, gaps and mitigations,
  prerequisites, next steps, open questions) within 48 hours and get the
  customer's confirmation.
- Flag complexity and gaps honestly; never promise unsupported integrations —
  custom work is scoped and priced separately.

Full detail: `architecture-reviews.md`

---

## 2. POC Scoping and Success Criteria

A POC answers one question: "Does this solution solve our specific problem?"
Everything else is scope creep.

- Before agreeing: run the discovery questions, and confirm a path to purchase
  ("If the POC meets all success criteria, what happens next?"). No answer
  means it's research, not a sales process.
- Require a named technical champion who commits time daily. A POC where only
  the vendor works is a free trial, not a proof of concept.
- Success criteria must be specific, measurable, binary, and locked in writing
  at kickoff — "search returns in < 500ms for 10M records", not "the system
  should be fast". New requirements go to a "phase 2" list, never mid-POC.
- Use a weighted scorecard for competitive bake-offs.
- Schedule the results review meeting at kickoff; deliver the written
  evaluation within 3 business days of POC end. Disclose limitations on day 1,
  not day 9.

Full detail: `poc-scoping.md`

---

## 3. Demo Environments

A demo environment is a curated experience, not a staging server. Treat it
with production rigor — a crashed demo loses more revenue than a crashed
staging server.

- Provision from infrastructure-as-code; never demo from one engineer's laptop
  or on production.
- Seed data that mirrors the prospect's industry vertical; "Acme Corp / John
  Doe" data signals you did not prepare. Maintain a reusable library of
  industry data sets.
- Keep a tested one-click reset script and fallback materials (screenshots,
  recorded video) for every demo.
- Follow the demo runbook: provision and seed at T-24h, smoke-test scenarios
  at T-4h, verify connectivity at T-2h, test screen share at T-10min.
- Limit scenarios to the 3–5 use cases from discovery. Time-limit credentials
  and tear down environments on schedule.

Full detail: `demo-environments.md`

---

## 4. Competitive Battle Cards

A battle card is a tactical playbook for a specific competitive situation, not
a feature comparison.

- Standard card structure: Quick Profile, When You Encounter Them (incumbent /
  bake-off / casual mention / price undercut), Differentiators with talk tracks
  and proof points, Landmines to defuse, trap questions, and demo strategy.
- Every differentiator needs at least one proof point (customer quote, metric,
  benchmark). Specific beats vague: "SOC 2 Type II in 6 months with zero
  findings" is actionable; "we're better at security" is not.
- Be honest about competitor strengths and never disparage them to prospects —
  technical evaluators have done their research.
- Feed cards with win/loss intelligence captured after every competitive deal;
  review monthly and update immediately on competitor launches or pricing
  changes. Stale cards are worse than none.
- Cover the top 3–5 competitors plus "status quo / do nothing" — no more.

Full detail: `battle-cards.md`

---

## 5. RFP/RFI Responses

Not every RFP deserves a response; the ones that do deserve discipline.

- Qualify first with the weighted go/no-go scorecard (relationship 3x,
  technical fit 3x, deal size 2x, competitive position 2x, timeline 1x,
  strategic value 1x). Decline politely below threshold.
- Read the entire RFP and its evaluation criteria before writing; allocate
  effort proportionally to the scoring rubric. Mirror the RFP's structure and
  numbering exactly.
- Complete a technical requirements compliance matrix with honest ratings —
  never mark "Full" if workarounds are required; explain every partial gap and
  mitigation. "On the roadmap" must mean planned and resourced.
- Answer every question, even unfavorably. Skipped questions read as evasion.
- SE drafts technical sections → SME review → legal → AE final review. Start
  within 24 hours of receipt; target 60% of the allowed timeline to leave
  review buffer. Final proofread by someone who did not write it.

Full detail: `rfp-rfi-responses.md`

---

## 6. Technical Wins and Handoff

A technical win — the prospect's evaluators confirming the solution meets
requirements — is a milestone, not the close.

- Document within 24 hours: evaluation results per criterion, what won
  (primary/secondary differentiators with evidence), open items and risks, and
  champion quotes captured verbatim.
- Translate technical results into business outcomes for the economic buyer:
  "passed integration tests" becomes "cuts integration from 6 months to 6
  weeks, saving $200K". Co-create the business case with the AE.
- Prepare the CS/implementation handoff document *before* close: solution
  architecture, configuration decisions, success criteria, contacts, open
  items, competitive context, red flags. Lost context is the top driver of
  early churn.
- Document losses with the same rigor as wins, and feed patterns back to
  product management quarterly.

Full detail: `technical-wins.md`

---

## Do / Don't

**Do:**
- Get POC scope and success criteria in writing before kickoff.
- Deliver architecture review summaries within 48 hours.
- Seed demos with prospect-relevant industry data and keep a one-click reset.
- Back every competitive differentiator with a proof point.
- Rate RFP compliance honestly and explain every gap with a mitigation.
- Document technical wins within 24 hours and hand off context to CS before close.

**Don't:**
- Turn an architecture review into a product demo.
- Let POC scope expand mid-flight or run past the end date without a formal extension.
- Demo on production or from an unreproducible laptop setup.
- Disparage competitors or use confidential/illegally obtained intelligence.
- Promise features or integrations that are not planned and resourced.
- Treat a technical win as a done deal — procurement and budget can still derail it.

---

## Common Pitfalls

1. **Product pitch disguised as discovery.** The architecture review or demo
   becomes a feature walkthrough. Structure the agenda so the customer's
   environment comes first.
2. **POC scope creep.** "Just one more thing" turns the POC into an unpaid
   implementation. Written scope plus formal change requests.
3. **Vague success criteria.** "It should work well" ends in "we need more
   time" — which means you lost. Lock binary, measurable criteria at kickoff.
4. **Stale battle cards and copy-paste RFP answers.** Both are obvious to
   evaluators and destroy credibility. Assign ownership and a review cadence.
5. **No deliverable or lost artifacts.** Great sessions with no artifact are
   forgotten in two weeks. Centralize diagrams, results, and recordings per deal.
6. **Undocumented wins and skipped handoffs.** The SE moves on, context
   evaporates, implementation restarts from scratch, and early churn follows.

---

## Checklist

- [ ] Architecture review covers discovery, integration design, and gap analysis with all system owners present
- [ ] Review summary delivered within 48 hours and confirmed by the customer
- [ ] POC has written scope, 2–3 use cases, binary success criteria, and a named daily champion
- [ ] Path to purchase confirmed before the POC starts; results review scheduled at kickoff
- [ ] Demo environment is IaC-provisioned, industry-seeded, smoke-tested, with reset script and fallback
- [ ] Battle cards exist for top competitors + status quo, each with proof points, reviewed monthly
- [ ] RFP go/no-go scorecard completed; compliance matrix rated honestly; every question answered
- [ ] Technical win documented within 24 hours with champion quotes and business translation
- [ ] CS handoff document prepared before close; win/loss data fed back to product
