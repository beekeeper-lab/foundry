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
