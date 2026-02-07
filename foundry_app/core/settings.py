"""Application settings: load, save, and manage persistent user preferences."""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Validated application settings with sensible defaults."""

    library_root: str = ""
    workspace_root: str = "./generated-projects"
    editor_font_size: int = 11
    editor_tab_width: int = 4
    validation_strictness: str = "standard"  # light | standard | strict
    git_auto_init: bool = False
    recent_libraries: list[str] = Field(default_factory=list)
    recent_projects: list[str] = Field(default_factory=list)


_SETTINGS_PATH = Path.home() / ".config" / "foundry" / "settings.json"


def load_settings() -> AppSettings:
    """Load settings from disk, returning defaults if file doesn't exist."""
    if not _SETTINGS_PATH.is_file():
        return AppSettings()
    try:
        raw = _SETTINGS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        return AppSettings.model_validate(data)
    except (json.JSONDecodeError, ValueError, OSError):
        return AppSettings()


def save_settings(settings: AppSettings) -> None:
    """Save settings to disk, creating parent directories as needed."""
    _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = settings.model_dump()
    _SETTINGS_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def add_recent_library(settings: AppSettings, path: str) -> AppSettings:
    """Add a library path to recent list (dedup, max 5), return updated settings."""
    paths = [p for p in settings.recent_libraries if p != path]
    paths.insert(0, path)
    return settings.model_copy(update={"recent_libraries": paths[:5]})


def add_recent_project(settings: AppSettings, path: str) -> AppSettings:
    """Add a project path to recent list (dedup, max 10), return updated settings."""
    paths = [p for p in settings.recent_projects if p != path]
    paths.insert(0, path)
    return settings.model_copy(update={"recent_projects": paths[:10]})


def validate_library_path(path: str) -> list[str]:
    """Validate that *path* points to a usable ai-team-library root.

    Returns a list of issues found (empty list means valid).
    """
    issues: list[str] = []
    p = Path(path)
    if not p.is_dir():
        issues.append(f"Directory does not exist: {path}")
        return issues
    if not (p / "personas").is_dir():
        issues.append(f"Missing 'personas/' subdirectory in {path}")
    if not (p / "stacks").is_dir():
        issues.append(f"Missing 'stacks/' subdirectory in {path}")
    return issues


def validate_workspace_path(path: str) -> list[str]:
    """Validate that *path* is a usable workspace directory.

    Returns a list of issues found (empty list means valid).
    """
    issues: list[str] = []
    p = Path(path)
    if p.is_dir():
        if not os.access(p, os.W_OK):
            issues.append(f"Directory is not writable: {path}")
    elif p.parent.is_dir():
        if not os.access(p.parent, os.W_OK):
            issues.append(f"Parent directory is not writable: {p.parent}")
    else:
        issues.append(f"Neither directory nor parent exist: {path}")
    return issues
