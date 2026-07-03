# Accessibility Audits and Remediation

## Category
Compliance & Governance

## Applies To

- ux-ui-designer
- developer
- tech-qa
- compliance-risk
- product-owner

Standards for conducting accessibility audits, documenting findings, prioritizing remediation,
and maintaining ongoing compliance. A structured audit process ensures consistent evaluation
and measurable progress toward conformance goals.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Audit methodology** | WCAG-EM (Website Accessibility Conformance Evaluation Methodology) | Section 508 ICT Testing Baseline, Trusted Tester methodology |
| **Issue tracker** | Dedicated accessibility backlog in existing project tracker | Standalone accessibility register, Siteimprove, Level Access AMP |
| **Severity model** | Critical / Major / Minor / Best Practice | CVSS-style scoring, business-impact weighting |
| **Reporting format** | VPAT 2.5 / ACR (Accessibility Conformance Report) | Custom audit report, Siteimprove dashboard, Deque WorldSpace |
| **Audit cadence** | Quarterly full audit, continuous automated scanning | Annual (minimum legal), per-release, continuous |

---

## Audit Process

```
1. Define scope: pages, user flows, assistive technologies, conformance target
2. Automated scan: axe-core, Pa11y, or Lighthouse across all in-scope pages
3. Manual testing: keyboard navigation, screen reader, zoom/reflow, cognitive review
4. Document findings: WCAG criterion, severity, affected element, reproduction steps
5. Prioritize: Critical issues first (blocks access), then Major, Minor, Best Practice
6. Remediate: Fix issues in priority order, verify each fix
7. Retest: Confirm fixes and check for regressions
8. Report: Produce VPAT/ACR with conformance status per criterion
9. Schedule next audit
```

---

## Do / Don't

- **Do** define audit scope explicitly — list every page, user flow, and technology tested.
  An audit without defined scope is unverifiable.
- **Do** combine automated and manual testing — automated tools find ~30-40% of issues;
  manual testing catches the remaining 60-70%.
- **Do** assign severity ratings based on user impact, not technical difficulty to fix.
  A missing form label (easy fix) that blocks a screen reader user from logging in is Critical.
- **Do** create a remediation backlog with WCAG criterion references, reproduction steps,
  and acceptance criteria for each issue.
- **Do** track remediation velocity and report it to stakeholders — visibility drives
  accountability.
- **Don't** audit only the homepage — test representative pages from every template and every
  critical user flow (login, checkout, search, forms).
- **Don't** defer all remediation to a "future accessibility sprint" — integrate fixes into
  regular sprint work alongside features.
- **Don't** close issues without verification — re-test each fix with the same methodology
  that found the original issue.
- **Don't** ignore third-party components in audits — embedded widgets, iframes, and vendor
  tools must also be evaluated.

---

## Common Pitfalls

1. **Scope too narrow.** Auditing only the homepage and login page misses issues in
   dashboards, settings, error pages, and edge cases. Define scope to include at least one
   page per template type and every critical user flow.

2. **Automated-only audits.** Organizations that rely solely on automated scan results
   miss the majority of accessibility issues. A clean axe-core scan does not equal WCAG
   conformance. Automated scanning is step one, not the whole audit.

3. **No remediation prioritization.** Presenting 200 findings without severity rankings
   overwhelms development teams. Categorize by impact: Critical (users blocked), Major
   (significant barriers), Minor (inconvenience), Best Practice (not a WCAG failure).

4. **Fix-and-forget pattern.** Fixing issues once without adding regression tests or
   updating component libraries causes the same issues to reappear in the next release.
   Add automated tests for every fixed issue.

5. **VPAT produced once, never updated.** A VPAT is a snapshot in time. When features
   change, the VPAT must be updated. Include the evaluation date and version number, and
   commit to quarterly reviews.

---

## Severity Classification

| Severity | Definition | SLA |
|----------|-----------|-----|
| **Critical** | User cannot complete a core task (login, checkout, submit form). Blocks access entirely. | Fix within current sprint |
| **Major** | Significant barrier that requires a workaround. User can complete task but with substantial difficulty. | Fix within 2 sprints |
| **Minor** | Inconvenience that does not prevent task completion. Cosmetic or minor usability issue. | Fix within next quarter |
| **Best Practice** | Not a WCAG failure but would improve the experience. Enhancement opportunity. | Backlog — address opportunistically |

---

## Issue Documentation Template

