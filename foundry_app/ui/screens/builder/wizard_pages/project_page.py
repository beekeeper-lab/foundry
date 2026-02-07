"""Wizard page 1 — Project Identity: name, tagline, and auto-generated slug."""

from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import ProjectIdentity

# ---------------------------------------------------------------------------
# Slug helper
# ---------------------------------------------------------------------------


def _slugify(text: str) -> str:
    """Convert *text* to a URL/filesystem-safe slug.

    Rules match the ``ProjectIdentity.slug`` regex ``^[a-z0-9][a-z0-9-]*$``:
    lowercase, leading non-alnum stripped, interior non-alnum replaced with
    single hyphens, trailing hyphens stripped.
    """
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


# ---------------------------------------------------------------------------
# Stylesheet (extends the Catppuccin theme from MainWindow)
# ---------------------------------------------------------------------------

PAGE_STYLE = """
QLabel#page-title {
    color: #cdd6f4;
    font-size: 22px;
    font-weight: bold;
}
QLabel#page-subtitle {
    color: #a6adc8;
    font-size: 14px;
    margin-bottom: 12px;
}
QLabel.field-label {
    color: #cdd6f4;
    font-size: 13px;
}
QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
}
QLineEdit:focus {
    border-color: #cba6f7;
}
QLineEdit:read-only {
    background-color: #1e1e2e;
    color: #6c7086;
    border-color: #313244;
}
QLabel#slug-preview {
    color: #6c7086;
    font-size: 12px;
    font-style: italic;
}
QLabel#validation-hint {
    color: #f38ba8;
    font-size: 12px;
}
"""


# ---------------------------------------------------------------------------
# ProjectPage widget
# ---------------------------------------------------------------------------


class ProjectPage(QWidget):
    """First wizard page — captures project name, tagline, and slug."""

    completeness_changed = Signal(bool)
    """Emitted whenever the page transitions between complete and incomplete."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(PAGE_STYLE)
        self._was_complete = False
        self._build_ui()
        self._connect_signals()

    # -- UI construction ---------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 32, 40, 32)
        outer.setSpacing(8)

        # Header
        title = QLabel("Create Your Project")
        title.setObjectName("page-title")
        outer.addWidget(title)

        subtitle = QLabel(
            "Give your project a name and an optional tagline. "
            "A URL-safe slug will be generated automatically."
        )
        subtitle.setObjectName("page-subtitle")
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        outer.addSpacing(12)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. My Awesome Project")
        self._name_edit.setMaxLength(120)
        name_label = QLabel("Project Name")
        name_label.setProperty("class", "field-label")
        form.addRow(name_label, self._name_edit)

        self._tagline_edit = QLineEdit()
        self._tagline_edit.setPlaceholderText("e.g. A fast, modern API gateway")
        self._tagline_edit.setMaxLength(200)
        tagline_label = QLabel("Tagline")
        tagline_label.setProperty("class", "field-label")
        form.addRow(tagline_label, self._tagline_edit)

        self._slug_edit = QLineEdit()
        self._slug_edit.setReadOnly(True)
        self._slug_edit.setPlaceholderText("auto-generated from name")
        slug_label = QLabel("Slug")
        slug_label.setProperty("class", "field-label")
        form.addRow(slug_label, self._slug_edit)

        outer.addLayout(form)

        # Slug hint
        self._slug_hint = QLabel(
            "Used as the output folder name and filesystem identifier."
        )
        self._slug_hint.setObjectName("slug-preview")
        outer.addWidget(self._slug_hint)

        # Validation hint (hidden by default)
        self._validation_hint = QLabel("")
        self._validation_hint.setObjectName("validation-hint")
        self._validation_hint.setVisible(False)
        outer.addWidget(self._validation_hint)

        outer.addStretch(1)

    def _connect_signals(self) -> None:
        self._name_edit.textChanged.connect(self._on_name_changed)

    # -- Slots -------------------------------------------------------------

    def _on_name_changed(self, text: str) -> None:
        slug = _slugify(text)
        self._slug_edit.setText(slug)

        # Update validation hint
        if text.strip():
            self._validation_hint.setVisible(False)
        else:
            self._validation_hint.setText("Project name is required.")
            self._validation_hint.setVisible(True)

        # Emit completeness change
        now_complete = self.is_complete()
        if now_complete != self._was_complete:
            self._was_complete = now_complete
            self.completeness_changed.emit(now_complete)

    # -- Public API --------------------------------------------------------

    def is_complete(self) -> bool:
        """Return True when enough data has been entered to proceed."""
        return bool(self._name_edit.text().strip())

    def get_data(self) -> ProjectIdentity:
        """Build a ProjectIdentity from the current form state."""
        name = self._name_edit.text().strip()
        slug = self._slug_edit.text() or _slugify(name)
        return ProjectIdentity(name=name, slug=slug)

    def set_data(self, identity: ProjectIdentity) -> None:
        """Populate the form from an existing ProjectIdentity."""
        self._name_edit.setText(identity.name)
        # Slug auto-updates via signal

    @property
    def name_edit(self) -> QLineEdit:
        """Access the name input (for testing)."""
        return self._name_edit

    @property
    def tagline_edit(self) -> QLineEdit:
        """Access the tagline input (for testing)."""
        return self._tagline_edit

    @property
    def slug_edit(self) -> QLineEdit:
        """Access the slug display (for testing)."""
        return self._slug_edit
