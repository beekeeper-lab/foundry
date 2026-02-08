"""Wizard page 1 — Project Identity: name, tagline, and auto-generated slug."""

from __future__ import annotations

import re

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import ProjectIdentity
from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    BG_BASE,
    BG_INSET,
    BORDER_DEFAULT,
    BORDER_SUBTLE,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XL,
    FONT_WEIGHT_BOLD,
    RADIUS_SM,
    SPACE_LG,
    SPACE_MD,
    SPACE_SM,
    SPACE_XXL,
    STATUS_ERROR,
    TEXT_DISABLED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

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
# Stylesheet (themed — industrial dark palette with brass/gold accents)
# ---------------------------------------------------------------------------

PAGE_STYLE = f"""
QLabel#page-title {{
    color: {TEXT_PRIMARY};
    font-size: {FONT_SIZE_XL}px;
    font-weight: {FONT_WEIGHT_BOLD};
}}
QLabel#page-subtitle {{
    color: {TEXT_SECONDARY};
    font-size: {FONT_SIZE_MD}px;
    margin-bottom: {SPACE_MD}px;
}}
QLabel.field-label {{
    color: {TEXT_SECONDARY};
    font-size: {FONT_SIZE_SM}px;
    font-weight: {FONT_WEIGHT_BOLD};
    padding-bottom: {SPACE_SM // 2}px;
}}
QLineEdit {{
    background-color: {BG_INSET};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_SM}px;
    padding: {SPACE_SM}px {SPACE_MD}px;
    font-size: {FONT_SIZE_MD}px;
}}
QLineEdit:focus {{
    border-color: {ACCENT_PRIMARY};
    border-width: 2px;
}}
QLineEdit:read-only {{
    background-color: {BG_BASE};
    color: {TEXT_DISABLED};
    border-color: {BORDER_SUBTLE};
}}
QLabel#slug-preview {{
    color: {TEXT_DISABLED};
    font-size: {FONT_SIZE_SM}px;
    font-style: italic;
}}
QLabel#validation-hint {{
    color: {STATUS_ERROR};
    font-size: {FONT_SIZE_SM}px;
}}
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
        outer.setContentsMargins(SPACE_XXL, SPACE_XXL, SPACE_XXL, SPACE_XXL)
        outer.setSpacing(SPACE_SM)

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

        outer.addSpacing(SPACE_LG)

        # Form — labels above inputs
        self._name_label = QLabel("Project Name")
        self._name_label.setProperty("class", "field-label")
        outer.addWidget(self._name_label)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. My Awesome Project")
        self._name_edit.setMaxLength(120)
        outer.addWidget(self._name_edit)

        # Validation hint (hidden by default, sits below name field)
        self._validation_hint = QLabel("")
        self._validation_hint.setObjectName("validation-hint")
        self._validation_hint.setVisible(False)
        outer.addWidget(self._validation_hint)

        outer.addSpacing(SPACE_MD)

        self._tagline_label = QLabel("Tagline")
        self._tagline_label.setProperty("class", "field-label")
        outer.addWidget(self._tagline_label)

        self._tagline_edit = QLineEdit()
        self._tagline_edit.setPlaceholderText("e.g. A fast, modern API gateway")
        self._tagline_edit.setMaxLength(200)
        outer.addWidget(self._tagline_edit)

        outer.addSpacing(SPACE_MD)

        self._slug_label = QLabel("Slug")
        self._slug_label.setProperty("class", "field-label")
        outer.addWidget(self._slug_label)

        self._slug_edit = QLineEdit()
        self._slug_edit.setReadOnly(True)
        self._slug_edit.setPlaceholderText("auto-generated from name")
        outer.addWidget(self._slug_edit)

        # Slug hint
        self._slug_hint = QLabel(
            "Used as the output folder name and filesystem identifier."
        )
        self._slug_hint.setObjectName("slug-preview")
        outer.addWidget(self._slug_hint)

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