```markdown
## A11Y-042: Missing form labels on checkout address fields

**WCAG Criterion:** 1.3.1 Info and Relationships (Level A)
**Severity:** Critical
**Status:** Open
**Found:** 2026-01-15 (Q1 audit)
**Page:** /checkout/shipping
**Affected Users:** Screen reader users cannot identify address fields

### Description
The shipping address form uses placeholder text as the only label for Street, City, State,
and ZIP fields. Screen readers announce "edit text" without identifying the field purpose.

### Reproduction
1. Navigate to /checkout/shipping
2. Tab to first address field
3. NVDA announces: "edit text" (expected: "Street address, edit text, required")

### Expected Behavior
Each form field has a visible `<label>` element associated via `for`/`id` attributes.

### Remediation
- Add `<label>` elements for each field
- Associate labels with `for` attribute matching input `id`
- Retain placeholders as supplementary hints only

### Acceptance Criteria
- [ ] NVDA announces field label, type, and required state
- [ ] VoiceOver announces field label, type, and required state
- [ ] axe-core reports no label violations on the page
- [ ] Visual labels are visible above each input field
```

---

## Remediation Prioritization Matrix

```
                    HIGH USER IMPACT
                         │
           Critical      │      Major
        (login blocked,  │  (workaround exists,
         no alternative) │   poor experience)
                         │
    ─────────────────────┼─────────────────────
                         │
           Minor         │    Best Practice
        (cosmetic,       │  (enhancement,
         edge case)      │   not a WCAG failure)
                         │
                    LOW USER IMPACT

    LOW EFFORT ──────────────────────── HIGH EFFORT
```

Fix order: Critical (any effort) → Major low-effort → Major high-effort → Minor → Best Practice.

---

## VPAT Template Excerpt

```markdown
## VPAT 2.5 — Product Accessibility Conformance Report

**Product:** [Product Name] v2.4
**Report Date:** 2026-02-15
**WCAG Version:** 2.2 Level AA
**Evaluation Methods:** Automated (axe-core), Manual (NVDA, VoiceOver, keyboard)

### Table 1: Success Criteria, Level A

| Criteria | Conformance Level | Remarks |
|----------|-------------------|---------|
| 1.1.1 Non-text Content | Supports | All images have alt text |
| 1.3.1 Info and Relationships | Partially Supports | Checkout form labels remediated Q1; settings page pending |
| 2.1.1 Keyboard | Supports | All interactive elements keyboard accessible |
| 2.1.2 No Keyboard Trap | Supports | Tested all modal dialogs and custom widgets |
| 4.1.2 Name, Role, Value | Partially Supports | Date picker ARIA labels pending fix (target Q2) |

### Conformance Levels Used
- **Supports:** Fully meets the criterion
- **Partially Supports:** Some functionality meets the criterion
- **Does Not Support:** Criterion is not met
- **Not Applicable:** Criterion is not relevant to the product
```

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| Siteimprove | Enterprise platform for continuous monitoring and compliance dashboards |
| Level Access AMP | Managed accessibility testing platform with expert audit services |
| Deque WorldSpace | Enterprise audit management with axe integration |
| Pope Tech | Continuous monitoring platform built on WAVE engine |
| Evinced | AI-assisted accessibility testing with visual analysis |
| UsableNet | Managed service for audit, remediation, and monitoring |

---

## Checklist

- [ ] Audit scope defined (pages, flows, technologies, conformance target)
- [ ] Automated scan completed across all in-scope pages
- [ ] Manual keyboard testing completed for all interactive elements
- [ ] Screen reader testing completed with at least two screen readers
- [ ] All findings documented with WCAG criterion, severity, and reproduction steps
- [ ] Remediation backlog created with priority assignments and sprint targets
- [ ] Critical issues fixed within current sprint
- [ ] Each fix verified with the same methodology that found the original issue
- [ ] Regression tests added for all remediated issues
- [ ] VPAT/ACR produced with evaluation date, product version, and conformance status
- [ ] Next audit date scheduled (quarterly recommended)
- [ ] Third-party components included in audit scope

---

# ARIA Patterns

Standards for implementing Accessible Rich Internet Applications (ARIA) roles, states, and
properties. Native HTML semantics are the default; ARIA is used only when native elements
cannot provide the required accessibility information.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Reference** | WAI-ARIA Authoring Practices Guide (APG) | MDN ARIA docs, Deque University patterns |
| **Component library** | Native HTML elements first | Radix UI, React Aria (Adobe), Headless UI |
| **Validation** | axe-core ARIA rules | WAVE, ARC Toolkit, browser accessibility tree inspector |
| **Documentation** | Inline code comments for ARIA usage | Storybook a11y addon, component API docs |

---

## The First Rule of ARIA

> If you can use a native HTML element with the semantics and behavior you require already
> built in, do so. Do not repurpose an element and add ARIA role, state, or property to make
> it accessible when a native element already exists.

