# Color Contrast

Standards for meeting WCAG 2.2 color contrast requirements. All text and UI components must
meet minimum contrast ratios to ensure readability for users with low vision, color blindness,
and in suboptimal viewing conditions.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Contrast checker** | Chrome DevTools contrast ratio inspector | Colour Contrast Analyser (TPGi), WebAIM Contrast Checker, Stark (Figma plugin) |
| **Design tool plugin** | Stark (Figma) | Able (Figma), A11y Color Contrast (Sketch), axe for Designers |
| **Automated testing** | axe-core color contrast rules | Lighthouse, Pa11y, WAVE |
| **Color palette tool** | Leonardo (Adobe) for accessible palette generation | Huetone, ColorBox (Lyft), Tailwind CSS color system |

---

## Contrast Ratio Requirements

| Element | WCAG Level AA | WCAG Level AAA |
|---------|--------------|----------------|
| **Normal text** (< 18pt / < 14pt bold) | 4.5:1 | 7:1 |
| **Large text** (≥ 18pt / ≥ 14pt bold) | 3:1 | 4.5:1 |
| **UI components** (borders, icons, focus indicators) | 3:1 | Not defined |
| **Graphical objects** (charts, diagrams) | 3:1 | Not defined |
| **Disabled elements** | Exempt | Exempt |
| **Decorative elements** | Exempt | Exempt |
| **Logos and brand text** | Exempt | Exempt |

---

## Do / Don't

- **Do** check contrast ratios during design — catching issues in Figma is cheaper than
  fixing them in code.
- **Do** provide sufficient contrast for all interactive states: default, hover, focus,
  active, disabled (disabled elements are exempt but should still be distinguishable).
- **Do** ensure placeholder text meets 4.5:1 contrast — or use visible labels instead of
  relying on placeholders.
- **Do** use a tool like Leonardo or Huetone to generate entire color palettes that meet
  contrast requirements by design.
- **Do** test contrast in both light and dark themes — a palette that passes in light mode
  may fail in dark mode.
- **Don't** rely on color alone to convey information (WCAG 1.4.1 Use of Color) — use
  icons, patterns, labels, or underlines as secondary indicators.
- **Don't** use light gray text on white backgrounds for "subtle" design — this fails contrast
  requirements and is unreadable for low-vision users.
- **Don't** assume brand colors are immutable — adjust for accessibility or use compliant
  alternatives in UI contexts.
- **Don't** ignore non-text contrast — input field borders, chart segments, toggle switches,
  and icons all need 3:1 against their background.

---

## Common Pitfalls

1. **Placeholder text with insufficient contrast.** Placeholders styled as `#999` on `#fff`
   yield a 2.85:1 ratio, failing WCAG AA. Use visible labels above inputs and treat
   placeholders as supplementary hints, not primary labels.

2. **Color as the sole differentiator.** Red/green for error/success states, colored dots
   without labels, chart lines distinguished only by hue — all fail for color-blind users
   (~8% of males). Add icons, patterns, text labels, or shape differences.

