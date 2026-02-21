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
