# Data Analyst -- Outputs

This document enumerates every artifact the Data Analyst is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. KPI Definitions & Metric Catalog

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | KPI Definition Document                            |
| **Cadence**        | When new metrics are required or definitions change |
| **Template**       | `kpi-definition.md`                                |
| **Format**         | Markdown                                           |

**Description.** Precise definitions of key performance indicators and business
metrics including calculation logic, data sources, refresh cadence, and
ownership. The metric catalog is the single source of truth for how metrics
are calculated across the organization.

**Quality Bar:**
- Every metric has a unique name, written definition, and calculation formula.
- Data source and specific tables/columns are documented.
- Refresh cadence and expected latency are stated.
- Metric owner is assigned.
- Edge cases and exclusions are explicitly documented (e.g., "excludes internal
  test accounts").
- Historical changes to metric definitions are versioned.

**Downstream Consumers:** Business Analyst (for requirements alignment), Team
Lead (for goal tracking), Developer (for event tracking implementation),
Data Engineer (for pipeline requirements).

---

## 2. Dashboards & Automated Reports

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Dashboard or Automated Report                      |
| **Cadence**        | When new reporting needs arise or metrics change   |
| **Template**       | `dashboard-spec.md`                                |
| **Format**         | Dashboard tool (Metabase, Looker, Tableau, etc.) + Markdown spec |

**Description.** Interactive dashboards and automated reports that surface
metrics for stakeholders. Each dashboard is purpose-built for a specific
audience and set of decisions.

**Quality Bar:**
- Dashboard has a stated purpose and target audience.
- All metrics displayed have documented definitions in the metric catalog.
- Visualizations are appropriate for the data type (no pie charts for 20
  categories, no dual axes without justification).
- Filters and drill-downs enable self-service exploration.
- Dashboard loads within acceptable performance thresholds.
- Color choices are accessible (color-blind safe palettes).
- Date ranges, refresh timestamps, and data freshness are visible.
- A stakeholder has reviewed and confirmed the dashboard meets their needs.

**Downstream Consumers:** Team Lead (for progress tracking), Business Analyst
(for requirements validation), stakeholders (for decision-making).

---

## 3. User Behavior Analysis

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | User Behavior Analysis Report                      |
| **Cadence**        | Per task assignment or investigation request        |
| **Template**       | `analysis-report.md`                               |
| **Format**         | Markdown with embedded visualizations              |

**Description.** Analytical reports covering user behavior patterns including
funnel analysis, cohort retention, segmentation, and trend identification.
Reports translate raw behavioral data into actionable insights about how
users interact with the product.

**Quality Bar:**
- Analysis answers a clearly stated business question.
- Methodology is documented and reproducible (queries, parameters, date ranges).
- Findings distinguish correlation from causation.
- Segments and cohorts are defined with explicit criteria.
- Visualizations include labeled axes, legends, and annotations for key findings.
- Sample sizes are stated for all reported metrics.
- Limitations and caveats are explicitly noted.
- Recommendations are actionable and supported by the evidence presented.

**Downstream Consumers:** Business Analyst (for product decisions), UX/UI
Designer (for design insights), Developer (for feature prioritization), Team
Lead (for strategic planning).

---

## 4. A/B Test Design & Results

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Experiment Design and Results Report               |
| **Cadence**        | Per experiment request                             |
| **Template**       | `ab-test-plan.md`                                  |
| **Format**         | Markdown                                           |

**Description.** End-to-end experiment documentation covering hypothesis,
test design, statistical methodology, monitoring plan, and results analysis.
Ensures experiments are designed with rigor and results are interpreted
correctly.

**Quality Bar:**
- Hypothesis is clearly stated with expected direction and magnitude.
- Primary and secondary metrics are defined before the test starts.
- Sample size calculation includes minimum detectable effect, significance
  level, and statistical power.
- Randomization unit and method are documented.
- Guard-rail metrics are defined to detect harmful side effects.
- Results include confidence intervals, not just point estimates.
- Winner declaration criteria are pre-specified.
- Post-experiment report includes learning and next steps.

**Downstream Consumers:** Developer (for implementation), Business Analyst
(for product decisions), Team Lead (for prioritization based on results).

---

## 5. Ad-Hoc Analysis & Decision Briefs

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Ad-Hoc Analysis or Decision Brief                  |
| **Cadence**        | On demand per stakeholder request                  |
| **Template**       | `analysis-report.md`                               |
| **Format**         | Markdown                                           |

**Description.** Targeted analysis responding to specific business questions.
Decision briefs synthesize data into clear findings and recommendations to
support time-sensitive decisions.

**Quality Bar:**
- The business question being answered is stated upfront.
- Data sources and date ranges are documented.
- Methodology is described at a level appropriate for the audience.
- Findings are presented with supporting evidence.
- Recommendations include trade-offs and confidence levels.
- Analysis is completed within the agreed timeframe.
- Follow-up questions and areas for deeper investigation are noted.

**Downstream Consumers:** Requesting stakeholder, Team Lead (for planning),
Business Analyst (for requirements refinement).

---

## 6. Self-Service Analytics Assets

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Reusable Queries, Views, and Documentation         |
| **Cadence**        | Ongoing as patterns emerge                         |
| **Template**       | None (follows project query conventions)           |
| **Format**         | SQL views, saved queries, documentation            |

**Description.** Reusable analytics assets that enable other team members to
answer routine questions without analyst involvement. Includes documented
queries, materialized views, lookup tables, and self-service guides.

**Quality Bar:**
- Queries are parameterized and documented with usage examples.
- Views are optimized for common access patterns.
- Naming conventions are consistent with the project's data catalog.
- Documentation explains what each asset does, when to use it, and its
  limitations.
- Assets are maintained -- outdated or broken queries are removed or fixed.
- No hardcoded credentials or environment-specific values.

**Downstream Consumers:** All team members (for self-service reporting),
Data Engineer (for optimization feedback).

---

## Output Format Guidelines

- Analysis follows the stack-specific conventions document (`stacks/<stack>/conventions.md`).
- Queries and analysis code follow the same conventions as production code:
  consistent formatting, meaningful aliases, documented CTEs.
- Reports are written as if the reader has no prior context about the analysis.
- All outputs are committed to the project repository or published to the
  designated analytics platform. No deliverables live in personal notebooks
  or local files only.