```html
<!-- BAD — div with ARIA mimicking a button -->
<div role="button" tabindex="0" aria-pressed="false" onclick="toggle()">
  Toggle Setting
</div>

<!-- GOOD — native button element -->
<button type="button" aria-pressed="false" onclick="toggle()">
  Toggle Setting
</button>
```

---

## Do / Don't

- **Do** use native HTML elements (`<button>`, `<nav>`, `<input>`, `<select>`, `<dialog>`)
  before reaching for ARIA — they provide keyboard behavior and semantics for free.
- **Do** pair `role` with required states and properties — a `role="checkbox"` without
  `aria-checked` is incomplete.
- **Do** use landmark roles (`<main>`, `<nav>`, `<aside>`, `<header>`, `<footer>`) to
  create page structure that screen readers can navigate.
- **Do** use `aria-live` regions for dynamic content updates (toast notifications, form
  validation errors, chat messages).
- **Do** test ARIA implementations with an actual screen reader — the accessibility tree
  and the rendered output can diverge.
- **Don't** add `role="presentation"` or `aria-hidden="true"` to interactive elements — this
  removes them from the accessibility tree entirely.
- **Don't** use ARIA to override native semantics unless absolutely necessary (e.g., do not
  add `role="button"` to an `<a>` tag — use a `<button>` instead).
- **Don't** duplicate information already provided by native semantics — adding
  `role="navigation"` to a `<nav>` element is redundant.
- **Don't** use `aria-label` on elements that already have visible text — use
  `aria-labelledby` to reference the visible text instead.

---

## Common Pitfalls

1. **Using ARIA as a substitute for semantic HTML.** ARIA provides accessibility information
   but does not add behavior. A `<div role="button">` does not respond to Enter/Space
   keypresses or receive focus without explicit `tabindex` and event handlers. Use `<button>`
   instead.

2. **Orphaned ARIA states.** Adding `aria-expanded` to a trigger without updating it via
   JavaScript means the screen reader announces the wrong state. Ensure every ARIA state
   attribute is dynamically managed and reflects the current UI state.

3. **Overusing aria-live.** Setting `aria-live="assertive"` on multiple regions creates a
   cacophony of announcements. Use `aria-live="polite"` by default and reserve `assertive`
   for urgent alerts (errors, session timeouts).

4. **Missing required ARIA properties.** Each ARIA role has required and supported states.
   For example, `role="combobox"` requires `aria-expanded` and `aria-controls`. Consult the
   WAI-ARIA specification for the complete list.

5. **Hiding content from assistive technology unintentionally.** `aria-hidden="true"` on a
   parent hides all descendants, including focusable elements. If a user can Tab to a
   hidden element, the screen reader announces nothing, creating confusion.

---

## Common Widget Patterns

### Modal Dialog

```html
<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Deletion</h2>
  <p>Are you sure you want to delete this item? This action cannot be undone.</p>
  <button type="button" autofocus>Cancel</button>
  <button type="button">Delete</button>
</div>
```

**Requirements:**
- Focus moves into the dialog on open (first focusable element or the dialog itself)
- Focus is trapped within the dialog while open
- Escape key closes the dialog
- Focus returns to the triggering element on close

### Tabs

```html
<div role="tablist" aria-label="Account settings">
  <button role="tab" aria-selected="true" aria-controls="panel-profile" id="tab-profile">
    Profile
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-security" id="tab-security"
          tabindex="-1">
    Security
  </button>
</div>
<div role="tabpanel" id="panel-profile" aria-labelledby="tab-profile">
  <!-- Profile content -->
</div>
<div role="tabpanel" id="panel-security" aria-labelledby="tab-security" hidden>
  <!-- Security content -->
</div>
```

**Requirements:**
- Arrow keys move between tabs (Left/Right for horizontal, Up/Down for vertical)
- Only the active tab is in the tab order (`tabindex="0"`)
- Inactive tabs use `tabindex="-1"`
- Tab key moves focus from the active tab into the tab panel

### Accordion

```html
<div>
  <h3>
    <button aria-expanded="true" aria-controls="section1-content" id="section1-header">
      Billing Information
    </button>
  </h3>
  <div id="section1-content" role="region" aria-labelledby="section1-header">
    <!-- Expanded content -->
  </div>
  <h3>
    <button aria-expanded="false" aria-controls="section2-content" id="section2-header">
      Shipping Address
    </button>
  </h3>
  <div id="section2-content" role="region" aria-labelledby="section2-header" hidden>
    <!-- Collapsed content -->
  </div>
</div>
```

### Live Region for Notifications

