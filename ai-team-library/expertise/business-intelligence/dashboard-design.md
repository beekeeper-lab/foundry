# Dashboard Design Patterns

Patterns and standards for designing effective BI dashboards. A well-designed
dashboard answers a specific set of questions for a defined audience without
requiring the viewer to ask "what am I looking at?"

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Layout** | Inverted pyramid — KPIs at top, trends in middle, detail tables at bottom | Left-nav drill-through for operational dashboards; tabbed layout for multi-audience boards |
| **Tile count** | Maximum 8 tiles per dashboard | Up to 12 tiles for executive summaries with small sparkline cards; 4–6 for focused operational views |
| **KPI cards** | Top row: 3–5 headline metrics with comparison to prior period and directional indicator | Sparkline-embedded cards for trend-at-a-glance |
| **Filters** | Global filters at top; scoped filters on individual tiles only when unavoidable | Cascading filter panels for high-cardinality dimensions |
| **Interactivity** | Click-to-filter (cross-filtering) between tiles | Drill-through links to detail dashboards; parameter-driven what-if views |
| **Responsive design** | Fixed-width optimized for 1440px; tested at 1024px | Fluid layout for embedded analytics; mobile-specific dashboard variants |
| **Color palette** | Sequential single-hue for magnitude; diverging for above/below target; categorical max 7 colors | Branded color palette if corporate guidelines mandate it |
| **Refresh indicator** | "Last updated: {timestamp}" label in the header or footer | Auto-refresh badge with countdown timer for real-time dashboards |

---

## Do / Don't

- **Do** start every dashboard with a title, one-sentence purpose statement, and intended audience. Example: "Sales Pipeline — Weekly pipeline health for Sales VPs."
- **Do** place the most important metrics at the top-left (the F-pattern reading position).
- **Do** use consistent time ranges across all tiles by default. A dashboard where one chart shows MTD and another shows trailing-30-days confuses viewers.
- **Do** provide context for every number — comparison to target, prior period, or benchmark. A revenue number without context is meaningless.
- **Do** use whitespace and grouping to create visual hierarchy. Related tiles share a section; unrelated tiles are separated.
- **Do** label axes, include units, and show the time grain (daily, weekly, monthly) on every time-series chart.
- **Don't** use 3D charts, dual-axis charts with mismatched scales, or decorative elements that add no information.
- **Don't** default to auto-scaling y-axes that start at non-zero values — this exaggerates small changes. Start at zero unless there is a documented reason.
- **Don't** embed raw SQL query results as a "dashboard." Tables are supporting detail, not the primary visualization.
- **Don't** overload a single dashboard to serve both executives and analysts. Create separate views: a summary for leadership and a detail view for operators.
- **Don't** hide critical filters behind expand/collapse panels. If a filter changes the meaning of every tile, it must be visible.

---

## Dashboard Types

### Executive Summary

- **Audience:** C-suite, VPs
- **Cadence:** Weekly or monthly review
- **Pattern:** 3–5 KPI cards across the top, 2–3 trend charts, one comparison table. No more than 8 tiles total.
- **Interactivity:** Minimal — click a KPI to drill into a detail dashboard. No ad-hoc filtering.

### Operational Dashboard

- **Audience:** Managers, team leads, on-call engineers
- **Cadence:** Daily or real-time
- **Pattern:** Status indicators (red/amber/green), queue depths, processing rates, error counts. Emphasis on anomaly detection.
- **Interactivity:** Cross-filtering, time range selector, auto-refresh.

### Analytical Explorer

- **Audience:** Analysts, data scientists
- **Cadence:** Ad-hoc
- **Pattern:** Flexible filters, dimension selectors, pivot tables, chart-type toggles. Designed for exploration, not presentation.
- **Interactivity:** High — parameter inputs, drill-anywhere, export to CSV.

### Embedded Analytics

- **Audience:** End users within a product
- **Cadence:** On-demand within the application
- **Pattern:** Scoped to the user's own data. Minimal chrome, integrated with the product's design system.
- **Interactivity:** Limited to filters relevant to the user's context. No access to underlying data outside their scope.

---

## Common Pitfalls

1. **Dashboard as data dump.** Cramming every available metric onto one screen because "someone might need it." Start with the 3 decisions the dashboard supports and work backward to the metrics required.
2. **Inconsistent time zones.** One tile shows UTC timestamps, another shows local time. Standardize on a single display time zone per dashboard and label it.
3. **Unlabeled comparisons.** A KPI card shows "+12%" but does not indicate whether that is week-over-week, month-over-month, or versus target. Always label the comparison basis.
4. **Filter amnesia.** A user applies a filter, navigates away, and returns to find the filter reset. Persist filter state in the URL or session where the platform supports it.
5. **Orphan dashboards.** A dashboard is created for a one-time analysis and never retired. It shows up in search results, confusing new users who assume it is authoritative. Tag dashboards with an expiration date or archive after 90 days of zero views.
6. **Color overload.** Using 12 distinct colors in a categorical chart makes it unreadable. Limit categorical palettes to 7 colors; group remaining categories into "Other."

---

## Checklist

- [ ] Dashboard has a title, purpose statement, and named audience
- [ ] Tile count is ≤ 8 (justified exception documented if exceeded)
- [ ] KPI cards include comparison context (prior period, target, or benchmark)
- [ ] All tiles share a consistent default time range
- [ ] Axes are labeled with units and time grain
- [ ] Y-axes start at zero (or deviation is documented)
- [ ] Color palette is colorblind-safe and limited to ≤ 7 categorical colors
- [ ] Global filters are visible; no hidden filters that change tile meaning
- [ ] "Last updated" timestamp is displayed
- [ ] Dashboard is tagged with an owner and review date
