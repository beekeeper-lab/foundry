"""Step 1: Project — name and subtitle."""

from __future__ import annotations

import re

from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


def _slugify(name: str) -> str:
    """Convert a human project name to a filesystem-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


class ProjectPage(QWidget):
    """Collect project name and subtitle. Slug and output are auto-derived."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Project Name"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Awesome Project")
        self.name_edit.textChanged.connect(self._on_name_changed)
        layout.addWidget(self.name_edit)

        # Auto-generated slug (read-only display)
        layout.addWidget(QLabel("Slug (auto-generated)"))
        self.slug_edit = QLineEdit()
        self.slug_edit.setPlaceholderText("my-awesome-project")
        self.slug_edit.setReadOnly(True)
        self.slug_edit.setStyleSheet("color: #888;")
        layout.addWidget(self.slug_edit)

        layout.addWidget(QLabel("Subtitle (optional — appears in CLAUDE.md)"))
        self.subtitle_edit = QLineEdit()
        self.subtitle_edit.setPlaceholderText("A brief description of what you're building")
        layout.addWidget(self.subtitle_edit)

        layout.addStretch()

    def _on_name_changed(self, text: str) -> None:
        self.slug_edit.setText(_slugify(text))