```html
<!-- Status messages (polite) -->
<div aria-live="polite" aria-atomic="true" class="sr-only" id="status-region">
  <!-- Dynamically updated: "3 items added to cart" -->
</div>

<!-- Error alerts (assertive) -->
<div role="alert" aria-live="assertive" id="error-region">
  <!-- Dynamically updated: "Session expired. Please log in again." -->
</div>
```

---

## Alternatives

| Library | When to consider |
|---------|-----------------|
| React Aria (Adobe) | Headless hooks for accessible React components with full ARIA support |
| Radix UI | Unstyled, accessible React primitives with built-in ARIA patterns |
| Headless UI (Tailwind) | Accessible UI components for React and Vue |
| Ariakit | Low-level accessible component primitives for React |
| Lion (ING) | Web component library with built-in ARIA patterns |

---

## Checklist

- [ ] Native HTML elements used before ARIA roles (first rule of ARIA followed)
- [ ] Every ARIA role includes its required states and properties
- [ ] `aria-expanded`, `aria-selected`, `aria-checked` states dynamically updated via JS
- [ ] `aria-live` regions used for dynamic content (polite by default, assertive for errors)
- [ ] Modal dialogs implement focus trap, Escape to close, and focus restoration
- [ ] Tab components use roving tabindex with Arrow key navigation
- [ ] `aria-hidden="true"` never applied to focusable or interactive elements
- [ ] Landmark roles (`main`, `nav`, `aside`, `header`, `footer`) define page structure
- [ ] ARIA implementations tested with at least one screen reader
- [ ] Component patterns follow WAI-ARIA Authoring Practices Guide specifications

---

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

---

# Keyboard Navigation

Standards for ensuring all interactive functionality is operable via keyboard alone. Full
keyboard accessibility is a WCAG 2.2 Level A requirement (2.1.1) and a prerequisite for
screen reader usability.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Focus indicator** | Browser default + custom `:focus-visible` styles | CSS outline, box-shadow, border, background-color change |
| **Focus management** | DOM order matches visual order | `tabindex` management, roving tabindex for composite widgets |
| **Skip links** | Skip-to-main-content link as first focusable element | Skip-to-navigation, skip-to-search, multiple skip links |
| **Testing** | Manual keyboard walkthrough per page | Accessibility Insights Tab Stops, No Coffee browser extension |

---

## Do / Don't

- **Do** ensure every interactive element is reachable via Tab key and activatable via
  Enter or Space.
- **Do** provide visible focus indicators that meet WCAG 2.4.7 (Focus Visible) — at least
  2px solid outline with 3:1 contrast against adjacent colors.
- **Do** use logical tab order that matches the visual reading order — left-to-right,
  top-to-bottom in LTR layouts.
- **Do** implement skip navigation links to bypass repeated content (header, navigation)
  on every page.
- **Do** manage focus programmatically when content changes — move focus to new content
  after route changes, modal opens, or inline expansion.
- **Do** support Escape to close overlays, menus, and modal dialogs.
- **Don't** use `tabindex` values greater than 0 — they break natural tab order and create
  unpredictable navigation.
- **Don't** remove the default browser focus outline without providing a visible replacement.
- **Don't** create keyboard traps — users must be able to navigate into and out of every
  component using standard keys (Tab, Shift+Tab, Escape).
- **Don't** rely solely on mouse events (`onClick`, `onHover`) — provide keyboard equivalents
  (`onKeyDown`, `onFocus`, `onBlur`).
- **Don't** attach keyboard shortcuts that conflict with screen reader or browser shortcuts
  (Ctrl+key, Alt+key combinations are often reserved).

---

## Common Pitfalls

1. **Invisible focus indicators.** `outline: none` in CSS resets removes the default focus
   ring without providing a replacement. Users cannot tell where they are on the page. Always
   use `:focus-visible` to show focus indicators for keyboard users while hiding them for
   mouse users.

2. **Keyboard traps in custom widgets.** Date pickers, rich text editors, and embedded media
   players often trap focus. Test that Tab and Escape allow the user to leave every widget.
   Implement an explicit exit mechanism if the widget captures Tab.

3. **Broken tab order after dynamic content.** Single-page applications that inject content
   via JavaScript often leave focus on a destroyed element or at the top of the page. After
   route changes or AJAX updates, move focus to the new content's heading or container.

4. **Non-interactive elements made focusable.** Adding `tabindex="0"` to `<div>` or `<span>`
   elements without adding keyboard event handlers creates elements that receive focus but do
   nothing. If it is focusable, it must be operable.

5. **Positive tabindex values.** `tabindex="1"` or higher overrides DOM order and creates
   unpredictable focus sequences. Use `tabindex="0"` (natural order) or `tabindex="-1"`
   (programmatic focus only). Never use positive values.

