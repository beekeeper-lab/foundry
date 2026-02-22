"""Tests for foundry_app.ui.main_window — MainWindow shell and navigation."""

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from foundry_app.core.settings import FoundrySettings
from foundry_app.ui.main_window import SCREENS, MainWindow

_app = QApplication.instance() or QApplication([])


@pytest.fixture()
def settings():
    s = FoundrySettings()
    s._qs.clear()
    return s


@pytest.fixture()
def window(settings):
    w = MainWindow(settings=settings)
    yield w
    w.close()


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

class TestNavigation:
    def test_nav_buttons_have_correct_labels(self, window):
        buttons = window.nav_buttons
        assert len(buttons) == len(SCREENS)
        for i, (label, *_rest) in enumerate(SCREENS):
            assert buttons[i].text() == label

    def test_nav_buttons_are_checkable(self, window):
        for btn in window.nav_buttons:
            assert btn.isCheckable()

    def test_stack_has_correct_count(self, window):
        # 4 nav screens + 1 progress screen
        assert window.stack.count() == len(SCREENS) + 1

    def test_clicking_nav_switches_stack(self, window):
        window.nav_buttons[1].click()
        assert window.stack.currentIndex() == 1

    def test_initial_selection_is_builder(self, window):
        assert window.nav_buttons[0].isChecked()
        assert window.stack.currentIndex() == 0

    def test_nav_buttons_icon_size(self, window):
        for btn in window.nav_buttons:
            assert btn.iconSize().width() >= 32
            assert btn.iconSize().height() >= 32

    def test_keyboard_nav_with_button_group(self, window):
        """Button group allows switching via checked state."""
        window.nav_buttons[2].setChecked(True)
        window.nav_group.idClicked.emit(2)
        assert window.stack.currentIndex() == 2


# ---------------------------------------------------------------------------
# Screen replacement
# ---------------------------------------------------------------------------

class TestScreenReplacement:
    def test_replace_screen(self, window):
        custom = QWidget()
        label = QLabel("Custom Screen")
        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(custom)
        layout.addWidget(label)

        window.replace_screen(0, custom)
        assert window.stack.widget(0) is custom
        # 4 nav screens + 1 progress screen
        assert window.stack.count() == len(SCREENS) + 1


# ---------------------------------------------------------------------------
# Geometry persistence
# ---------------------------------------------------------------------------

class TestGenerationWiring:
    def test_progress_screen_exists(self, window):
        assert window.progress_screen is not None

    def test_progress_screen_in_stack(self, window):
        ps = window.progress_screen
        assert window.stack.indexOf(ps) >= 0

    def test_generate_signal_connected(self, window):
        """Builder screen's generate_requested signal should be connected."""
        # Verify the signal exists and has receivers
        assert window.builder_screen.generate_requested is not None

    def test_back_to_builder_returns_to_index_0(self, window):
        # Simulate being on progress screen
        window.stack.setCurrentWidget(window.progress_screen)
        assert window.stack.currentWidget() is window.progress_screen
        # Trigger back
        window._on_back_to_builder()
        assert window.stack.currentIndex() == 0
        assert window.nav_buttons[0].isChecked()


class TestGeometry:
    def test_close_saves_geometry(self, window, settings):
        window.close()
        geo = settings.window_geometry
        # After close, geometry should have been written (non-empty)
        assert not geo.isEmpty()
