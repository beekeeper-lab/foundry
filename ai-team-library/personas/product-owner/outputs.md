# Product Owner / Product Manager — Outputs

This document enumerates every artifact the Product Owner / Product Manager is
responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. Product Roadmap

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Product Roadmap                                    |
| **Cadence**        | Created at project start; updated quarterly or on major strategy shifts |
| **Template**       | `personas/product-owner/templates/product-roadmap.md` |
| **Format**         | Markdown                                           |

**Description.** A strategic document that communicates the product direction
over time — what will be built, roughly when, and why. The roadmap organizes
planned work into time horizons (Now / Next / Later or quarterly buckets),
links each initiative to a strategic goal, and provides stakeholders with a
shared understanding of product direction. The roadmap is a living document
that is versioned and updated as priorities evolve.

**Quality Bar:**
- Every initiative on the roadmap links to a strategic goal or success metric.
- Time horizons are explicit: "Now" items have defined scope; "Later" items
  are directional, not commitments.
- Each initiative has a one-sentence value statement explaining why it matters.
- The roadmap includes a version number and last-updated date.
- Completed or deprioritized items are moved to a changelog section, not
  silently deleted.
- The roadmap is concise enough to fit on one page for executive consumption.

**Downstream Consumers:** Team Lead (for sprint planning and capacity
allocation), Business Analyst (for requirements decomposition), Architect (for
technical planning), stakeholders (for alignment and expectation setting).

---

## 2. Prioritized Backlog

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Prioritized Backlog                                |
| **Cadence**        | Maintained continuously; formally reviewed per sprint or cycle |
| **Template**       | `personas/product-owner/templates/prioritized-backlog.md` |
| **Format**         | Markdown                                           |

**Description.** An ordered list of product work items ranked by value using a
consistent prioritization framework (RICE, MoSCoW, or weighted scoring). Each
item includes enough context for the Business Analyst to decompose it into
user stories and for the Team Lead to plan capacity. The backlog is the single
source of truth for what the team should work on next.

**Quality Bar:**
- Every item has a RICE score or MoSCoW classification with documented
  rationale — not just a priority label.
- Items in the top quarter of the backlog have clear value propositions and
  success metrics.
- The backlog is regularly pruned: items older than two cycles without
  advancement are reviewed for removal.
- Each item includes: title, value statement, priority score, target user
  segment, and estimated effort category (S/M/L/XL).
- Dependencies between items are identified and noted.
- The backlog distinguishes between new features, enhancements, technical
  debt, and bugs.

**Downstream Consumers:** Team Lead (for sprint planning), Business Analyst
(for story decomposition), Developer (for context on upcoming work),
stakeholders (for visibility into planned work).

---

## 3. Feature Scoping Document

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Feature Scoping Document                           |
| **Cadence**        | One per major feature or initiative                 |
| **Template**       | `personas/product-owner/templates/feature-scope.md` |
| **Format**         | Markdown                                           |

**Description.** A focused document that defines what a feature includes, what
it excludes, and how success will be measured. The scoping document is the
contract between the Product Owner and the delivery team — it establishes
boundaries so the team knows when the feature is done and the Product Owner
can validate that the outcome matches the intent.

**Quality Bar:**
- The document includes a clear problem statement: what user or business need
  this feature addresses.
- In-scope and out-of-scope sections are explicit, with rationale for each
  exclusion.