---

## Focus Management Patterns

### Skip Navigation

```html
<!-- First element in <body> -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<header>
  <nav><!-- Site navigation --></nav>
</header>

<main id="main-content" tabindex="-1">
  <!-- Page content -->
</main>
```

```css
.skip-link {
  position: absolute;
  left: -9999px;
  top: auto;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

.skip-link:focus {
  position: fixed;
  top: 10px;
  left: 10px;
  width: auto;
  height: auto;
  padding: 0.75rem 1.5rem;
  background: #000;
  color: #fff;
  font-size: 1rem;
  z-index: 10000;
  outline: 3px solid #4a90d9;
}
```

### Focus Visible Styles

```css
/* Only show focus styles for keyboard navigation */
:focus-visible {
  outline: 3px solid #4a90d9;
  outline-offset: 2px;
}

/* Remove default outline for mouse clicks */
:focus:not(:focus-visible) {
  outline: none;
}

/* High-contrast mode support */
@media (forced-colors: active) {
  :focus-visible {
    outline: 3px solid CanvasText;
  }
}
```

### SPA Route Change Focus Management

```javascript
// React — manage focus after route change
import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";

function PageLayout({ children, title }) {
  const headingRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    // Move focus to the page heading after navigation
    if (headingRef.current) {
      headingRef.current.focus();
    }
    // Announce the new page to screen readers
    document.title = title;
  }, [location.pathname, title]);

  return (
    <main>
      <h1 ref={headingRef} tabIndex={-1}>
        {title}
      </h1>
      {children}
    </main>
  );
}
```

### Roving Tabindex for Composite Widgets

```javascript
// Toolbar with roving tabindex — Arrow keys move between items
function Toolbar({ items }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const itemRefs = useRef([]);

  const handleKeyDown = (event) => {
    let newIndex = activeIndex;
    switch (event.key) {
      case "ArrowRight":
        newIndex = (activeIndex + 1) % items.length;
        break;
      case "ArrowLeft":
        newIndex = (activeIndex - 1 + items.length) % items.length;
        break;
      case "Home":
        newIndex = 0;
        break;
      case "End":
        newIndex = items.length - 1;
        break;
      default:
        return;
    }
    event.preventDefault();
    setActiveIndex(newIndex);
    itemRefs.current[newIndex]?.focus();
  };

  return (
    <div role="toolbar" aria-label="Formatting" onKeyDown={handleKeyDown}>
      {items.map((item, index) => (
        <button
          key={item.id}
          ref={(el) => (itemRefs.current[index] = el)}
          tabIndex={index === activeIndex ? 0 : -1}
          aria-pressed={item.active}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
```

---

## Keyboard Shortcut Reference

| Key | Standard Behavior |
|-----|------------------|
| Tab | Move to next focusable element |
| Shift + Tab | Move to previous focusable element |
| Enter | Activate links, buttons, submit forms |
| Space | Activate buttons, toggle checkboxes, select options |
| Escape | Close modals, menus, dropdowns, tooltips |
| Arrow keys | Navigate within composite widgets (tabs, menus, toolbars, grids) |
| Home / End | Jump to first/last item in lists, menus, sliders |

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| Accessibility Insights (Microsoft) | Tab Stops visualization for keyboard navigation testing |
| No Coffee (Chrome extension) | Simulates vision impairments to test focus visibility |
| Focusable (npm) | Programmatic detection of focusable elements in the DOM |
| focus-trap (npm) | Focus trapping for modals and overlays |
| tabbable (npm) | Query tabbable elements in DOM order |

---

## Checklist

- [ ] All interactive elements reachable via Tab key
- [ ] Visible focus indicators present on all focusable elements (`:focus-visible`)
- [ ] Focus indicators have minimum 3:1 contrast against adjacent colors
- [ ] Tab order matches visual reading order (no positive `tabindex` values)
- [ ] Skip navigation link present as the first focusable element on every page
- [ ] Focus managed programmatically after route changes and dynamic content updates
- [ ] Escape key closes all overlays, modals, menus, and dropdowns
- [ ] No keyboard traps — users can Tab and Shift+Tab in and out of all components
- [ ] Composite widgets (tabs, toolbars, menus) use roving tabindex with Arrow keys
- [ ] Custom keyboard shortcuts do not conflict with browser or screen reader shortcuts

---

# Screen Reader Testing

