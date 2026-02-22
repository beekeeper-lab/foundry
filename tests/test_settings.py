"""Tests for foundry_app.core.settings — QSettings-backed preferences."""

import pytest
from PySide6.QtWidgets import QApplication

from foundry_app.core.settings import MAX_RECENT, FoundrySettings

# QApplication is required for QSettings to work
_app = QApplication.instance() or QApplication([])


@pytest.fixture()
def settings(tmp_path):
    """Return a FoundrySettings instance backed by a temp location."""
    s = FoundrySettings()
    # Clear any prior state so tests are isolated
    s._qs.clear()
    return s


# ---------------------------------------------------------------------------
# Setters / getters
# ---------------------------------------------------------------------------

class TestSettersGetters:
    def test_set_library_root(self, settings):
        settings.library_root = "/some/path"
        assert settings.library_root == "/some/path"

    def test_set_workspace_root(self, settings):
        settings.workspace_root = "/workspace"
        assert settings.workspace_root == "/workspace"

    def test_set_library_root_with_path_object(self, settings, tmp_path):
        settings.library_root = tmp_path
        assert settings.library_root == str(tmp_path)


# ---------------------------------------------------------------------------
# Recent libraries
# ---------------------------------------------------------------------------

class TestRecentLibraries:
    def test_add_recent_library(self, settings):
        settings.add_recent_library("/lib/a")
        assert settings.recent_libraries == ["/lib/a"]

    def test_add_duplicate_moves_to_front(self, settings):
        settings.add_recent_library("/lib/a")
        settings.add_recent_library("/lib/b")
        settings.add_recent_library("/lib/a")
        assert settings.recent_libraries == ["/lib/a", "/lib/b"]

    def test_max_recent_enforced(self, settings):
        for i in range(MAX_RECENT + 5):
            settings.add_recent_library(f"/lib/{i}")
        assert len(settings.recent_libraries) == MAX_RECENT
        # Most recent should be first
        assert settings.recent_libraries[0] == f"/lib/{MAX_RECENT + 4}"


# ---------------------------------------------------------------------------
# Generation defaults
# ---------------------------------------------------------------------------

class TestGenerationDefaults:
    def test_overlay_mode_default_is_false(self, settings):
        assert settings.default_overlay_mode is False

    def test_set_overlay_mode(self, settings):
        settings.default_overlay_mode = True
        assert settings.default_overlay_mode is True

    def test_strictness_default_is_standard(self, settings):
        assert settings.default_strictness == "standard"

    def test_set_strictness(self, settings):
        settings.default_strictness = "strict"
        assert settings.default_strictness == "strict"

    def test_strictness_invalid_falls_back(self, settings):
        settings.set_value("generation/strictness", "invalid")
        assert settings.default_strictness == "standard"

    def test_seed_mode_default_is_detailed(self, settings):
        assert settings.default_seed_mode == "detailed"

    def test_set_seed_mode(self, settings):
        settings.default_seed_mode = "kickoff"
        assert settings.default_seed_mode == "kickoff"

    def test_seed_mode_none(self, settings):
        settings.default_seed_mode = "none"
        assert settings.default_seed_mode == "none"


# ---------------------------------------------------------------------------
# Safety defaults
# ---------------------------------------------------------------------------

class TestSafetyDefaults:
    def test_posture_default_is_baseline(self, settings):
        assert settings.default_safety_posture == "baseline"

    def test_set_posture(self, settings):
        settings.default_safety_posture = "hardened"
        assert settings.default_safety_posture == "hardened"

    def test_posture_invalid_falls_back(self, settings):
        settings.set_value("safety/posture", "invalid")
        assert settings.default_safety_posture == "baseline"

    def test_write_safety_config_default_is_true(self, settings):
        assert settings.write_safety_config is True

    def test_set_write_safety_config(self, settings):
        settings.write_safety_config = False
        assert settings.write_safety_config is False


# ---------------------------------------------------------------------------
# Appearance
# ---------------------------------------------------------------------------

class TestAppearance:
    def test_font_size_default_is_medium(self, settings):
        assert settings.font_size_preference == "medium"

    def test_set_font_size(self, settings):
        settings.font_size_preference = "large"
        assert settings.font_size_preference == "large"

    def test_font_size_invalid_falls_back(self, settings):
        settings.set_value("appearance/font_size", "huge")
        assert settings.font_size_preference == "medium"

    def test_theme_default_is_dark(self, settings):
        assert settings.theme_preference == "dark"

    def test_set_theme(self, settings):
        settings.theme_preference = "dark"
        assert settings.theme_preference == "dark"


# ---------------------------------------------------------------------------
# Reset all
# ---------------------------------------------------------------------------

class TestResetAll:
    def test_reset_clears_values(self, settings):
        settings.library_root = "/some/path"
        settings.default_strictness = "strict"
        settings.reset_all()
        assert settings.library_root == ""
        assert settings.default_strictness == "standard"


# ---------------------------------------------------------------------------
# sync / value
# ---------------------------------------------------------------------------

class TestGenericAccess:
    def test_set_and_get_arbitrary_value(self, settings):
        settings.set_value("custom/key", 42)
        assert settings.value("custom/key") == 42

    def test_sync_does_not_raise(self, settings):
        settings.sync()