- Success metrics are defined, measurable, and time-bound (e.g., "increase
  activation rate by 10% within 30 days of launch").
- Target user segment is identified — not "all users" unless genuinely
  applicable.
- Key assumptions are listed and marked as validated or unvalidated.
- The MoSCoW classification for sub-features is documented: must-have,
  should-have, could-have, will-not-have.
- Risks and open questions are captured with owners and deadlines.

**Downstream Consumers:** Business Analyst (for requirements decomposition),
Architect (for design scoping), UX/UI Designer (for design scope), Team Lead
(for effort estimation and planning), Developer (for implementation context).

---

## 4. Go-to-Market Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Go-to-Market Plan                                  |
| **Cadence**        | One per customer-facing release or major feature    |
| **Template**       | `personas/product-owner/templates/go-to-market.md`  |
| **Format**         | Markdown                                           |

**Description.** A plan that defines how a feature or release will be
introduced to users — who the target audience is, what the messaging says,
how the rollout will be staged, and how success will be measured post-launch.
The go-to-market plan bridges the gap between building a feature and ensuring
users discover, adopt, and benefit from it.

**Quality Bar:**
- Target audience is specific: demographics, segments, or persona types —
  not "everyone."
- Key messaging is concise: one sentence explaining the value proposition
  for the target audience.
- Rollout strategy is defined: big bang, phased, beta, feature flag, or
  percentage rollout, with rationale for the choice.
- Launch checklist includes all dependencies: documentation, support
  training, marketing assets, monitoring dashboards.
- Success metrics are defined with targets and a measurement timeline.
- Rollback criteria are documented: under what conditions the feature will
  be pulled or rolled back.

**Downstream Consumers:** Team Lead (for release coordination), Technical
Writer (for documentation), DevOps / Release Engineer (for deployment
planning), stakeholders (for launch alignment).

---

## 5. Stakeholder Brief

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Stakeholder Brief                                  |
| **Cadence**        | Per sprint, milestone, or on-demand for decisions   |
| **Template**       | `personas/product-owner/templates/stakeholder-brief.md` |
| **Format**         | Markdown                                           |

**Description.** A concise communication artifact that updates stakeholders on
product progress, upcoming priorities, key decisions, and items requiring
stakeholder input. The brief is designed to be consumed in under five minutes
and to drive alignment without requiring a meeting.

**Quality Bar:**
- The brief fits on one page: no more than 500 words plus a summary table.
- Progress is reported against roadmap milestones, not task counts.
- Key decisions made since the last brief are listed with rationale.
- Items requiring stakeholder input are clearly called out with a deadline
  for response.
- Risks or blockers are stated with their impact on the roadmap.
- Tone is factual and forward-looking — no blame, no excuses, no filler.

**Downstream Consumers:** Stakeholders (primary), Team Lead (for alignment
verification), Architect (for strategic context).

---

## 6. Competitive Analysis

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Competitive Analysis                               |
| **Cadence**        | At product inception; refreshed quarterly or when market shifts |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** An assessment of the competitive landscape that informs
product strategy and prioritization decisions. The analysis identifies
competitors, compares capabilities, highlights differentiation opportunities,
and surfaces threats that should influence the roadmap.

**Required Sections:**
1. **Market Overview** — Market size, trends, and dynamics relevant to the
   product.
2. **Competitor Profiles** — For each competitor: name, target market, key
   strengths, key weaknesses, and recent moves (launches, pivots, funding).
3. **Feature Comparison Matrix** — A table comparing the product against
   competitors across key capabilities.
4. **Differentiation Opportunities** — Areas where the product can win based
   on competitor gaps or market underservice.
5. **Threats** — Competitor advantages or market trends that could erode the
   product's position.
6. **Strategic Implications** — How the analysis should influence roadmap
   priorities.

**Quality Bar:**
- Competitor data is sourced and dated — not speculation.
- The comparison matrix uses objective, verifiable criteria.
- Differentiation opportunities are actionable: they can be translated into
  roadmap items.
- The analysis avoids confirmation bias: competitor strengths are acknowledged
  honestly.
- Strategic implications are concrete: "Prioritize feature X to close gap
  with Competitor Y" not "We should be more competitive."

**Downstream Consumers:** Stakeholders (for strategic decisions), Business
Analyst (for requirements context), Architect (for technology benchmarking).

---

## Output Format Guidelines

- All deliverables are written in Markdown and stored in the project repository
  under `docs/product/` or a dedicated product management folder.
- The product roadmap and prioritized backlog are living documents — they are
  updated in place with version history, not replaced with new files each cycle.
- Feature scoping documents are created per initiative and archived (not
  deleted) when the feature is completed or deprioritized.
- Stakeholder briefs are date-stamped and stored chronologically for audit
  trail purposes.
- RICE scores use the standard formula: (Reach x Impact x Confidence) / Effort.
  Document the scale used for each factor (e.g., Impact: 0.25 / 0.5 / 1 / 2 / 3).
- MoSCoW classifications follow the standard definitions: Must have (non-negotiable),
  Should have (important but not critical), Could have (desirable if capacity allows),
  Will not have (explicitly excluded from this scope).
- Cross-reference related documents: roadmap items should link to feature scoping
  documents; backlog items should link to roadmap initiatives.