Standards for testing web applications with screen readers to validate that content is
perceivable, operable, and understandable for users who rely on assistive technology. Manual
screen reader testing is required — automated tools cannot verify the quality of the screen
reader experience.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Primary screen reader** | NVDA + Firefox (Windows) | JAWS + Chrome, VoiceOver + Safari (macOS/iOS), TalkBack + Chrome (Android) |
| **Testing matrix** | NVDA/Firefox + VoiceOver/Safari | Full matrix per WebAIM Screen Reader Survey |
| **Testing frequency** | Every sprint for changed UI components | Pre-release only (not recommended), continuous |
| **Test documentation** | Screen reader test script per feature | Recorded test sessions, annotated screenshots |

---

## Screen Reader Market Share

| Screen Reader | Platform | Market Share | Best Browser Pairing |
|---------------|----------|-------------|---------------------|
| JAWS | Windows | ~40% | Chrome, Edge |
| NVDA | Windows | ~30% | Firefox, Chrome |
| VoiceOver | macOS/iOS | ~20% | Safari |
| TalkBack | Android | ~5% | Chrome |
| Narrator | Windows | ~3% | Edge |

Test with at least two screen readers from different platforms to catch implementation
differences.

---

## Do / Don't

- **Do** test with the screen reader's recommended browser pairing — NVDA with Firefox,
  VoiceOver with Safari, JAWS with Chrome.
- **Do** create screen reader test scripts that specify the expected announcement for each
  interactive element and landmark.
- **Do** test the full user journey, not just individual components — navigation, form
  submission, error recovery, success confirmation.
- **Do** verify that dynamic content changes are announced via `aria-live` regions.
- **Do** test with screen reader in both browse mode (reading) and focus/forms mode
  (interacting) — behavior differs significantly.
- **Don't** assume that passing automated tests means the screen reader experience is good —
  automated tools test code, not user experience.
- **Don't** test only with VoiceOver on macOS — it is the most forgiving screen reader and
  may mask issues that NVDA and JAWS expose.
- **Don't** add excessive `aria-label` attributes that duplicate visible text — screen reader
  users hear everything twice.
- **Don't** use `title` attributes as the primary accessible name — most screen readers do
  not reliably announce them.

---

## Common Pitfalls

1. **Testing only in browse mode.** Screen readers have distinct modes: browse mode for
   reading content and forms/focus mode for interacting with widgets. Custom widgets may work
   in one mode but not the other. Test both modes explicitly.

2. **Verbose or confusing announcements.** A button announced as "Close button close dialog
   button" indicates redundant ARIA labeling. Listen to the actual output and simplify.
   Remove `aria-label` when the visible text is sufficient.

3. **Missing announcements for dynamic updates.** AJAX-loaded content, toast notifications,
   and form validation errors may appear visually but go unannounced. Verify that `aria-live`
   regions or `role="alert"` trigger announcements.

4. **Testing with a single screen reader.** NVDA, JAWS, and VoiceOver interpret ARIA
   differently. A combobox that works in VoiceOver may be unusable in JAWS. Test with at
   least two screen readers before release.

5. **Images of text without alt text.** Logos, headings rendered as images, and infographics
   must have meaningful `alt` text. An empty `alt=""` is correct only for purely decorative
   images that add no information.

---

## Screen Reader Test Script Template

```markdown
## Feature: User Login Form

### Setup
1. Navigate to /login
2. Enable screen reader (NVDA: Ctrl+Alt+N, VoiceOver: Cmd+F5)

### Test Steps

| # | Action | Expected Announcement |
|---|--------|-----------------------|
| 1 | Tab to email field | "Email, edit text, required" |
| 2 | Type email address | Characters echoed as typed |
| 3 | Tab to password field | "Password, password edit text, required" |
| 4 | Tab to "Remember me" checkbox | "Remember me, checkbox, not checked" |
| 5 | Press Space to check | "checked" |
| 6 | Tab to "Sign in" button | "Sign in, button" |
| 7 | Press Enter to submit | (loading state announced, then result) |
| 8 | Invalid credentials submitted | "Error: Invalid email or password, alert" |
| 9 | Tab to error message | "Error: Invalid email or password" |

### Landmarks
- Page has banner, navigation, main, and contentinfo landmarks
- "Skip to main content" link is first focusable element
- Form is within main landmark

### Headings
- H1: "Sign in to your account"
- Heading hierarchy is sequential (no skipped levels)
```

---

## NVDA Quick Reference

```
# Starting / Stopping
Ctrl + Alt + N          Start NVDA
Insert + Q              Quit NVDA

# Navigation
Insert + F7             Elements list (links, headings, landmarks)
H / Shift + H           Next / previous heading
D / Shift + D           Next / previous landmark
K / Shift + K           Next / previous link
F / Shift + F           Next / previous form field
T / Shift + T           Next / previous table

# Reading
Insert + Down Arrow     Read from current position
Ctrl                    Stop reading
Insert + Up Arrow       Read current line
Insert + F              Read current field info

# Modes
Insert + Space          Toggle browse / focus mode
```

