# PySide6 Accessibility

Making PySide6 desktop applications accessible to users with disabilities,
including screen reader support, keyboard navigation, and high-contrast theming.

---

## Defaults

- **Standard:** WCAG 2.1 AA as the baseline target for desktop applications.
- **Screen readers:** NVDA (Windows), VoiceOver (macOS), Orca (Linux).
- **Framework API:** `QAccessible`, `QAccessibleInterface`, accessible properties on widgets.
- **Keyboard navigation:** All interactive elements reachable via Tab; all actions triggerable via keyboard.
- **Color contrast:** Minimum 4.5:1 ratio for normal text, 3:1 for large text.

---

## Setting Accessible Properties

Every interactive widget must have an accessible name and, where appropriate, a description.

```python
from PySide6.QtWidgets import QPushButton, QLineEdit, QLabel


# Buttons: accessible name defaults to button text, but set it explicitly
# when the button uses only an icon.
save_button = QPushButton()
save_button.setIcon(QIcon(":/icons/save.svg"))
save_button.setAccessibleName("Save project")
save_button.setAccessibleDescription("Save the current project to disk")
save_button.setToolTip("Save project")  # Tooltip should match for consistency

# Line edits: associate with a label using setBuddy()
email_label = QLabel("&Email:")       # & creates Alt+E mnemonic
email_input = QLineEdit()
email_label.setBuddy(email_input)
email_input.setAccessibleName("Email address")
email_input.setPlaceholderText("user@example.com")

# Tables and trees: set accessible name on the view
tree_view.setAccessibleName("Project files")
```

---

## Keyboard Navigation

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QShortcut
from PySide6.QtGui import QKeySequence


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._setup_shortcuts()
        self._setup_tab_order()

    def _setup_shortcuts(self) -> None:
        """Register global keyboard shortcuts."""
        QShortcut(QKeySequence.Save, self, self._on_save)
        QShortcut(QKeySequence("Ctrl+Shift+P"), self, self._open_command_palette)
        QShortcut(QKeySequence(Qt.Key_F1), self, self._show_help)

    def _setup_tab_order(self) -> None:
        """Define explicit tab order for form elements."""
        QWidget.setTabOrder(self.name_input, self.email_input)
        QWidget.setTabOrder(self.email_input, self.role_combo)
        QWidget.setTabOrder(self.role_combo, self.submit_button)
        QWidget.setTabOrder(self.submit_button, self.cancel_button)
```

---

## Do / Don't

- **Do** set `accessibleName` on every icon-only button, toolbar action, and custom widget.
- **Do** use `QLabel.setBuddy()` to associate labels with their input widgets.
- **Do** use mnemonics (`&File`, `&Save`) in menu items and labels.
- **Do** define explicit tab order with `setTabOrder()` for forms.
- **Do** provide keyboard shortcuts for all primary actions.
- **Do** test with a real screen reader (NVDA on Windows, Orca on Linux) at least once per release.
- **Do** respect the system high-contrast theme -- use palette-aware colors in QSS.
- **Don't** use color alone to convey information (e.g., red/green status). Add icons or text.
- **Don't** disable focus indicators. If you style `:focus`, keep a visible ring.
- **Don't** use `setFocusPolicy(Qt.NoFocus)` on interactive widgets.
- **Don't** create custom widgets without implementing `QAccessibleInterface` if they have interactive behavior.

---

## High-Contrast and Theming

```css
/* main.qss - Use palette references for theme-aware colors */
QWidget {
    background-color: palette(window);
    color: palette(window-text);
}

QPushButton {
    background-color: palette(button);
    color: palette(button-text);
    border: 1px solid palette(mid);
    padding: 6px 16px;
    min-height: 24px;        /* Minimum touch/click target */
}

QPushButton:focus {
    border: 2px solid palette(highlight);
    outline: none;           /* Replace default with visible custom focus ring */
}

QLineEdit:focus {
    border: 2px solid palette(highlight);
}

/* Ensure minimum target size for clickable elements */
QToolButton {
    min-width: 32px;
    min-height: 32px;
}
```

---

## Common Pitfalls

1. **Icon-only buttons without accessible names.** Screen readers announce nothing. Always call `setAccessibleName()` on buttons that have no text.
2. **Custom-painted widgets.** If you override `paintEvent()`, Qt cannot infer accessible properties. Implement `QAccessibleInterface` or set accessible roles and names manually.
3. **Dynamic content without announcements.** When status text changes, screen readers may not notice. Use `QAccessible.updateAccessibility()` to push notifications.
4. **Hardcoded colors in QSS.** `color: #333333` ignores the user's high-contrast settings. Prefer `palette()` references.
5. **Focus traps.** Modal dialogs and popups must return focus to the triggering widget when dismissed.
6. **Forgetting Tab order.** Qt's default tab order follows widget creation order, which is often wrong. Define it explicitly for every form.

### Alternatives

| Tool / Library       | Purpose                                       |
|----------------------|-----------------------------------------------|
| `QAccessible` API    | Built-in: programmatic accessibility interface |
| Accessibility Insights (Windows) | Inspect accessible tree, find issues |
| `accerciser` (Linux) | GTK accessibility inspector (works partially with Qt via AT-SPI) |
| Colour Contrast Analyser | Verify color contrast ratios              |

---

## Checklist

- [ ] Every icon-only button has `setAccessibleName()`
- [ ] All form labels use `setBuddy()` to associate with inputs
- [ ] Mnemonics (`&Label`) defined for menu items and form labels
- [ ] Explicit `setTabOrder()` defined for all forms
- [ ] Keyboard shortcuts registered for all primary actions
- [ ] Focus indicators visible on all interactive widgets
- [ ] Color is never the sole indicator of state (icons or text supplement)
- [ ] QSS uses `palette()` references, not hardcoded colors
- [ ] Minimum click target size is 32x32 pixels
- [ ] Tested with at least one screen reader before release
- [ ] Custom widgets implement `QAccessibleInterface` or set accessible roles
- [ ] Dynamic status changes trigger `QAccessible.updateAccessibility()`
