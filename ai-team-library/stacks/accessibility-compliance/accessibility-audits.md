# Accessibility Audits and Remediation

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
