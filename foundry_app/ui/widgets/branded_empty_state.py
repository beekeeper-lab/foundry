"""Reusable branded empty-state widget with splash background image."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from foundry_app.core.resources import splash_image_path
from foundry_app.ui.theme import TEXT_PRIMARY, TEXT_SECONDARY


class BrandedEmptyState(QWidget):
    """Full-size widget showing the splash image with an overlay and centered text."""

    def __init__(
        self,
        heading: str,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._pixmap: QPixmap | None = None

        img_path = splash_image_path()
        if img_path.is_file():
            self._pixmap = QPixmap(str(img_path))

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._heading = QLabel(heading)
        self._heading.setFont(QFont("", 24, QFont.Weight.Bold))
        self._heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._heading.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")

        self._description = QLabel(description)
        self._description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description.setWordWrap(True)
        self._description.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 15px; background: transparent;"
        )

        layout.addWidget(self._heading)
        layout.addWidget(self._description)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        rect = self.rect()

        if self._pixmap and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                rect.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (rect.width() - scaled.width()) // 2
            y = (rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter.fillRect(rect, Qt.GlobalColor.black)

        overlay = QColor(30, 30, 46, 153)
        painter.fillRect(rect, overlay)
        painter.end()
