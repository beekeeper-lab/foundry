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
