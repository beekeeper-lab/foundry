# Feature Lifecycle Management

The end-to-end lifecycle of a product feature from initial discovery through
delivery, iteration, and eventual sunset. Managing features as lifecycle assets
prevents feature bloat, ensures investment follows impact, and gives teams a
framework for the hardest product decision: when to stop.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Lifecycle stages** | Discovery → Definition → Delivery → Launch → Growth → Maturity → Sunset | Simplified 4-stage (Ideate → Build → Run → Retire) for small teams |
| **Stage gate reviews** | Product manager + engineering lead at each transition | Cross-functional review board for features with revenue impact >$100K |
| **Discovery method** | Customer interviews + usage data analysis | Prototype testing for UX-heavy features; market research for new segments |
| **Delivery methodology** | Iterative (2-week sprints with incremental delivery) | Big-bang delivery for regulated or hardware-dependent features |
| **Feature flags** | Enabled for all new features (gradual rollout) | Direct deployment for low-risk changes; long-lived flags for premium features |
| **Success metrics** | Adoption rate + retention impact + support ticket volume | Revenue attribution for monetized features; NPS delta for experience features |
| **Sunset trigger** | <5% monthly active usage AND declining trend for 2+ quarters | Cost-based trigger when maintenance cost exceeds value delivered |
| **Sunset notice period** | 6 months for paid features; 3 months for free features | 12 months for enterprise contracts; immediate for security-compromised features |

---

## Lifecycle Stages

```
Discovery → Definition → Delivery → Launch → Growth → Maturity → Sunset
   │            │           │          │         │          │         │
   │ Validate   │ Specify   │ Build    │ Release │ Optimize │ Maintain│ Remove
   │ problem    │ solution  │ & test   │ & adopt │ & expand │ & harden│ & migrate
   v            v           v          v         v          v         v
```

### Discovery

**Purpose:** Validate that a real problem exists and is worth solving.

**Activities:**
- Customer interviews (5–10 per segment minimum)
- Usage data analysis for existing product areas
- Competitive landscape review for the problem space
- Problem sizing: how many users are affected? How painful is it?

**Exit criteria:**
- Problem is validated with customer evidence (not just internal intuition)
- Target persona and use case are defined
- Opportunity is sized and prioritized against other candidates

### Definition

**Purpose:** Specify the solution at enough detail to estimate, plan, and build.

**Activities:**
- Write user stories with acceptance criteria
- Create wireframes or prototypes for key flows
- Define success metrics (what will we measure to know this worked?)
- Estimate effort and identify technical risks
- Determine the feature flag strategy

**Exit criteria:**
- User stories are written and reviewed by engineering
- Success metrics are defined with baseline and target values
- Effort estimate is complete (t-shirt size or story points)
- Build/buy/partner decision is made

### Delivery

**Purpose:** Build, test, and prepare the feature for release.

**Activities:**
- Implement in iterative increments behind a feature flag
- Write automated tests (unit, integration, and key E2E paths)
- Conduct internal dogfooding and beta testing
- Prepare documentation and support materials
- Complete security and performance reviews

**Exit criteria:**
- All acceptance criteria pass
- Test coverage meets team standards
- Performance benchmarks are met
- Documentation is published
- Feature flag is ready for gradual rollout

### Launch

**Purpose:** Release the feature to users and drive initial adoption.

**Activities:**
- Gradual rollout via feature flag (1% → 10% → 50% → 100%)
- Monitor error rates, performance, and support tickets during rollout
- Execute GTM plan (see `go-to-market.md`)
- Collect early user feedback

**Exit criteria:**
- Feature is enabled for 100% of target users
- Error rate is within acceptable thresholds
- Initial adoption metrics are tracking

### Growth

**Purpose:** Optimize the feature for maximum impact and adoption.

**Activities:**
- Analyze usage patterns and identify friction points
- Run A/B experiments to optimize key flows
- Extend the feature based on user feedback (iteration, not reinvention)
- Develop advanced use cases and power-user capabilities
- Create educational content (tutorials, webinars, case studies)

**Exit criteria:**
- Feature reaches target adoption rate
- Key success metrics meet or exceed targets
- Diminishing returns on further investment are evident

### Maturity

**Purpose:** Maintain the feature with minimal investment while it delivers
ongoing value.

**Activities:**
- Monitor health metrics (usage trends, error rates, support volume)
- Apply security patches and dependency updates
- Address critical bugs only (no new development)
- Evaluate ongoing maintenance cost vs. value delivered

**Exit criteria:**
- Usage drops below sunset threshold, OR
- Maintenance cost exceeds value delivered, OR
- A replacement feature is planned or available