---

## VoiceOver Quick Reference

```
# Starting / Stopping
Cmd + F5                Toggle VoiceOver on/off
VO = Ctrl + Option      VoiceOver modifier key

# Navigation
VO + U                  Open rotor (navigate by headings, links, landmarks)
VO + Right/Left         Move to next/previous element
VO + Shift + Down       Enter a group (table, list, landmark)
VO + Shift + Up         Exit a group

# Reading
VO + A                  Read from current position
Ctrl                    Stop reading
VO + B                  Read from top

# Interaction
VO + Space              Activate (click) current element
VO + Shift + M          Open shortcut menu
```

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| JAWS (Freedom Scientific) | Enterprise standard, deepest Office/PDF support, commercial license |
| NVDA (NV Access) | Free, open-source, strong web support, best for developer testing |
| VoiceOver (Apple) | Built into macOS/iOS, required for Safari/iOS testing |
| TalkBack (Google) | Built into Android, required for Android app testing |
| Narrator (Microsoft) | Built into Windows, paired with Edge |
| ChromeVox | Chrome extension, useful for quick Chromebook testing |

---

## Checklist

- [ ] Screen reader testing performed with at least two screen readers (NVDA + VoiceOver recommended)
- [ ] Test scripts document expected announcements for all interactive elements
- [ ] Full user journeys tested, not just individual components
- [ ] Dynamic content updates verified as announced (aria-live, role="alert")
- [ ] Browse mode and focus/forms mode tested separately
- [ ] Heading hierarchy is logical and sequential (no skipped levels)
- [ ] All landmarks announced and navigable (banner, nav, main, contentinfo)
- [ ] Images have meaningful alt text (or empty alt for decorative images)
- [ ] Form fields have associated labels announced correctly
- [ ] Error messages announced immediately upon display

---

# WCAG 2.2 Conformance

Standards for achieving Web Content Accessibility Guidelines 2.2 conformance at Level A, AA,
and AAA. Level AA is the default target for all web applications; deviations require an ADR.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Conformance target** | WCAG 2.2 Level AA | Level A (minimum legal), Level AAA (aspirational) |
| **Testing tool** | axe-core (Deque) | Pa11y, WAVE, Lighthouse Accessibility, ARC Toolkit |
| **CI integration** | axe-core + jest-axe in unit tests | Pa11y CI, Lighthouse CI, cypress-axe |
| **Manual testing** | Screen reader + keyboard walkthrough | Assistive technology matrix, user testing with disabled users |
| **Audit standard** | VPAT (Voluntary Product Accessibility Template) | ACR (Accessibility Conformance Report), Section 508 checklist |

---

## WCAG 2.2 Conformance Levels

### Level A — Minimum Accessibility

Essential requirements that must be met. Failure means some users cannot access content at all.

| Criterion | Summary |
|-----------|---------|
| 1.1.1 Non-text Content | All images, icons, and media have text alternatives |
| 1.3.1 Info and Relationships | Structure conveyed visually is also available programmatically |
| 2.1.1 Keyboard | All functionality available via keyboard |
| 2.4.1 Bypass Blocks | Skip-navigation links to bypass repeated content |
| 4.1.2 Name, Role, Value | All UI components have accessible names and roles |

### Level AA — Standard Target

The accepted standard for legal compliance (ADA, Section 508, EN 301 549).

| Criterion | Summary |
|-----------|---------|
| 1.4.3 Contrast (Minimum) | Text has at least 4.5:1 contrast ratio (3:1 for large text) |
| 1.4.4 Resize Text | Text resizable up to 200% without loss of content |
| 1.4.11 Non-text Contrast | UI components and graphical objects have 3:1 contrast |
| 2.4.7 Focus Visible | Keyboard focus indicator is visible |
| 3.3.8 Accessible Authentication | No cognitive function test required for login |
| 3.2.6 Consistent Help | Help mechanisms appear in consistent locations |

### Level AAA — Enhanced Accessibility

Aspirational goals. Not required for conformance but beneficial for specific audiences.

| Criterion | Summary |
|-----------|---------|
| 1.4.6 Contrast (Enhanced) | 7:1 contrast ratio for text (4.5:1 for large text) |
| 2.4.9 Link Purpose (Link Only) | Link purpose determinable from link text alone |
| 3.1.5 Reading Level | Content does not exceed lower-secondary education reading level |

---

## Do / Don't

- **Do** set WCAG 2.2 Level AA as the minimum conformance target for all user-facing
  applications and document this in project requirements.
