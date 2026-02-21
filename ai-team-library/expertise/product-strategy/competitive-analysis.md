# Competitive Analysis

Structured methods for understanding the competitive landscape, identifying
differentiation opportunities, and informing product positioning. Competitive
analysis is an ongoing practice, not a one-time exercise — markets shift, and
yesterday's differentiation becomes tomorrow's table stakes.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Analysis frequency** | Quarterly refresh with monthly signal monitoring | Event-driven updates when a competitor launches, pivots, or raises funding |
| **Competitor set** | 3–5 direct competitors + 2–3 adjacent/emerging threats | Broader landscape (10+) for investor presentations or market entry |
| **Data sources** | Public: websites, pricing pages, changelogs, reviews (G2, Capterra), job postings | Paid: analyst reports (Gartner, Forrester); win/loss interviews with sales |
| **Analysis framework** | Feature comparison matrix + SWOT per competitor | Porter's Five Forces for market-level analysis; Value Curve for positioning |
| **Output format** | Internal wiki page with summary table and positioning map | Slide deck for executive/board presentations |
| **Ownership** | Product manager with input from sales, marketing, and CS | Dedicated competitive intelligence function for enterprise orgs |
| **Distribution** | Shared with product, sales, and marketing teams | Restricted distribution for sensitive pricing/strategy intelligence |

---

## Feature Comparison Matrix

The foundation of competitive analysis. Compare your product against competitors
on the features and capabilities that matter to your target buyers.

| Capability | Your Product | Competitor A | Competitor B | Competitor C |
|------------|-------------|-------------|-------------|-------------|
| Core feature 1 | ● Full | ● Full | ◐ Partial | ○ None |
| Core feature 2 | ◐ Partial | ● Full | ● Full | ◐ Partial |
| Integration X | ● Full | ○ None | ◐ Partial | ● Full |
| Pricing (per seat/mo) | $25 | $35 | $20 | $30 |
| Free tier | Yes (10 users) | No | Yes (3 users) | Yes (5 users) |
| API access | All plans | Enterprise only | Pro+ | All plans |
| Uptime SLA | 99.9% | 99.95% | 99.5% | 99.9% |

**Legend:** ● Full support | ◐ Partial/limited | ○ Not available

**Rules for the matrix:**
- Include only capabilities that influence buying decisions — not every checkbox feature
- Weight capabilities by importance to your target segment
- Update when competitors ship new features or change pricing
- Source claims from public documentation, not assumptions

---

## SWOT Analysis

Assess each competitor (and your own product) across four dimensions.

### SWOT Template

| | Helpful | Harmful |
|---|---------|---------|
| **Internal** | **Strengths:** What they do well. Core competencies, resources, brand equity, technology advantages. | **Weaknesses:** Where they fall short. Product gaps, scaling issues, poor UX, limited integrations. |
| **External** | **Opportunities:** Market trends or shifts they could exploit. Emerging segments, regulatory changes, technology shifts. | **Threats:** External risks to their position. New entrants, substitutes, changing buyer behavior, economic conditions. |

### SWOT Example (Competitor A)

| | Helpful | Harmful |
|---|---------|---------|
| **Internal** | Strong enterprise brand recognition; deep integration with Salesforce ecosystem; $50M ARR provides R&D runway | Slow release cadence (quarterly); no self-serve onboarding; poor mobile experience |
| **External** | Growing demand for AI-powered analytics in their segment; expansion into APAC market | New entrants (us) offering modern UX at lower price; regulatory compliance requirements increasing build cost |

---

## Positioning Map

A 2D visualization that plots competitors along the two dimensions most important
to your target market. Reveals white space and crowded segments.

```
                    High Ease of Use
                         |
                         |
         ┌───────────────┼───────────────┐
         │   ○ You       │               │
         │               │  ○ Comp C     │
Low ─────┼───────────────┼───────────────┼───── High
Feature  │               │               │     Feature
Depth    │  ○ Comp B     │               │     Depth
         │               │  ○ Comp A     │
         └───────────────┼───────────────┘
                         |
                    Low Ease of Use
```

