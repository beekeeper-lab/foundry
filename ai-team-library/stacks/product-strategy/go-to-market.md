# Go-to-Market Planning

A structured approach to launching products, features, and market expansions.
Go-to-market (GTM) planning coordinates product, marketing, sales, and customer
success around a shared launch strategy. A great product with a poor GTM plan
underperforms a good product with a great one.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **GTM motion** | Product-led growth (PLG) with self-serve onboarding | Sales-led for enterprise; community-led for developer tools; hybrid for mid-market |
| **Launch tiers** | 3-tier system (T1 major, T2 minor, T3 incremental) | 2-tier (big/small) for small teams; 4-tier for large orgs with platform launches |
| **Launch lead time** | T1: 6–8 weeks; T2: 2–4 weeks; T3: ship-and-announce | Compress timelines for competitive responses; extend for regulated markets |
| **Pricing model** | Per-seat with feature-gated tiers (Free, Pro, Enterprise) | Usage-based for API/infrastructure products; flat-rate for simplicity |
| **Channel strategy** | Website + content marketing + product-driven virality | Outbound sales for enterprise; partnerships/channel for niche verticals |
| **Success metrics** | Activation rate, time-to-value, expansion revenue | MQLs/SQLs for sales-led; community growth for developer products |
| **Launch retrospective** | 30 days post-launch review with all stakeholders | 14-day retro for fast-iteration teams; 60-day for enterprise launches |

---

## Launch Tiers

| Tier | Description | Scope | Typical Activities |
|------|-------------|-------|-------------------|
| **T1 — Major** | New product, new market entry, or transformative feature | Full cross-functional GTM | Press release, launch event, sales enablement, customer migration, paid campaigns, analyst briefing |
| **T2 — Minor** | Significant feature, new integration, or pricing change | Product + marketing + sales coordination | Blog post, email campaign, in-app announcement, sales one-pager, help docs update |
| **T3 — Incremental** | Bug fix, UX improvement, minor feature addition | Product + docs | Changelog entry, in-app tooltip, help docs update |

**Tier assignment criteria:**
- Revenue impact potential (high → T1)
- Customer behavior change required (significant → T1/T2)
- Competitive response needed (yes → T1)
- Number of teams involved (3+ → T1, 2 → T2, 1 → T3)

---

## GTM Planning Process

### Phase 1: Strategy (8–6 weeks before launch)

1. **Define the target segment.** Who is this for? Be specific about persona,
   company size, industry, and use case.
2. **Articulate the value proposition.** What problem does this solve? What is the
   measurable benefit? How is it different from alternatives?
3. **Set launch goals.** Define 3–5 measurable success criteria with targets
   (e.g., 500 signups in week 1, 20% activation in 30 days).
4. **Choose the GTM motion.** Self-serve? Sales-assisted? Partner-driven?
5. **Determine pricing and packaging.** Which tier includes this feature? Is there
   a pricing change?

### Phase 2: Preparation (6–2 weeks before launch)

1. **Create sales enablement materials.** One-pager, FAQ, competitive positioning,
   demo script, objection handling guide.
2. **Build marketing assets.** Landing page, blog post, email sequences, social
   content, ad creative.
3. **Prepare customer communications.** Existing customer email, in-app announcements,
   migration guides if needed.
4. **Update documentation.** Help articles, API docs, getting-started guides.
5. **Train internal teams.** Sales, CS, and support should see a demo and have
   access to the FAQ before launch.
6. **Set up tracking.** Analytics events, conversion funnels, attribution tracking.

### Phase 3: Launch (launch day + first 2 weeks)

1. **Coordinate the launch sequence.** Activate channels in order: product release →
   in-app announcements → email → blog/social → press/outbound.
2. **Monitor metrics in real time.** Signups, activation, errors, support tickets.
3. **Activate the sales team.** Share launch messaging, talking points, and early
   customer stories.
4. **Respond to feedback.** Monitor support channels, social mentions, and review
   sites. Address issues quickly.

### Phase 4: Post-Launch (2–8 weeks after)

1. **Measure against launch goals.** Did we hit the targets set in Phase 1?
2. **Conduct a launch retrospective.** What worked? What didn't? What would we
   change next time?
3. **Iterate on positioning.** Refine messaging based on actual customer language
   and adoption patterns.
4. **Feed insights back to product.** Usage data and feedback inform the next
   iteration.

---

## Pricing Framework

