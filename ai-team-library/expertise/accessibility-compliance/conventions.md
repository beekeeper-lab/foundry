---
id: accessibility-compliance
category: Compliance & Governance
applies_to:
  - ux-ui-designer
  - developer
  - tech-qa
  - compliance-risk
  - product-owner
entry: true
last-reviewed: 2026-07
---

# Accessibility Compliance Conventions

## Category
Compliance & Governance

Standards for building and verifying accessible web applications: WCAG 2.2
conformance, ARIA usage, keyboard operability, color contrast, screen reader
testing, and the audit/remediation process. WCAG 2.2 Level AA is the default
target for all user-facing applications; deviations require an ADR.

---

## Defaults

| Concern | Default | Notes |
|---------|---------|-------|
| Conformance target | WCAG 2.2 Level AA | Level A is not sufficient for ADA / Section 508 / EN 301 549 |
| Automated testing | axe-core (+ jest-axe / cypress-axe in CI) | Catches only ~30-40% of issues — manual testing is mandatory |
| Screen readers | NVDA + Firefox and VoiceOver + Safari | Test with at least two, from different platforms |
| Contrast — normal text | 4.5:1 (AA) | 3:1 for large text (≥18pt / ≥14pt bold) |
| Contrast — UI components | 3:1 (WCAG 1.4.11) | Borders, icons, focus indicators, chart segments |
| ARIA policy | Native HTML elements first | ARIA only when no native element provides the semantics |
| Focus indicator | `:focus-visible`, ≥2px solid outline, 3:1 contrast | Never `outline: none` without a replacement |
| Audit methodology | WCAG-EM; quarterly full audit + continuous scanning | Findings rated Critical / Major / Minor / Best Practice |
| Reporting | VPAT 2.5 / ACR with evaluation date and version | Update quarterly; a VPAT is a snapshot, not a certificate |

---

## 1. WCAG 2.2 Conformance

- Set WCAG 2.2 Level AA as the minimum target in project requirements and
  include accessibility acceptance criteria in every user story that touches UI.
- Test against all four POUR principles: Perceivable, Operable, Understandable,
  Robust.
- Explicitly test the criteria new in 2.2 — 3.3.8 Accessible Authentication,
  3.2.6 Consistent Help, 2.4.11 Focus Not Obscured, 2.4.12, 2.4.13 — teams
  auditing against 2.1 miss them.
- Partial conformance is acceptable when documented: the conformance statement
  lists met / partially met / unmet criteria with remediation dates.
- Do not use overlays or widgets that claim to "fix" accessibility
  automatically — they do not achieve conformance and often add barriers.

Full detail: `wcag-conformance.md`

---

## 2. ARIA and Semantic HTML

- **First rule of ARIA:** if a native HTML element (`<button>`, `<nav>`,
  `<input>`, `<select>`, `<dialog>`) provides the semantics and behavior, use
  it. ARIA adds information, not behavior — `<div role="button">` gets no
  keyboard handling for free.
- Every ARIA role must include its required states and properties (e.g.
  `role="combobox"` requires `aria-expanded` and `aria-controls`), and every
  state (`aria-expanded`, `aria-selected`, `aria-checked`) must be dynamically
  updated by JS to match the UI.
- Use `aria-live="polite"` for dynamic updates; reserve `assertive` /
  `role="alert"` for urgent errors. Never apply `aria-hidden="true"` to
  focusable elements.
- Modal dialogs: focus moves in on open, is trapped while open, Escape closes,
  focus returns to the trigger on close. Tabs and toolbars use roving tabindex
  with Arrow-key navigation.
- Follow the WAI-ARIA Authoring Practices Guide for widget patterns.

Full detail: `aria-patterns.md`

---

## 3. Keyboard Navigation

- Every interactive element must be reachable via Tab and operable via Enter
  or Space; Escape closes overlays, menus, and modals. No keyboard traps.
- Tab order matches visual reading order. Use `tabindex="0"` (natural order)
  or `tabindex="-1"` (programmatic focus only) — never positive values.
- Provide a skip-to-main-content link as the first focusable element on every
  page.
- Manage focus programmatically after route changes, modal opens, and dynamic
  content injection — move focus to the new content's heading or container.
- Style focus with `:focus-visible`; never remove the default outline without
  a visible replacement meeting 3:1 contrast.

Full detail: `keyboard-navigation.md`

---

## 4. Color and Contrast

- Normal text 4.5:1; large text 3:1; UI components and graphical objects 3:1
  (WCAG 1.4.11). Placeholder text must meet 4.5:1 — or use visible labels and
  treat placeholders as hints only.
- Never rely on color alone to convey information (WCAG 1.4.1) — add icons,
  patterns, labels, or underlines as secondary indicators (~8% of males are
  color-blind).
