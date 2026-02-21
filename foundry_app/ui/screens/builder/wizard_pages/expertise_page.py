"""Wizard page 3 — Expertise Selection.

Displays all expertise from the library index with checkboxes for multi-select.
Each expertise row shows name/description and file count badge.
Selected expertise can be reordered to control compilation priority.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    ExpertiseInfo,
    ExpertiseSelection,
    LibraryIndex,
)
from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    ACCENT_SECONDARY_MUTED,
    BG_INSET,
    BG_SURFACE,
    BORDER_DEFAULT,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XL,
    FONT_SIZE_XS,
    FONT_WEIGHT_BOLD,
    RADIUS_MD,
    RADIUS_SM,
    SPACE_MD,
    STATUS_ERROR,
    TEXT_DISABLED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

logger = logging.getLogger(__name__)

EXPERTISE_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "clean-code": ("Clean Code", "Code quality standards, naming conventions, SOLID principles"),
    "devops": ("DevOps", "CI/CD pipelines, infrastructure as code, deployment automation"),
    "dotnet": (".NET / C#", "ASP.NET Core, Entity Framework, NuGet packaging"),
    "java": ("Java", "Spring Boot, Maven/Gradle, JVM ecosystem conventions"),
    "node": ("Node.js", "Express/Fastify, npm packaging, API design patterns"),
    "python": ("Python", "Packaging, testing, performance, security conventions"),
    "python-qt-pyside6": ("Python Qt (PySide6)", "Desktop GUI with PySide6, Qt patterns"),
    "react": ("React", "Components, state management, accessibility, testing"),
    "security": ("Security", "OWASP guidelines, threat modeling, secure coding"),
    "sql-dba": ("SQL / DBA", "Database design, query optimization, migrations"),
    "typescript": ("TypeScript", "Type safety, module patterns, build tooling"),
}

CARD_STYLE = f"""
QFrame#expertise-card {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD}px;
    padding: {SPACE_MD}px;
}}
QFrame#expertise-card:hover {{
    border-color: {ACCENT_SECONDARY_MUTED};
}}
"""

CARD_SELECTED_BORDER = f"border-color: {ACCENT_PRIMARY};"

LABEL_STYLE = (
    f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px; font-weight: {FONT_WEIGHT_BOLD};"
)
DESC_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
HEADING_STYLE = (
    f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_XL}px; font-weight: {FONT_WEIGHT_BOLD};"
)
SUBHEADING_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
WARNING_STYLE = f"color: {STATUS_ERROR}; font-size: {FONT_SIZE_SM}px;"
FILES_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_XS}px; font-style: italic;"
ORDER_BTN_STYLE = f"""
QPushButton {{
    background-color: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_SM}px;
    padding: 2px 8px;
    font-size: {FONT_SIZE_SM}px;
}}
QPushButton:hover {{
    background-color: {BG_INSET};
}}
QPushButton:disabled {{
    color: {TEXT_DISABLED};
    background-color: {BG_INSET};
    border-color: {BORDER_DEFAULT};
}}
"""


class ExpertiseCard(QFrame):
    """A card representing a single expertise with checkbox."""

    toggled = Signal(str, bool)

    def __init__(self, expertise: ExpertiseInfo, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._expertise = expertise
        self.setObjectName("expertise-card")
        self.setStyleSheet(CARD_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        self._checkbox = QCheckBox()
        self._checkbox.stateChanged.connect(self._on_toggled)
        layout.addWidget(self._checkbox)

        display_name, desc = EXPERTISE_DESCRIPTIONS.get(
            self._expertise.id, (self._expertise.id.replace("-", " ").title(), "")
        )

        name_label = QLabel(display_name)
        name_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(name_label)

        desc_label = QLabel(f"— {desc}" if desc else "")
        desc_label.setStyleSheet(DESC_STYLE)
        layout.addWidget(desc_label, stretch=1)

        file_count = len(self._expertise.files)
        if file_count > 0:
            badge = QLabel(f"{file_count} file{'s' if file_count != 1 else ''}")
            badge.setStyleSheet(FILES_STYLE)
            layout.addWidget(badge)

    @property
    def expertise_id(self) -> str:
        return self._expertise.id

    @property
    def is_selected(self) -> bool:
        return self._checkbox.isChecked()

    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        self._checkbox.setChecked(value)

    @property
    def file_count(self) -> int:
        return len(self._expertise.files)

    def to_expertise_selection(self, order: int = 0) -> ExpertiseSelection:
        return ExpertiseSelection(id=self._expertise.id, order=order)

    def load_from_selection(self, sel: ExpertiseSelection) -> None:
        self._checkbox.setChecked(True)

    def _on_toggled(self, state: int) -> None:
        checked = state == Qt.CheckState.Checked.value
        self.toggled.emit(self._expertise.id, checked)
        if checked:
            self.setStyleSheet(
                CARD_STYLE + f"QFrame#expertise-card {{ {CARD_SELECTED_BORDER} }}"
            )
        else:
            self.setStyleSheet(CARD_STYLE)


class ExpertiseSelectionPage(QWidget):
    """Wizard page for selecting expertise from the library."""

    selection_changed = Signal()

    def __init__(
        self,
        library_index: LibraryIndex | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cards: dict[str, ExpertiseCard] = {}
        self._ordered_ids: list[str] = []
        self._warning_label: QLabel | None = None
        self._build_ui()
        if library_index is not None:
            self.load_expertise(library_index)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)

        heading = QLabel("Select Expertise")
        heading.setStyleSheet(HEADING_STYLE)
        outer.addWidget(heading)

        subtitle = QLabel(
            "Choose the expertise for your project. "
            "Each expertise provides coding conventions, testing patterns, and best practices. "
            "Use the arrow buttons to set compilation priority (higher = compiled first)."
        )
        subtitle.setStyleSheet(SUBHEADING_STYLE)
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        self._warning_label = QLabel("At least one expertise must be selected.")
        self._warning_label.setStyleSheet(WARNING_STYLE)
        self._warning_label.setVisible(False)
        outer.addWidget(self._warning_label)

        # Empty-state label (visible until library is loaded)
        self._empty_label = QLabel(
            "No library loaded. Go to Settings and configure your "
            "Library Root to populate this page."
        )
        self._empty_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setWordWrap(True)
        outer.addWidget(self._empty_label)

        order_row = QHBoxLayout()
        order_row.setSpacing(8)

        self._move_up_btn = QPushButton("\u25b2 Move Up")
        self._move_up_btn.setToolTip("Move selected expertise higher in compilation order")
        self._move_up_btn.setStyleSheet(ORDER_BTN_STYLE)
        self._move_up_btn.setEnabled(False)
        self._move_up_btn.clicked.connect(self._on_move_up)
        order_row.addWidget(self._move_up_btn)

        self._move_down_btn = QPushButton("\u25bc Move Down")
        self._move_down_btn.setToolTip("Move selected expertise lower in compilation order")
        self._move_down_btn.setStyleSheet(ORDER_BTN_STYLE)
        self._move_down_btn.setEnabled(False)
        self._move_down_btn.clicked.connect(self._on_move_down)
        order_row.addWidget(self._move_down_btn)

        order_row.addStretch(1)
        outer.addLayout(order_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self._card_container = QWidget()
        self._card_layout = QVBoxLayout(self._card_container)
        self._card_layout.setContentsMargins(0, 0, 0, 0)
        self._card_layout.setSpacing(8)
        self._card_layout.addStretch(1)

        scroll.setWidget(self._card_container)
        outer.addWidget(scroll, stretch=1)

    def load_expertise(self, library_index: LibraryIndex) -> None:
        for card in self._cards.values():
            self._card_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()
        self._ordered_ids.clear()

        insert_idx = 0
        for expertise in library_index.expertise:
            card = ExpertiseCard(expertise)
            card.toggled.connect(self._on_card_toggled)
            self._card_layout.insertWidget(insert_idx, card)
            self._cards[expertise.id] = card
            insert_idx += 1

        self._empty_label.setVisible(len(self._cards) == 0)
        logger.info("Loaded %d expertise cards", len(self._cards))

    def get_expertise_selections(self) -> list[ExpertiseSelection]:
        selections: list[ExpertiseSelection] = []
        for idx, sid in enumerate(self._ordered_ids):
            if sid in self._cards and self._cards[sid].is_selected:
                selections.append(self._cards[sid].to_expertise_selection(order=idx))
        next_order = len(selections)
        for sid, card in self._cards.items():
            if card.is_selected and sid not in self._ordered_ids:
                selections.append(card.to_expertise_selection(order=next_order))
                next_order += 1
        return selections

    def set_expertise_selections(self, selections: list[ExpertiseSelection]) -> None:
        sorted_sels = sorted(selections, key=lambda s: s.order)
        for card in self._cards.values():
            card.is_selected = False
        self._ordered_ids = [s.id for s in sorted_sels if s.id in self._cards]
        for sel in sorted_sels:
            if sel.id in self._cards:
                self._cards[sel.id].load_from_selection(sel)
        self._update_warning()
        self._update_order_buttons()

    def selected_count(self) -> int:
        return sum(1 for c in self._cards.values() if c.is_selected)

    def is_valid(self) -> bool:
        return self.selected_count() > 0

    @property
    def expertise_cards(self) -> dict[str, ExpertiseCard]:
        return dict(self._cards)

    @property
    def ordered_ids(self) -> list[str]:
        return list(self._ordered_ids)

    def move_expertise_up(self, expertise_id: str) -> None:
        if expertise_id not in self._ordered_ids:
            return
        idx = self._ordered_ids.index(expertise_id)
        if idx <= 0:
            return
        self._ordered_ids[idx], self._ordered_ids[idx - 1] = (
            self._ordered_ids[idx - 1],
            self._ordered_ids[idx],
        )
        self._update_order_buttons()
        self.selection_changed.emit()

    def move_expertise_down(self, expertise_id: str) -> None:
        if expertise_id not in self._ordered_ids:
            return
        idx = self._ordered_ids.index(expertise_id)
        if idx >= len(self._ordered_ids) - 1:
            return
        self._ordered_ids[idx], self._ordered_ids[idx + 1] = (
            self._ordered_ids[idx + 1],
            self._ordered_ids[idx],
        )
        self._update_order_buttons()
        self.selection_changed.emit()

    def _on_card_toggled(self, expertise_id: str, checked: bool) -> None:
        logger.debug("Expertise %s toggled: %s", expertise_id, checked)
        if checked:
            if expertise_id not in self._ordered_ids:
                self._ordered_ids.append(expertise_id)
        else:
            if expertise_id in self._ordered_ids:
                self._ordered_ids.remove(expertise_id)
        self._update_warning()
        self._update_order_buttons()
        self.selection_changed.emit()

    def _update_warning(self) -> None:
        if self._warning_label is not None:
            self._warning_label.setVisible(not self.is_valid())

    def _update_order_buttons(self) -> None:
        has_ordered = len(self._ordered_ids) > 1
        self._move_up_btn.setEnabled(has_ordered)
        self._move_down_btn.setEnabled(has_ordered)

    def _on_move_up(self) -> None:
        if len(self._ordered_ids) >= 2:
            self.move_expertise_up(self._ordered_ids[-1])

    def _on_move_down(self) -> None:
        if len(self._ordered_ids) >= 2:
            self.move_expertise_down(self._ordered_ids[0])
