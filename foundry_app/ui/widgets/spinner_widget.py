"""Reusable spinning gear widget for loading/progress indication."""

from __future__ import annotations

import math

from PySide6.QtCore import (
    Property,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
)
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from foundry_app.ui.theme import ACCENT_PRIMARY


class SpinnerWidget(QWidget):
    """Animated spinning gear indicator.

    Uses QPainter to draw a gear/cog shape and QPropertyAnimation for
    smooth rotation.  Call ``start()`` to begin spinning and ``stop()``
    to halt the animation.
    """

    def __init__(
        self,
        size: int = 48,
        color: str = ACCENT_PRIMARY,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._size = size
        self._color = QColor(color)
        self._angle = 0.0

        self.setFixedSize(QSize(size, size))

        self._animation = QPropertyAnimation(self, b"rotation_angle")
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(360.0)
        self._animation.setDuration(2000)
        self._animation.setLoopCount(-1)  # infinite

    # -- Qt property for animation -----------------------------------------

    def _get_rotation_angle(self) -> float:
        return self._angle

    def _set_rotation_angle(self, value: float) -> None:
        self._angle = value
        self.update()

    rotation_angle = Property(float, _get_rotation_angle, _set_rotation_angle)

    # -- Public API --------------------------------------------------------

    @property
    def is_spinning(self) -> bool:
        return self._animation.state() == QPropertyAnimation.State.Running

    def start(self) -> None:
        """Start the spinning animation."""
        if not self.is_spinning:
            self._animation.start()

    def stop(self) -> None:
        """Stop the spinning animation."""
        self._animation.stop()
        self._angle = 0.0
        self.update()

    # -- Painting ----------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self._size / 2
        cy = self._size / 2

        painter.translate(cx, cy)
        painter.rotate(self._angle)

        pen = QPen(self._color, max(1, self._size // 20))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw gear: outer ring with teeth
        outer_r = self._size * 0.40
        inner_r = self._size * 0.28
        teeth = 8
        tooth_width = math.pi / teeth  # angular half-width of each tooth

        from PySide6.QtGui import QPainterPath

        path = QPainterPath()
        for i in range(teeth):
            angle = 2 * math.pi * i / teeth

            # Outer tooth point
            x1 = outer_r * math.cos(angle - tooth_width * 0.5)
            y1 = outer_r * math.sin(angle - tooth_width * 0.5)
            x2 = outer_r * math.cos(angle + tooth_width * 0.5)
            y2 = outer_r * math.sin(angle + tooth_width * 0.5)

            # Inner valley point
            valley_angle = angle + math.pi / teeth
            x3 = inner_r * math.cos(valley_angle - tooth_width * 0.3)
            y3 = inner_r * math.sin(valley_angle - tooth_width * 0.3)
            x4 = inner_r * math.cos(valley_angle + tooth_width * 0.3)
            y4 = inner_r * math.sin(valley_angle + tooth_width * 0.3)

            if i == 0:
                path.moveTo(x1, y1)
            else:
                path.lineTo(x1, y1)
            path.lineTo(x2, y2)
            path.lineTo(x3, y3)
            path.lineTo(x4, y4)

        path.closeSubpath()

        painter.setBrush(self._color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

        # Center hole
        hole_r = self._size * 0.12
        painter.setBrush(self.palette().window().color())
        painter.drawEllipse(QRect(
            int(-hole_r), int(-hole_r),
            int(hole_r * 2), int(hole_r * 2),
        ))

        painter.end()