- Test dark mode independently — inverting a light theme rarely produces
  compliant contrast — and check every interactive state (default, hover,
  focus, active).
- Generate palettes with contrast built in (e.g. Leonardo, Huetone) rather
  than fixing pairs one at a time; catch issues in design tools (Stark) before
  code.

Full detail: `color-contrast.md`

---

## 5. Screen Reader Testing

- Manual screen reader testing is required — a clean axe-core scan does not
  equal WCAG conformance. Test with the recommended pairings: NVDA + Firefox,
  VoiceOver + Safari, JAWS + Chrome.
- Test both browse mode (reading) and focus/forms mode (interacting) — custom
  widgets may work in one but not the other. Don't test only VoiceOver; it is
  the most forgiving and masks issues NVDA/JAWS expose.
- Write test scripts specifying the expected announcement per interactive
  element, and test full user journeys (navigation, form submission, error
  recovery), not isolated components.
- Verify dynamic updates (toasts, validation errors) are actually announced
  via `aria-live` / `role="alert"`. Avoid redundant `aria-label`s that make
  users hear everything twice; don't rely on `title` attributes.

Full detail: `screen-reader-testing.md`

---

## 6. Audits and Remediation

- Follow WCAG-EM: define scope explicitly (pages, flows, technologies,
  conformance target), automated scan, manual testing, documented findings
  with WCAG criterion + severity + reproduction steps, prioritized
  remediation, retest, VPAT/ACR.
- Severity by user impact, not fix difficulty: Critical (user blocked — fix
  this sprint), Major (workaround exists — 2 sprints), Minor (next quarter),
  Best Practice (backlog).
- Audit representative pages from every template and every critical flow —
  not just the homepage — and include third-party components (widgets,
  iframes, vendor tools).
- Verify every fix with the same methodology that found it, and add regression
  tests so issues don't reappear next release.

Full detail: `accessibility-audits.md`

---

## Do / Don't

**Do:**
- Target WCAG 2.2 Level AA and document it in project requirements.
- Combine automated and manual testing — automation finds ~30-40% of issues.
- Use native HTML elements before reaching for ARIA.
- Give every focusable element a visible `:focus-visible` indicator (3:1+).
- Announce dynamic content via `aria-live` regions and verify with a reader.
- Publish and quarterly-update a VPAT/ACR for enterprise products.

**Don't:**
- Rely on automated scans alone or on accessibility "overlay" widgets.
- Use positive `tabindex` values or remove focus outlines without replacement.
- Apply `aria-hidden="true"` or `role="presentation"` to interactive elements.
- Rely on color alone for meaning, or ship untested dark-mode palettes.
- Defer all fixes to a "future accessibility sprint" — integrate them into
  regular sprint work.
- Close findings without retesting with the original methodology.

---

## Common Pitfalls

1. **Automated-only audits.** axe-core/Lighthouse detect ~30-40% of WCAG
   violations; reading order, alt-text quality, keyboard traps, and cognitive
   barriers need manual assistive-technology testing.
2. **ARIA as a substitute for semantic HTML.** `<div role="button">` receives
   no focus or Enter/Space behavior; orphaned states like a never-updated
   `aria-expanded` announce the wrong thing.
3. **Invisible focus.** `outline: none` in a CSS reset with no replacement
   leaves keyboard users lost; thin gray outlines fail 2.4.11/2.4.13.
4. **Missing WCAG 2.2 deltas.** Teams auditing against 2.1 skip the nine new
   criteria (3.3.8, 3.2.6, 2.4.11, …).
5. **Fix-and-forget.** Remediating without regression tests or component
   library updates lets the same issues return next release.
6. **Scope too narrow.** Homepage-only audits miss dashboards, settings,
   error pages, and third-party embeds.

---

## Checklist

- [ ] WCAG 2.2 Level AA set as conformance target in requirements
- [ ] axe-core (or Pa11y) in CI; failures block the build
- [ ] All interactive elements keyboard-reachable; no traps; Escape closes overlays
- [ ] Visible `:focus-visible` indicators with ≥3:1 contrast; no positive tabindex
- [ ] Skip link is the first focusable element on every page
- [ ] Native HTML first; every ARIA role has required states, dynamically updated
- [ ] Text 4.5:1 / large text 3:1 / UI components 3:1; dark mode tested independently
- [ ] Color never the sole indicator; charts use patterns/labels too
- [ ] Tested with two screen readers (NVDA + VoiceOver), browse and focus modes
- [ ] Dynamic updates announced (aria-live / role="alert")
- [ ] Findings documented with WCAG criterion, severity, reproduction steps
- [ ] Critical issues fixed within current sprint; fixes verified and regression-tested
- [ ] VPAT/ACR published with evaluation date and version; quarterly review scheduled
- [ ] Third-party components included in audit scope