### Sunset

**Purpose:** Remove the feature gracefully to reduce complexity and maintenance
burden.

**Activities:**
- Announce deprecation with clear timeline and migration path
- Provide migration tools or documentation for affected users
- Implement usage warnings in the product (in-app banners, API deprecation headers)
- Remove feature code, configuration, and documentation after the notice period
- Verify no residual dependencies or broken references

**Exit criteria:**
- All users are migrated or notified
- Feature code is removed from the codebase
- Documentation references are updated or removed
- No residual technical debt from the feature

---

## Feature Health Scorecard

Track these metrics monthly for every feature past the Launch stage:

| Metric | Healthy | Watch | Sunset Candidate |
|--------|---------|-------|-----------------|
| **Monthly active users** | Stable or growing | Declining <10% QoQ | <5% of total users |
| **Retention (30-day)** | >60% return usage | 40–60% return | <40% return |
| **Support tickets** | Low, declining | Moderate, stable | High relative to usage |
| **Error rate** | Within SLO | Occasional spikes | Persistent failures |
| **Maintenance cost** | Low (no dedicated effort) | Moderate (regular patches) | High (frequent firefighting) |
| **Revenue attribution** | Positive contribution | Neutral | Negative (cost exceeds revenue) |

---

## Do / Don't

- **Do** define success metrics before building. If you cannot articulate what
  success looks like, you cannot evaluate whether the feature is worth maintaining.
- **Do** use feature flags for every new feature. Gradual rollout protects users
  and gives you a kill switch.
- **Do** plan for sunset from day one. Every feature should have a documented
  sunset trigger, even if it is "never" (with justification).
- **Do** review feature health quarterly. A 15-minute review per feature prevents
  zombie features that nobody uses but everyone maintains.
- **Do** communicate sunset decisions early and clearly. Surprises erode trust.
  Give users time and tools to migrate.
- **Do** remove dead code after sunset. Commented-out features and unused flags
  are technical debt that slows down the entire codebase.
- **Don't** skip discovery. Building a solution before validating the problem is
  the most expensive mistake in product development.
- **Don't** treat delivery as the finish line. Launch is the halfway point.
  Growth and maturity determine whether the investment paid off.
- **Don't** keep features alive because "someone might use it." Data-driven
  decisions require data. If <5% of users touch it in a quarter, it is a sunset
  candidate.
- **Don't** sunset without a migration path. Removing a feature that users depend
  on without an alternative damages trust permanently.
- **Don't** let features accumulate without lifecycle review. Every unmaintained
  feature increases complexity for every future change. Feature bloat is the silent
  killer of product velocity.

---

## Common Pitfalls

1. **Perpetual discovery.** Research and validation without ever committing to build.
   Solution: timebox discovery (2–4 weeks) and force a go/no-go decision at the
   gate review.
2. **Skipping definition.** Jumping from "customers want X" to "let's build X"
   without defining scope, metrics, or acceptance criteria. Solution: require a
   definition document before sprint commitment.
3. **Feature flag debt.** Flags left in the codebase long after rollout is complete.
   Solution: add a flag expiration date at creation time. Clean up flags within
   one sprint of reaching 100% rollout.
4. **Launch-and-forget.** Shipping a feature and immediately moving to the next
   one without monitoring adoption or iterating. Solution: block the next initiative
   until the 30-day post-launch review is complete.
5. **Zombie features.** Features with negligible usage that nobody dares to remove.
   They consume maintenance effort, slow down refactors, and confuse new users.
   Solution: quarterly health scorecard review with a mandatory sunset-or-justify
   decision for features below the usage threshold.
6. **Sunset avoidance.** Product teams resist sunsetting because it feels like
   admitting failure. Solution: reframe sunset as responsible product management.
   Celebrate well-managed sunsets the same way you celebrate launches.

---

## Checklist

- [ ] Every feature has defined lifecycle stages with exit criteria
- [ ] Discovery is timeboxed with a go/no-go gate review
- [ ] Success metrics are defined before delivery begins (baseline + target)
- [ ] Feature flags are used for gradual rollout with documented expiration dates
- [ ] Post-launch review is completed within 30 days of reaching 100% rollout
- [ ] Feature health scorecard is reviewed quarterly
- [ ] Sunset triggers are documented for every feature (usage threshold + decline trend)
- [ ] Sunset notice periods are defined (6 months paid, 3 months free)
- [ ] Migration paths are documented before any sunset announcement
- [ ] Dead code and feature flags are removed within one sprint of sunset completion
