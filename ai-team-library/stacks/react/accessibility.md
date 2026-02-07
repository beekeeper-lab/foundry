# React Accessibility

Accessibility (a11y) is a requirement, not a feature. All React components must
meet WCAG 2.1 Level AA compliance. Violations are treated as bugs with the same
priority as functional defects.

---

## Defaults

- **Standard:** WCAG 2.1 Level AA.
- **Automated scanning:** `axe-core` via `@axe-core/react` in development and `vitest-axe` in tests.
- **CI gate:** `axe` violations fail the build. No exceptions without a documented remediation plan.
- **Linting:** `eslint-plugin-jsx-a11y` enabled with recommended rules.
- **Screen reader testing:** Manual testing with NVDA (Windows) or VoiceOver (macOS) for critical flows.

### Alternatives

| Default                | Alternative         | When to consider                       |
|------------------------|---------------------|----------------------------------------|
| `axe-core`             | Pa11y               | Need page-level scanning in CI pipeline|
| `eslint-plugin-jsx-a11y` | Biome a11y rules | Already using Biome as linter          |
| NVDA                   | JAWS                | Enterprise environment requires JAWS   |

---

## Semantic HTML First

Use the correct HTML element before reaching for ARIA. Semantic elements carry
implicit roles, keyboard behavior, and screen reader announcements for free.

```tsx
// Good: semantic button with built-in keyboard support and role
export function DeleteButton({ onDelete }: { onDelete: () => void }) {
  return (
    <button type="button" onClick={onDelete}>
      Delete item
    </button>
  );
}

// Bad: div pretending to be a button -- no keyboard support, no role
export function DeleteButton({ onDelete }: { onDelete: () => void }) {
  return (
    <div className="btn" onClick={onDelete}>
      Delete item
    </div>
  );
}
```

**Key semantic elements to use:**

- `<button>` for actions, `<a>` for navigation.
- `<nav>`, `<main>`, `<aside>`, `<header>`, `<footer>` for landmarks.
- `<ul>`/`<ol>` for lists, `<table>` for tabular data.
- `<dialog>` for modals (with the `open` attribute or `.showModal()`).
- `<fieldset>` + `<legend>` for grouping related form controls.

---

## Forms and Labels

Every form input must have a programmatically associated label.

```tsx
// Good: explicit label association
<label htmlFor="email">Email address</label>
<input id="email" type="email" name="email" aria-describedby="email-hint" />
<p id="email-hint">We will never share your email.</p>

// Good: wrapping label (no htmlFor needed)
<label>
  Email address
  <input type="email" name="email" />
</label>

// Bad: placeholder-only "label"
<input type="email" placeholder="Email address" />
```

- Use `aria-describedby` to link help text or error messages to the input.
- Use `aria-invalid="true"` on inputs that fail validation.
- Use `aria-required="true"` (or the HTML `required` attribute) for mandatory fields.

---

## Keyboard Navigation

- All interactive elements must be reachable and operable with the keyboard.
- Tab order follows the visual order. Do not use `tabIndex` > 0.
- Custom widgets (dropdowns, date pickers, tabs) must implement the
  [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/) keyboard patterns.
- Focus must be managed when content changes: after opening a modal, focus moves
  into it; after closing, focus returns to the trigger element.

```tsx
// Focus management for a modal
import { useRef, useEffect } from "react";

export function Modal({ isOpen, onClose, children }: ModalProps) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      closeRef.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <dialog open aria-modal="true" role="dialog" aria-label="Confirmation">
      {children}
      <button ref={closeRef} onClick={onClose}>
        Close
      </button>
    </dialog>
  );
}
```

---

## ARIA Usage Rules

1. **No ARIA is better than bad ARIA.** Incorrect `role` or `aria-*` attributes
   are worse than none -- they mislead assistive technology.
2. **Do not override native semantics.** `<button role="link">` is wrong. Use `<a>`.
3. **Use `aria-live` regions for dynamic content.** Status messages, toast
   notifications, and inline validation errors should use `aria-live="polite"`
   (or `"assertive"` for critical alerts).
4. **Provide accessible names.** Icon-only buttons need `aria-label`. Linked
   images need `alt` text that describes the link destination.

---

## Images and Media

- Informative images: `alt` describes the content or function.
- Decorative images: `alt=""` (empty string) so screen readers skip them.
- Complex images (charts, diagrams): provide a text description nearby or via
  `aria-describedby`.
- Videos: provide captions and transcripts.

---

## Color and Contrast

- Normal text: minimum 4.5:1 contrast ratio against the background.
- Large text (18px+ bold or 24px+ regular): minimum 3:1.
- Do not convey information by color alone. Use icons, text labels, or patterns
  as secondary indicators.
- Test with a contrast checker (e.g., WebAIM Contrast Checker, browser DevTools).

---

## Do / Don't

### Do

- Use semantic HTML elements before ARIA.
- Provide visible focus indicators on all interactive elements (never `outline: none` without a replacement).
- Test with a screen reader at least once per sprint for critical flows.
- Use `aria-live` for dynamically injected content (toasts, validation errors).
- Ensure modals trap focus and return it on close.

### Don't

- Don't use `<div>` or `<span>` with `onClick` for interactive elements.
- Don't rely on placeholder text as the only label.
- Don't set `tabIndex` to a positive number.
- Don't auto-play audio or video without user consent.
- Don't use `title` attributes as the sole accessible name -- they are not reliably announced.
- Don't remove the focus outline without providing a visible alternative.

---

## Common Pitfalls

1. **Icon buttons without labels.** A `<button>` containing only an SVG icon
   has no accessible name. Add `aria-label="Close"` or visually-hidden text.
2. **Modals that don't trap focus.** Users tab out of the modal into the
   background content. Use `inert` on the background or implement a focus trap.
3. **Missing live regions.** Form validation errors appear visually but are not
   announced. Wrap the error container with `aria-live="polite"`.
4. **Incorrect heading hierarchy.** Jumping from `<h1>` to `<h4>` confuses
   screen reader navigation. Headings must follow a logical, sequential order.
5. **Using `aria-hidden="true"` on focusable elements.** This creates a
   situation where the element receives focus but is invisible to assistive tech.

---

## Checklist

Before merging any component:

- [ ] All interactive elements are operable via keyboard (Tab, Enter, Space, Escape)
- [ ] Every form input has a programmatically associated `<label>`
- [ ] Images have appropriate `alt` text (descriptive or empty for decorative)
- [ ] Color contrast meets AA ratios (4.5:1 normal, 3:1 large)
- [ ] No information conveyed by color alone
- [ ] Visible focus indicator on all focusable elements
- [ ] Headings follow a sequential hierarchy (no skipped levels)
- [ ] Modals trap focus and return it on close
- [ ] Dynamic content uses `aria-live` regions
- [ ] `axe-core` scan passes with zero violations
- [ ] `eslint-plugin-jsx-a11y` reports no warnings
- [ ] Manual screen reader test completed for new interactive patterns
