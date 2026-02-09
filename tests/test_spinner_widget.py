"""Tests for foundry_app.ui.widgets.spinner_widget — spinning gear indicator."""

import pytest

try:
    from PySide6.QtWidgets import QApplication

    _app = QApplication.instance() or QApplication([])
    HAS_DISPLAY = True
except ImportError:
    HAS_DISPLAY = False
except Exception:
    HAS_DISPLAY = False

pytestmark = pytest.mark.skipif(not HAS_DISPLAY, reason="PySide6/display unavailable")


@pytest.fixture
def spinner():
    from foundry_app.ui.widgets.spinner_widget import SpinnerWidget

    return SpinnerWidget(size=48)


class TestSpinnerWidget:
    """Tests for SpinnerWidget construction and API."""

    def test_default_size(self, spinner):
        assert spinner.width() == 48
        assert spinner.height() == 48

    def test_custom_size(self):
        from foundry_app.ui.widgets.spinner_widget import SpinnerWidget

        w = SpinnerWidget(size=64)
        assert w.width() == 64
        assert w.height() == 64

    def test_not_spinning_initially(self, spinner):
        assert spinner.is_spinning is False

    def test_start_makes_spinning(self, spinner):
        spinner.start()
        assert spinner.is_spinning is True
        spinner.stop()

    def test_stop_halts_spinning(self, spinner):
        spinner.start()
        spinner.stop()
        assert spinner.is_spinning is False

    def test_start_idempotent(self, spinner):
        spinner.start()
        spinner.start()  # should not error
        assert spinner.is_spinning is True
        spinner.stop()

    def test_stop_idempotent(self, spinner):
        spinner.stop()  # should not error when not spinning
        assert spinner.is_spinning is False

    def test_rotation_angle_property(self, spinner):
        spinner._set_rotation_angle(45.0)
        assert spinner._get_rotation_angle() == 45.0