- **Do** test with automated tools first (axe-core catches ~30-40% of issues), then
  follow up with manual keyboard and screen reader testing.
- **Do** include accessibility acceptance criteria in every user story that touches UI.
- **Do** publish a VPAT/ACR for enterprise products — procurement teams require it.
- **Do** test conformance at each WCAG principle: Perceivable, Operable, Understandable,
  Robust (POUR).
- **Don't** rely solely on automated testing — it cannot detect missing alt text quality,
  logical reading order, or keyboard trap issues.
- **Don't** treat accessibility as a phase — bake it into design, development, and QA
  from sprint one.
- **Don't** assume Level A is sufficient for legal compliance — most regulations (ADA,
  Section 508, EN 301 549) reference Level AA.
- **Don't** use overlays or widgets that claim to "fix" accessibility automatically — they
  do not achieve conformance and often introduce new barriers.

---

## Common Pitfalls

1. **Testing only with automated tools.** axe-core and Lighthouse detect approximately
   30-40% of WCAG violations. The remaining issues — logical reading order, meaningful alt
   text, keyboard traps, cognitive barriers — require manual testing with assistive
   technologies.

2. **Ignoring new WCAG 2.2 criteria.** Teams familiar with WCAG 2.1 miss nine new success
   criteria in 2.2, including 3.3.8 Accessible Authentication, 3.2.6 Consistent Help, and
   2.4.11 Focus Not Obscured. Audit against the full 2.2 specification.

3. **Conformance claims without documentation.** Stating "WCAG AA compliant" without a VPAT
   or ACR is unverifiable. Produce a formal conformance report, specify the evaluation date,
   list known exceptions, and plan remediation timelines.

4. **Treating conformance as binary.** Partial conformance is common and acceptable when
   documented. Use a conformance statement that lists which criteria are met, partially met,
   or not met, with remediation plans for gaps.

5. **Forgetting third-party content.** Embedded widgets (maps, chat, video players,
   analytics consent banners) must also conform. Require accessibility conformance in vendor
   contracts and test integrations independently.

---

## Automated Conformance Testing

```javascript
// jest-axe — unit test for WCAG 2.2 AA conformance
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

test("login form has no accessibility violations", async () => {
  const { container } = render(<LoginForm />);
  const results = await axe(container, {
    runOnly: {
      type: "tag",
      values: ["wcag2a", "wcag2aa", "wcag22aa"],
    },
  });
  expect(results).toHaveNoViolations();
});
```

```javascript
// Cypress + cypress-axe — integration test
describe("Dashboard accessibility", () => {
  beforeEach(() => {
    cy.visit("/dashboard");
    cy.injectAxe();
  });

  it("meets WCAG 2.2 AA standards", () => {
    cy.checkA11y(null, {
      runOnly: {
        type: "tag",
        values: ["wcag2a", "wcag2aa", "wcag22aa"],
      },
    });
  });
});
```

```yaml
# Pa11y CI configuration — .pa11yci.json
{
  "defaults": {
    "standard": "WCAG2AA",
    "timeout": 30000,
    "wait": 1000,
    "chromeLaunchConfig": {
      "args": ["--no-sandbox"]
    }
  },
  "urls": [
    "http://localhost:3000/",
    "http://localhost:3000/login",
    "http://localhost:3000/dashboard",
    "http://localhost:3000/settings"
  ]
}
```

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| Pa11y | CLI-based testing with HTML CodeSniffer, good for CI pipelines |
| WAVE (WebAIM) | Browser extension for visual overlay of accessibility issues |
| Lighthouse | Built into Chrome DevTools, good for quick audits |
| ARC Toolkit (TPGi) | Comprehensive browser extension with WCAG 2.2 support |
| Tenon.io | API-based testing for integration into custom workflows |
| Accessibility Insights (Microsoft) | Free tool with guided manual testing workflows |

---

## Checklist

- [ ] WCAG 2.2 Level AA set as the conformance target in project requirements
- [ ] Automated accessibility tests integrated into CI pipeline (axe-core or Pa11y)
- [ ] Manual testing performed with at least one screen reader (NVDA, VoiceOver, or JAWS)
- [ ] Keyboard-only navigation tested for all interactive flows
- [ ] VPAT/ACR produced and published for enterprise-facing products
- [ ] New WCAG 2.2 criteria explicitly tested (3.3.8, 3.2.6, 2.4.11, 2.4.12, 2.4.13)
- [ ] Third-party components audited for accessibility conformance
- [ ] Conformance statement documents met, partially met, and unmet criteria
- [ ] Remediation plan created for any unmet criteria with target dates
- [ ] Accessibility regression tests added for previously fixed issues
