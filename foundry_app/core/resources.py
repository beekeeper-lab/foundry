"""Resource path resolution."""

from __future__ import annotations

from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _APP_DIR.parent
_BUNDLED_RESOURCES = _APP_DIR / "_resources"


def get_resource_path(relative: str) -> Path:
    """Return the absolute path to a resource file."""
    dev_path = _PROJECT_ROOT / relative
    if dev_path.is_file():
        return dev_path
    parts = Path(relative).parts
    if parts and parts[0] == "resources":
        bundled = _BUNDLED_RESOURCES / Path(*parts[1:])
        if bundled.is_file():
            return bundled
    return dev_path


def splash_image_path() -> Path:
    """Return the path to the splash / branded-background image."""
    return get_resource_path("resources/images/foundry-splash.png")


def logo_icon_path() -> Path:
    """Return the path to the application logo icon."""
    return get_resource_path("resources/icons/foundry-logo.png")
