# PySide6 Testing

Testing strategy for Qt desktop applications: unit testing services, widget testing
with pytest-qt, and integration testing with simulated user interaction.

---

## Defaults

- **Framework:** pytest + pytest-qt.
- **Coverage target:** 80% on services and models. Widget tests cover critical user flows.
- **Strategy:** Test services and models without Qt where possible. Use `qtbot` for widget interaction tests.
- **CI requirement:** Tests run headless via `xvfb` (Linux) or virtual framebuffer.

---

## QApplication Fixture

Every test session needs exactly one `QApplication`. pytest-qt handles this automatically
via the `qapp` fixture. You rarely need to manage it yourself.

```python
# conftest.py
import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Provide a QApplication for the entire test session.

    pytest-qt provides this automatically, but define it explicitly
    if you need custom arguments (e.g., platform plugins).
    """
    app = QApplication.instance() or QApplication(["-platform", "offscreen"])
    yield app
```

---

## Testing Signals with qtbot

```python
from PySide6.QtCore import Signal, QObject


class DataLoader(QObject):
    data_ready = Signal(list)
    error_occurred = Signal(str)

    def load(self, path: str) -> None:
        try:
            data = self._read(path)
            self.data_ready.emit(data)
        except FileNotFoundError:
            self.error_occurred.emit(f"Not found: {path}")


def test_data_loader_emits_on_success(qtbot, tmp_path):
    """Verify data_ready signal fires with correct payload."""
    test_file = tmp_path / "data.json"
    test_file.write_text('[{"id": 1}]')

    loader = DataLoader()

    with qtbot.waitSignal(loader.data_ready, timeout=1000) as blocker:
        loader.load(str(test_file))

    assert len(blocker.args[0]) == 1
    assert blocker.args[0][0]["id"] == 1


def test_data_loader_emits_error_on_missing_file(qtbot):
    """Verify error_occurred signal fires for missing files."""
    loader = DataLoader()

    with qtbot.waitSignal(loader.error_occurred, timeout=1000) as blocker:
        loader.load("/nonexistent/path.json")

    assert "Not found" in blocker.args[0]
```

---

## Testing Widgets

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QLineEdit

from myapp.views.login_form import LoginForm


def test_login_button_disabled_when_fields_empty(qtbot):
    """Login button should be disabled until both fields have text."""
    form = LoginForm()
    qtbot.addWidget(form)

    submit_btn = form.findChild(QPushButton, "submit_button")
    assert not submit_btn.isEnabled()

    username_input = form.findChild(QLineEdit, "username_input")
    password_input = form.findChild(QLineEdit, "password_input")

    qtbot.keyClicks(username_input, "admin")
    qtbot.keyClicks(password_input, "secret")

    assert submit_btn.isEnabled()


def test_login_emits_credentials_on_submit(qtbot):
    """Clicking submit emits the login_requested signal with credentials."""
    form = LoginForm()
    qtbot.addWidget(form)

    username_input = form.findChild(QLineEdit, "username_input")
    password_input = form.findChild(QLineEdit, "password_input")
    submit_btn = form.findChild(QPushButton, "submit_button")

    qtbot.keyClicks(username_input, "admin")
    qtbot.keyClicks(password_input, "secret")

    with qtbot.waitSignal(form.login_requested, timeout=1000) as blocker:
        qtbot.mouseClick(submit_btn, Qt.LeftButton)

    assert blocker.args == ["admin", "secret"]
```

---

## Do / Don't

- **Do** test services and models as plain Python (no `qtbot` needed).
- **Do** use `qtbot.addWidget()` for every widget created in tests -- it ensures cleanup.
- **Do** use `qtbot.waitSignal()` instead of `time.sleep()` or manual event processing.
- **Do** name widgets with `setObjectName()` so tests can find them with `findChild()`.
- **Do** run CI tests with `-platform offscreen` or `xvfb-run`.
- **Don't** test Qt's own behavior (e.g., "does QPushButton emit clicked?").
- **Don't** use `QTest.qWait()` for synchronization. Use signal-based waiting.
- **Don't** create `QApplication` in individual test files. Use the session fixture.
- **Don't** skip widget tests entirely. Critical user flows need coverage.

---

## Common Pitfalls

1. **Multiple QApplication instances.** Creating `QApplication()` more than once crashes. Always use the session-scoped fixture or `QApplication.instance()` guard.
2. **Widget not shown.** Some behaviors (layout, paint) only work after `widget.show()`. Use `qtbot.addWidget(w)` which handles lifecycle.
3. **Signal race conditions.** Use `qtbot.waitSignal()` with a timeout. Never assume a signal fires synchronously.
4. **Skipping headless setup in CI.** PySide6 needs a display server. Add `xvfb-run pytest` to your CI script or use the offscreen platform plugin.
5. **Testing private implementation.** Test observable behavior (signals emitted, text displayed), not internal widget state.

### Alternatives

| Tool           | Use Case                                          |
|----------------|---------------------------------------------------|
| `pytest-qt`    | Primary: signal testing, widget interaction        |
| `unittest.mock`| Mocking services injected into controllers         |
| `hypothesis`   | Property-based testing for model data transforms   |
| `pytest-xvfb`  | Auto-manages Xvfb for Linux CI                     |

---

## Checklist

- [ ] `conftest.py` provides session-scoped `QApplication` fixture
- [ ] All widget tests use `qtbot.addWidget()` for cleanup
- [ ] Signal assertions use `qtbot.waitSignal()`, not sleep
- [ ] Service layer tests run without `QApplication`
- [ ] CI runs tests headless (`-platform offscreen` or `xvfb-run`)
- [ ] Critical user flows (login, save, export) have widget-level tests
- [ ] Widgets under test have `objectName` set for `findChild()` lookup
- [ ] No `QApplication()` constructor calls outside the session fixture
- [ ] Slow integration tests marked with `@pytest.mark.slow`
- [ ] Coverage measured on services (80%+) and reported on widgets
