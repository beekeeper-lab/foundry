# Data Visualization Best Practices

Standards for selecting, designing, and presenting data visualizations. The
purpose of every visualization is to make the data's message immediately clear.
If a chart requires a paragraph of explanation, the chart has failed.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Chart selection** | Choose by data relationship (see selection matrix below) | Custom visualizations (D3.js, Observable) only when standard charts are insufficient |
| **Color palette** | Sequential single-hue for magnitude; diverging two-hue for above/below threshold | Categorical palette (max 7 colors) for nominal dimensions; branded palette if mandated |
| **Colorblind safety** | Use palettes from ColorBrewer or Tableau's colorblind-safe set | Supplement color with shape, pattern, or direct labels for critical charts |
| **Axis baseline** | Y-axis starts at zero for bar charts and area charts | Non-zero baseline acceptable for line charts showing narrow-range fluctuation (must be labeled) |
| **Labels** | Direct labels on data points when ≤ 12 items; legend otherwise | Tooltips for dense charts; annotation callouts for key data points |
| **Number formatting** | Abbreviate large numbers (1.2M, 450K); use locale-appropriate separators | Full precision in tables and exported data |
| **Aspect ratio** | ~16:9 for time-series; ~1:1 for scatter plots | Tall aspect ratio for horizontal bar charts with many categories |
| **Animation** | No animation by default; transitions only for state changes in interactive views | Animated builds for presentation decks (not dashboards) |

---

## Do / Don't

- **Do** choose the chart type based on the data relationship, not aesthetics. A bar chart that answers the question clearly is better than a fancy visualization that obscures it.
- **Do** label axes with the metric name, unit, and time grain. "Revenue ($M) — Monthly" not just "Revenue."
- **Do** use consistent color encoding across dashboards. If blue means "Actual" and gray means "Target" on one chart, maintain that convention everywhere.
- **Do** sort bar charts by value (largest to smallest) unless the axis has an inherent order (time, rank, category hierarchy).
- **Do** add reference lines for targets, benchmarks, or thresholds. A metric without context is just a number.
- **Do** test every visualization in grayscale to verify it is readable without color.
- **Do** use annotations to highlight notable events (product launches, outages, seasonal peaks) directly on the chart.
- **Don't** use pie charts for more than 5 categories or for comparing values across time. Use bar charts instead.
- **Don't** use 3D charts, ever. They distort proportions and make accurate comparison impossible.
- **Don't** use dual Y-axes with different scales. Two overlaid lines on mismatched scales create false correlations. Use two separate charts or index both series to a common baseline.
- **Don't** truncate the Y-axis on bar charts. Bars encode value by length; a truncated axis makes small differences look dramatic.
- **Don't** use red/green as the only distinction between good/bad. Use blue/orange or add icons/patterns for colorblind accessibility.
- **Don't** add chartjunk: grid lines heavier than data, excessive tick marks, decorative backgrounds, or unnecessary borders.

---

## Chart Selection Matrix

Select the chart type based on what you are showing:

| Data Relationship | Recommended Chart | When to Use |
|------------------|-------------------|-------------|
| **Change over time** | Line chart | Continuous metric over time; ≤ 5 series |
| **Change over time (volume)** | Area chart (stacked) | Showing composition of a total over time |
| **Comparison (few categories)** | Vertical bar chart | Comparing ≤ 12 categories at one point in time |
| **Comparison (many categories)** | Horizontal bar chart | Comparing > 12 categories; long category labels |
| **Proportion / part-to-whole** | Stacked bar chart (100%) | Showing percentage breakdown across categories |
| **Proportion (single point)** | Donut chart or waffle chart | Showing a single metric as % of total (≤ 5 segments) |
| **Distribution** | Histogram or box plot | Showing spread, skew, and outliers of a single variable |
| **Correlation** | Scatter plot | Showing relationship between two continuous variables |
| **Ranking** | Horizontal bar chart (sorted) | Ordered list of items by a single metric |
| **Geographic** | Choropleth or bubble map | Showing metric variation across regions |
| **Flow / funnel** | Funnel chart | Showing conversion through sequential stages |
| **KPI snapshot** | Big number card with comparison | Single headline metric with directional context |

---

## Color Guidelines

### Sequential Palette (Magnitude)

Use a single hue with varying lightness to represent low-to-high values.
Appropriate for heatmaps, choropleths, and any chart encoding a continuous scale.

```
Light (low) ████████████████████ Dark (high)
     #deebf7  #9ecae1  #3182bd  #08519c
```

### Diverging Palette (Above/Below Threshold)

Use two hues diverging from a neutral midpoint. Appropriate for variance-to-plan,
profit/loss, or any metric with a meaningful center point.

```
Below ██████████ Neutral ██████████ Above
#d73027  #fc8d59   #ffffbf   #91bfdb  #4575b4
```

### Categorical Palette (Nominal Dimensions)

Use distinct hues with similar saturation and lightness. Maximum 7 colors;
group remaining categories into "Other."

```
██ #4e79a7  ██ #f28e2b  ██ #e15759  ██ #76b7b2
██ #59a14f  ██ #edc948  ██ #b07aa1
```

### Accessibility Rules

- Test with a colorblind simulator (Coblis, Sim Daltonism) before publishing.
- Never encode meaning through color alone — pair with shape, pattern, or text label.
- Ensure a contrast ratio of at least 3:1 between adjacent colors in a chart.
- Provide alt text for charts in reports and documentation.

---

## Common Pitfalls

1. **Spaghetti charts.** A line chart with 15 overlapping series is unreadable. Limit to 5 series; use small multiples (one chart per series) for more.
2. **Rainbow color maps.** Using a rainbow gradient (red → green → blue) for continuous data creates perceptual non-uniformity — equal data steps appear as unequal color steps. Use sequential single-hue or perceptually uniform palettes (viridis, inferno).
3. **Misleading area.** In bubble charts or icon arrays, doubling the radius quadruples the visual area. Scale by area (radius ∝ √value), not by radius.
4. **Overuse of pie charts.** Humans are poor at comparing angles. A simple table or bar chart communicates the same information more accurately. Reserve pie/donut charts for 2–4 segment, single-point-in-time summaries.
5. **Ignoring aspect ratio.** A time-series chart that is too wide flattens trends; too narrow exaggerates them. The "banking to 45°" principle: adjust aspect ratio so the average slope of important trends is near 45°.
6. **Dark mode afterthought.** Charts designed for light backgrounds become unreadable on dark backgrounds. If the dashboard supports dark mode, design charts for both themes from the start.

---

## Checklist

- [ ] Chart type matches the data relationship (per selection matrix)
- [ ] Axes are labeled with metric name, unit, and time grain
- [ ] Y-axis starts at zero for bar and area charts (exception documented if not)
- [ ] Color palette is colorblind-safe and tested in grayscale
- [ ] Categorical colors are limited to ≤ 7; remaining items grouped as "Other"
- [ ] Color encoding is consistent across the dashboard (same meaning = same color)
- [ ] Data points are directly labeled when ≤ 12 items; legend used otherwise
- [ ] Reference lines or annotations provide context (targets, benchmarks, events)
- [ ] No 3D effects, dual Y-axes, or decorative chartjunk
- [ ] Chart is readable at the target display size (dashboard tile, not full screen)
- [ ] Alt text is provided for charts in exported reports and documentation