3. **Dark mode contrast failures.** Inverting a light theme rarely produces compliant dark
   mode. Pure white text (#fff) on dark gray (#333) passes, but accent colors and secondary
   text often fall below thresholds. Test every color combination in dark mode independently.

4. **Ignoring non-text contrast.** Input borders, icon buttons, toggle tracks, slider
   thumbs, and chart segments are covered under WCAG 1.4.11 Non-text Contrast (3:1 ratio).
   Teams that only test text contrast miss these.

5. **Focus indicator contrast.** WCAG 2.4.11 (Focus Not Obscured) and 2.4.13 (Focus
   Appearance) in WCAG 2.2 require focus indicators to be visible. A thin dotted gray
   outline on a light background fails. Use solid outlines with 3:1+ contrast.

---

## Accessible Color Palette Generation

```javascript
// Using Leonardo (Adobe) to generate an accessible color palette
// Install: npm install @adobe/leonardo-contrast-colors

import { Theme, Color, BackgroundColor } from "@adobe/leonardo-contrast-colors";

const gray = new BackgroundColor({
  name: "gray",
  colorKeys: ["#cacaca"],
  ratios: [1, 1.25, 1.5, 2, 3, 4.5, 7, 10],  // Each ratio is WCAG-compliant
});

const blue = new Color({
  name: "blue",
  colorKeys: ["#0054a6"],
  ratios: [3, 4.5, 7],  // Ratios for UI components, normal text, enhanced text
});

const theme = new Theme({
  colors: [blue],
  backgroundColor: gray,
  lightness: 97,  // Light theme
});

console.log(theme.contrastColorValues);
// Outputs hex values guaranteed to meet specified contrast ratios
```

```css
/* Accessible form field styling with sufficient contrast */
.form-input {
  border: 2px solid #595959;       /* 7:1 against #fff — passes AA & AAA */
  color: #1a1a1a;                  /* 16.6:1 against #fff */
  background-color: #ffffff;
}

.form-input::placeholder {
  color: #595959;                  /* 7:1 against #fff — passes AA */
}

.form-input:focus {
  outline: 3px solid #0054a6;      /* 7.3:1 against #fff */
  outline-offset: 2px;
}

.form-input--error {
  border-color: #b3261e;           /* 5.9:1 against #fff */
}

.form-error-message {
  color: #b3261e;                  /* 5.9:1 against #fff */
}

/* Error message includes icon — not relying on color alone */
.form-error-message::before {
  content: "⚠ ";
}
```

```css
/* Color-blind safe data visualization */
.chart-series-1 { color: #0077bb; }  /* Blue */
.chart-series-2 { color: #ee7733; }  /* Orange */
.chart-series-3 { color: #009988; }  /* Teal */
.chart-series-4 { color: #cc3311; }  /* Red */

/* Supplement with patterns for print and color blindness */
.chart-series-1 { stroke-dasharray: none; }         /* Solid */
.chart-series-2 { stroke-dasharray: 8 4; }          /* Dashed */
.chart-series-3 { stroke-dasharray: 2 2; }          /* Dotted */
.chart-series-4 { stroke-dasharray: 8 4 2 4; }      /* Dash-dot */
```

---

## Testing Workflow

```
1. Design phase: Check every color pair in Stark/Figma contrast checker
2. Development: Run axe-core contrast rules in unit tests
3. Review: Use Chrome DevTools "Rendering > Emulate vision deficiencies"
4. QA: Test with Colour Contrast Analyser (CCA) on rendered pages
5. CI: Pa11y or Lighthouse flags contrast failures as build errors
```

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| Colour Contrast Analyser (CCA) | Desktop app for testing contrast of any on-screen element |
| WebAIM Contrast Checker | Quick web-based checker for individual color pairs |
| Stark (Figma/Sketch/Adobe XD) | Design tool plugin for contrast checking during design |
| Leonardo (Adobe) | Generating entire accessible color systems from contrast ratios |
| Huetone | Visual tool for building accessible color palettes with APCA support |
| Who Can Use | Shows how color combinations appear to users with different vision types |

---

## Checklist

- [ ] All normal text meets 4.5:1 contrast ratio against its background
- [ ] All large text (≥18pt or ≥14pt bold) meets 3:1 contrast ratio
- [ ] UI components (borders, icons, focus indicators) meet 3:1 contrast ratio
- [ ] Placeholder text meets 4.5:1 contrast or replaced with visible labels
- [ ] Color is never the sole means of conveying information (icons, text, patterns added)
- [ ] Dark mode tested independently for all contrast requirements
- [ ] Focus indicators meet 3:1 contrast against adjacent colors
- [ ] Data visualizations use patterns, shapes, or labels in addition to color
- [ ] Contrast checked across all interactive states (default, hover, focus, active)
- [ ] Design system color palette generated with built-in contrast compliance
