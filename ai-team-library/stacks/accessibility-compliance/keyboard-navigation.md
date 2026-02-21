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
