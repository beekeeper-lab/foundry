"""Icon loader for the Foundry industrial icon set.

Loads monochrome SVG icons from the ``foundry_app/ui/icons/`` directory and
optionally tints them to a specified color at runtime.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QIcon

_ICONS_DIR = Path(__file__).parent / "icons"

# All available icon names
ICON_NAMES: list[str] = [
    # Navigation
    "builder",
    "history",
    "settings",
    "library",
    # Actions
    "generate",
    "export",
    "add",
    "remove",
    "move-up",
    "move-down",
    "refresh",
    # Status
    "success",
    "error",
    "warning",
    "pending",
    "running",
    # UI
    "expand",
    "collapse",
    "search",
    "folder",
]


def icon_path(name: str) -> Path:
    """Return the filesystem path to the SVG for *name*.

    Raises ``FileNotFoundError`` if the icon does not exist.
    """
    path = _ICONS_DIR / f"{name}.svg"
    if not path.is_file():
        raise FileNotFoundError(f"Icon not found: {name}")
    return path


_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _tint_svg(svg_bytes: bytes, color: str) -> bytes:
    """Replace stroke/fill color values in raw SVG bytes with *color*."""
    if not _HEX_COLOR_RE.match(color):
        raise ValueError(f"Invalid hex color: {color!r}")
    text = svg_bytes.decode("utf-8")
    text = re.sub(r'stroke="#[0-9a-fA-F]{6}"', f'stroke="{color}"', text)
    text = re.sub(r'fill="#[0-9a-fA-F]{6}"', f'fill="{color}"', text)
    return text.encode("utf-8")


def load_icon(name: str, *, color: str | None = None, size: int = 24) -> QIcon:
    """Load an icon by name and return a ``QIcon``.

    Parameters
    ----------
    name:
        Icon name without extension (e.g. ``"builder"``).
    color:
        Optional hex color string to tint the icon (e.g. ``"#c9a84c"``).
        When *None*, the icon keeps its original white stroke color.
    size:
        Pixel size for the rendered icon (default 24).

    Returns
    -------
    QIcon
        The rendered and optionally tinted icon.

    Raises
    ------
    FileNotFoundError
        If no SVG file exists for the given *name*.
    """
    from PySide6.QtCore import QByteArray, QSize
    from PySide6.QtGui import QIcon, QPainter, QPixmap
    from PySide6.QtSvg import QSvgRenderer

    path = icon_path(name)
    svg_bytes = path.read_bytes()

    if color is not None:
        svg_bytes = _tint_svg(svg_bytes, color)

    renderer = QSvgRenderer(QByteArray(svg_bytes))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill()  # transparent fill

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


def available_icons() -> list[str]:
    """Return sorted list of available icon names (based on files on disk)."""
    return sorted(p.stem for p in _ICONS_DIR.glob("*.svg"))