| Model | Best For | Pros | Cons |
|-------|----------|------|------|
| **Per-seat** | Collaboration tools, team-based products | Predictable revenue; scales with org size | Discourages adoption; users share seats |
| **Usage-based** | APIs, infrastructure, data products | Aligns cost with value; low entry barrier | Revenue volatility; hard to forecast |
| **Flat-rate** | Simple products, early-stage startups | Easy to understand; frictionless purchase | Leaves money on table with power users |
| **Feature-gated tiers** | Products with distinct user segments | Clear upgrade path; captures willingness to pay | Complexity; feature allocation debates |
| **Hybrid** | Products with both team and usage dimensions | Captures both vectors of value | Pricing page complexity; billing system overhead |

**Pricing decision checklist:**
- What is the primary value metric (seats, usage, features)?
- What does the competitive landscape charge?
- What is the buyer's willingness to pay (from user research)?
- Does the model encourage or discourage adoption?
- Can the billing system support this model?

---

## Do / Don't

- **Do** define the target segment narrowly. "Small businesses" is not a segment.
  "10–50 person SaaS companies that manage invoicing manually" is a segment.
- **Do** involve sales and CS in GTM planning early. They know what customers
  actually ask for and what objections arise.
- **Do** stagger launches. Soft launch to a beta group → expand to existing customers →
  public launch. Each stage surfaces issues before they hit the widest audience.
- **Do** set measurable launch goals *before* launch. Defining success after the
  fact leads to rationalization.
- **Do** prepare a competitive battle card for sales before a T1 launch. They will
  be asked "how is this different from X?" on day one.
- **Do** update pricing pages and documentation before the feature goes live, not
  after.
- **Don't** launch on a Friday. Support capacity is lowest on weekends. Monday or
  Tuesday launches give the team a full week to respond.
- **Don't** skip the retrospective. The temptation to move on to the next thing
  is strong. The retro is where the team actually learns.
- **Don't** treat every feature as a T1 launch. Launch fatigue is real. Over-hyping
  minor updates erodes credibility and attention for major ones.
- **Don't** set pricing in isolation from product packaging. Price and packaging
  are intertwined — changing one without the other creates misalignment.
- **Don't** assume the first GTM motion is permanent. PLG can transition to
  sales-assisted as the product moves upmarket. Plan for motion evolution.

---

## Common Pitfalls

1. **Build-it-and-they-will-come.** Shipping a feature with no launch plan and
   wondering why adoption is low. Solution: every feature above T3 gets a launch
   plan. No exceptions.
2. **One-size-fits-all launch.** Running the same launch playbook for a major product
   and a minor feature toggle. Solution: tier the launch and scale effort to impact.
3. **Internal misalignment.** Sales promises features that don't exist; marketing
   messages don't match the product reality. Solution: shared GTM doc with
   positioning, timeline, and scope reviewed by all teams before launch.
4. **Premature scaling.** Spending on paid acquisition before product-market fit is
   proven. Solution: validate activation and retention metrics with organic traffic
   first.
5. **Pricing anchored to cost, not value.** Setting price based on what it cost to
   build rather than what the customer is willing to pay. Solution: research
   willingness to pay through Van Westendorp or Gabor-Granger surveys.
6. **Ignoring existing customers.** Focusing launch energy on acquisition while
   existing customers don't know the feature exists. Solution: existing customer
   comms are a required launch activity for T1 and T2.

---

## Launch Checklist

### Pre-Launch

- [ ] Target segment and personas defined
- [ ] Value proposition articulated (problem, solution, differentiation)
- [ ] Launch tier assigned (T1/T2/T3)
- [ ] Launch goals set with measurable targets
- [ ] Pricing and packaging finalized
- [ ] Sales enablement materials created (one-pager, FAQ, battle card)
- [ ] Marketing assets prepared (landing page, blog, email, social)
- [ ] Documentation updated (help articles, API docs, guides)
- [ ] Internal teams trained (sales, CS, support)
- [ ] Analytics and tracking configured

### Launch Day

- [ ] Product deployed and verified in production
- [ ] In-app announcements activated
- [ ] Customer email sent
- [ ] Blog post published
- [ ] Social media posts scheduled/published
- [ ] Sales team notified with talking points
- [ ] Support team briefed and monitoring channels

### Post-Launch

- [ ] Week 1 metrics reviewed against goals
- [ ] Customer feedback collected and categorized
- [ ] Quick-win issues fixed (UX friction, bugs, messaging gaps)
- [ ] 30-day launch retrospective scheduled
- [ ] Retrospective completed with documented learnings
- [ ] Insights fed back to product roadmap