**Choosing axes:**
- Pick the two attributes your target buyers care most about (from user research)
- Common axis pairs: ease of use vs. feature depth, price vs. quality, speed vs.
  customization, SMB focus vs. enterprise focus
- Plot honestly — if a competitor is better on an axis, acknowledge it

---

## Competitive Intelligence Signals

Track these ongoing signals to detect competitor moves early:

| Signal | What to watch | Source |
|--------|--------------|--------|
| **Product changes** | New features, deprecations, pricing changes | Changelogs, release notes, product blogs |
| **Hiring patterns** | New roles signal strategic direction (e.g., hiring ML engineers → AI features) | LinkedIn, job boards |
| **Funding & M&A** | New capital enables expansion; acquisitions change competitive dynamics | Crunchbase, press releases |
| **Customer sentiment** | Complaints and praise reveal strengths and weaknesses | G2, Capterra, Reddit, support forums |
| **Content & messaging** | Positioning shifts, new target segments, competitive comparisons | Website changes, blog posts, ad copy |
| **Win/loss data** | Why deals were won or lost against specific competitors | Sales team interviews, CRM notes |

---

## Do / Don't

- **Do** focus on the competitor's strategy, not just their feature list. Features
  are symptoms; strategy explains direction.
- **Do** include adjacent competitors and potential disruptors, not only direct
  competitors. The biggest threat may come from a different category.
- **Do** use win/loss interviews as a primary data source. Sales teams hear why
  customers choose competitors in the customer's own words.
- **Do** update the analysis regularly. A 6-month-old competitive analysis is
  a historical document, not a strategic tool.
- **Do** differentiate between table-stakes features and true differentiators.
  Matching table stakes is necessary; winning requires differentiation.
- **Do** share competitive intelligence with sales and marketing. Product
  knowledge locked in a PM's head does not help the team sell.
- **Don't** obsess over competitors at the expense of customer needs. The best
  product strategy is customer-driven, not competitor-driven.
- **Don't** assume competitor claims are accurate. "Enterprise-grade security" on
  a marketing page does not mean SOC 2 compliance. Verify.
- **Don't** copy competitor features without understanding *why* they built them.
  Their context, users, and strategy differ from yours.
- **Don't** treat the analysis as confidential by default. Overclasfication
  prevents the team from using the insights. Restrict only genuinely sensitive data.
- **Don't** ignore indirect competitors (spreadsheets, manual processes, in-house
  tools). Your real competition may be "do nothing."

---

## Common Pitfalls

1. **Feature-counting fallacy.** Assuming more features = better product. Customers
   care about the right features done well, not a long checklist. Solution: weight
   features by buyer importance.
2. **Confirmation bias.** Seeking evidence that confirms your product is superior
   while dismissing competitor strengths. Solution: assign a "red team" to argue
   the competitor's case.
3. **Analysis paralysis.** Spending months on a comprehensive competitive report
   that is outdated by the time it is published. Solution: start with a lightweight
   matrix and iterate. A living doc beats a polished artifact.
4. **Ignoring non-consumption.** Fixating on named competitors while the majority
   of potential customers use spreadsheets or manual processes. Solution: size the
   "non-consumption" segment and treat it as the primary competitive alternative.
5. **One-time snapshot.** The competitive analysis is done once for a board deck and
   never updated. Solution: assign ownership and set a quarterly refresh cadence.
6. **Reactive positioning.** Changing your roadmap every time a competitor ships
   something new. Solution: maintain a strategic thesis and evaluate competitor
   moves against it, not the other way around.

---

## Checklist

- [ ] Direct competitors (3–5) and adjacent threats (2–3) are identified
- [ ] Feature comparison matrix is built with buyer-relevant capabilities
- [ ] SWOT analysis is completed for each key competitor
- [ ] Positioning map is created with the two most important buyer dimensions
- [ ] Win/loss data is collected from sales team
- [ ] Competitive intelligence signals are monitored (changelogs, hiring, funding)
- [ ] Analysis is shared with product, sales, and marketing teams
- [ ] Refresh cadence is established (quarterly recommended)
- [ ] Non-consumption (spreadsheets, manual processes) is sized as a competitor
- [ ] Differentiation strategy is documented based on analysis findings
