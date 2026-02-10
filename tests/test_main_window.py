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
# Construction
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_window_title(self, window):
        assert window.windowTitle() == "Foundry"

    def test_minimum_size(self, window):
        assert window.minimumWidth() >= 900
        assert window.minimumHeight() >= 600

    def test_no_menu_bar(self, window):
        menu_bar = window.menuBar()
        # QMainWindow always returns a QMenuBar, but it should be empty
        assert menu_bar.actions() == []

    def test_has_central_widget(self, window):
        assert window.centralWidget() is not None


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
        assert window.stack.count() == len(SCREENS)

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
        assert window.stack.count() == len(SCREENS)


# ---------------------------------------------------------------------------
# Geometry persistence
# ---------------------------------------------------------------------------

class TestLibraryAutoDetect:
    def test_detect_library_root_finds_sibling_dir(self):
        """Detection resolves ai-team-library/ relative to the package."""
        result = MainWindow._detect_library_root()
        # In the foundry repo, ai-team-library/ exists as a sibling of foundry_app/
        from pathlib import Path

        expected = Path(__file__).resolve().parent.parent / "ai-team-library"
        if expected.is_dir() and (expected / "personas").is_dir():
            assert result == str(expected)
        else:
            # Running from a different location — detection returns empty
            assert result == ""

    def test_auto_detect_persists_to_settings(self, settings):
        """When library_root is empty, auto-detection persists the result."""
        assert settings.library_root == ""
        w = MainWindow(settings=settings)
        # If auto-detection found the library, it should now be in settings
        from pathlib import Path

        expected = Path(__file__).resolve().parent.parent / "ai-team-library"
        if expected.is_dir() and (expected / "personas").is_dir():
            assert settings.library_root == str(expected)
        w.close()

    def test_existing_setting_skips_detection(self, settings):
        """If library_root is already set, auto-detection is skipped."""
        settings.library_root = "/custom/path"
        w = MainWindow(settings=settings)
        assert settings.library_root == "/custom/path"
        w.close()


class TestGeometry:
    def test_close_saves_geometry(self, window, settings):
        window.close()
        geo = settings.window_geometry
        # After close, geometry should have been written (non-empty)
        assert not geo.isEmpty()
