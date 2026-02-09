"""QSettings-backed persistent user preferences for Foundry."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QByteArray, QSettings, QSize

logger = logging.getLogger(__name__)

_DEFAULTS: dict[str, object] = {
    "library_root": "",
    "workspace_root": "",
    "recent_libraries": [],
    "window/size": QSize(1100, 750),
    "window/pos": None,
    "window/geometry": QByteArray(),
    "window/state": QByteArray(),
}

MAX_RECENT = 10


class FoundrySettings:
    """Thin wrapper around QSettings for Foundry user preferences.

    All keys are namespaced under the *Foundry* organisation/application
    so they do not collide with other Qt apps on the same machine.
    """

    def __init__(self, *, scope: QSettings.Scope = QSettings.Scope.UserScope) -> None:
        self._qs = QSettings(scope, "Foundry", "Foundry")

    # -- generic helpers ---------------------------------------------------

    def value(self, key: str, default: object = None) -> object:
        fallback = default if default is not None else _DEFAULTS.get(key)
        return self._qs.value(key, fallback)

    def set_value(self, key: str, val: object) -> None:
        self._qs.setValue(key, val)

    def sync(self) -> None:
        self._qs.sync()

    # -- typed accessors ---------------------------------------------------

    @property
    def library_root(self) -> str:
        return str(self.value("library_root", ""))

    @library_root.setter
    def library_root(self, path: str | Path) -> None:
        self.set_value("library_root", str(path))

    @property
    def workspace_root(self) -> str:
        return str(self.value("workspace_root", ""))

    @workspace_root.setter
    def workspace_root(self, path: str | Path) -> None:
        self.set_value("workspace_root", str(path))

    @property
    def recent_libraries(self) -> list[str]:
        val = self.value("recent_libraries", [])
        if isinstance(val, list):
            return val
        return []

    def add_recent_library(self, path: str | Path) -> None:
        recent = self.recent_libraries
        s = str(path)
        if s in recent:
            recent.remove(s)
        recent.insert(0, s)
        self.set_value("recent_libraries", recent[:MAX_RECENT])

    # -- generation defaults -----------------------------------------------

    @property
    def default_overlay_mode(self) -> bool:
        val = self.value("generation/overlay_mode", False)
        return val in (True, "true", "True")

    @default_overlay_mode.setter
    def default_overlay_mode(self, enabled: bool) -> None:
        self.set_value("generation/overlay_mode", enabled)

    @property
    def default_strictness(self) -> str:
        val = str(self.value("generation/strictness", "standard"))
        return val if val in ("light", "standard", "strict") else "standard"

    @default_strictness.setter
    def default_strictness(self, level: str) -> None:
        self.set_value("generation/strictness", level)

    @property
    def default_seed_mode(self) -> str:
        val = str(self.value("generation/seed_mode", "detailed"))
        return val if val in ("detailed", "kickoff", "none") else "detailed"

    @default_seed_mode.setter
    def default_seed_mode(self, mode: str) -> None:
        self.set_value("generation/seed_mode", mode)

    # -- safety defaults ---------------------------------------------------

    @property
    def default_safety_posture(self) -> str:
        val = str(self.value("safety/posture", "baseline"))
        return val if val in ("baseline", "hardened", "regulated") else "baseline"

    @default_safety_posture.setter
    def default_safety_posture(self, posture: str) -> None:
        self.set_value("safety/posture", posture)

    @property
    def write_safety_config(self) -> bool:
        val = self.value("safety/write_config", True)
        return val in (True, "true", "True")

    @write_safety_config.setter
    def write_safety_config(self, enabled: bool) -> None:
        self.set_value("safety/write_config", enabled)

    # -- appearance --------------------------------------------------------

    @property
    def font_size_preference(self) -> str:
        val = str(self.value("appearance/font_size", "medium"))
        return val if val in ("small", "medium", "large") else "medium"

    @font_size_preference.setter
    def font_size_preference(self, size: str) -> None:
        self.set_value("appearance/font_size", size)

    @property
    def theme_preference(self) -> str:
        val = str(self.value("appearance/theme", "dark"))
        return val if val in ("dark",) else "dark"

    @theme_preference.setter
    def theme_preference(self, name: str) -> None:
        self.set_value("appearance/theme", name)

    # -- advanced ----------------------------------------------------------

    def reset_all(self) -> None:
        """Clear all settings and restore defaults."""
        self._qs.clear()
        self._qs.sync()
        logger.info("All settings reset to defaults")

    # -- window geometry ---------------------------------------------------

    @property
    def window_geometry(self) -> QByteArray:
        val = self.value("window/geometry", QByteArray())
        return val if isinstance(val, QByteArray) else QByteArray()

    @window_geometry.setter
    def window_geometry(self, data: QByteArray) -> None:
        self.set_value("window/geometry", data)

    @property
    def window_state(self) -> QByteArray:
        val = self.value("window/state", QByteArray())
        return val if isinstance(val, QByteArray) else QByteArray()

    @window_state.setter
    def window_state(self, data: QByteArray) -> None:
        self.set_value("window/state", data)
