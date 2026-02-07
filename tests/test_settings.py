"""Tests for foundry_app.core.settings: load, save, recent-list management."""

from __future__ import annotations

from pathlib import Path

import foundry_app.core.settings as settings_mod
from foundry_app.core.settings import (
    AppSettings,
    add_recent_library,
    add_recent_project,
    load_settings,
    save_settings,
)

# -- Defaults ----------------------------------------------------------------


def test_default_settings():
    """AppSettings() should have sensible defaults for every field."""
    s = AppSettings()
    assert s.library_root == ""
    assert s.workspace_root == "./generated-projects"
    assert s.editor_font_size == 11
    assert s.editor_tab_width == 4
    assert s.validation_strictness == "standard"
    assert s.git_auto_init is False
    assert s.recent_libraries == []
    assert s.recent_projects == []


# -- Round-trip persistence ---------------------------------------------------


def test_save_and_load_roundtrip(tmp_path: Path, monkeypatch):
    """Saving settings and loading them back should yield identical data."""
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_mod, "_SETTINGS_PATH", settings_file)

    original = AppSettings(
        library_root="/some/lib",
        workspace_root="/some/workspace",
        editor_font_size=14,
        editor_tab_width=2,
        validation_strictness="strict",
        git_auto_init=True,
        recent_libraries=["/lib/a", "/lib/b"],
        recent_projects=["/proj/x"],
    )
    save_settings(original)
    loaded = load_settings()

    assert loaded.library_root == original.library_root
    assert loaded.workspace_root == original.workspace_root
    assert loaded.editor_font_size == original.editor_font_size
    assert loaded.editor_tab_width == original.editor_tab_width
    assert loaded.validation_strictness == original.validation_strictness
    assert loaded.git_auto_init == original.git_auto_init
    assert loaded.recent_libraries == original.recent_libraries
    assert loaded.recent_projects == original.recent_projects


# -- Graceful fallback -------------------------------------------------------


def test_load_missing_file_returns_defaults(tmp_path: Path, monkeypatch):
    """When the settings file does not exist, load_settings returns defaults."""
    monkeypatch.setattr(settings_mod, "_SETTINGS_PATH", tmp_path / "nonexistent.json")
    s = load_settings()
    assert s == AppSettings()


def test_load_corrupted_file_returns_defaults(tmp_path: Path, monkeypatch):
    """When the settings file contains invalid JSON, load_settings returns defaults."""
    bad_file = tmp_path / "settings.json"
    bad_file.write_text("NOT VALID JSON {{{", encoding="utf-8")
    monkeypatch.setattr(settings_mod, "_SETTINGS_PATH", bad_file)
    s = load_settings()
    assert s == AppSettings()


# -- Recent libraries ---------------------------------------------------------


def test_add_recent_library_dedup():
    """Adding the same library path twice should not create duplicates."""
    s = AppSettings()
    s = add_recent_library(s, "/lib/one")
    s = add_recent_library(s, "/lib/one")
    assert s.recent_libraries == ["/lib/one"]


def test_add_recent_library_max_5():
    """Recent libraries list is capped at 5, most-recent-first."""
    s = AppSettings()
    for i in range(6):
        s = add_recent_library(s, f"/lib/{i}")

    assert len(s.recent_libraries) == 5
    # Most recently added should be first
    assert s.recent_libraries[0] == "/lib/5"
    # The oldest (lib/0) should have been dropped
    assert "/lib/0" not in s.recent_libraries


# -- Recent projects ----------------------------------------------------------


def test_add_recent_project_max_10():
    """Recent projects list is capped at 10, most-recent-first."""
    s = AppSettings()
    for i in range(11):
        s = add_recent_project(s, f"/proj/{i}")

    assert len(s.recent_projects) == 10
    assert s.recent_projects[0] == "/proj/10"
    assert "/proj/0" not in s.recent_projects
