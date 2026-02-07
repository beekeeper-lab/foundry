"""Wizard page 3 — Technology Stack Selection.

Displays all stacks from the library index with checkboxes for multi-select.
Each stack row shows name/description and a file-count badge.
Selected stacks include an order spin box for controlling prompt compilation order.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    LibraryIndex,
    StackInfo,
    StackSelection,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Human-readable stack descriptions (keyed by directory id)
# ---------------------------------------------------------------------------

STACK_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "clean-code": ("Clean Code", "Code quality principles and refactoring conventions"),
    "devops": ("DevOps", "CI/CD, infrastructure, and deployment conventions"),
    "dotnet": (".NET", "C# / .NET development conventions and patterns"),
    "java": ("Java", "Java development conventions and patterns"),
    "node": ("Node.js", "Node.js runtime and npm ecosystem conventions"),
    "python": ("Python", "Python development conventions and tooling"),
    "python-qt-pyside6": ("Python Qt / PySide6", "PySide6 desktop application conventions"),
    "react": ("React", "React front-end development conventions"),
    "security": ("Security", "Application security practices and guidelines"),
    "sql-dba": ("SQL / DBA", "Database administration and SQL conventions"),
    "typescript": ("TypeScript", "TypeScript language conventions and patterns"),
}

# ---------------------------------------------------------------------------
# Stylesheet constants
# ---------------------------------------------------------------------------

CARD_STYLE = """
QFrame#stack-card {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 12px;
}
QFrame#stack-card:hover {
    border-color: #585b70;
}
"""

CARD_SELECTED_BORDER = "border-color: #89b4fa;"

LABEL_STYLE = "color: #cdd6f4; font-size: 14px; font-weight: bold;"
DESC_STYLE = "color: #6c7086; font-size: 12px;"
CONFIG_LABEL_STYLE = "color: #a6adc8; font-size: 12px;"
HEADING_STYLE = "color: #cdd6f4; font-size: 18px; font-weight: bold;"
SUBHEADING_STYLE = "color: #6c7086; font-size: 13px;"
WARNING_STYLE = "color: #f38ba8; font-size: 12px;"
FILES_STYLE = "color: #a6adc8; font-size: 11px; font-style: italic;"


# ---------------------------------------------------------------------------
# StackCard — single stack row widget
# ---------------------------------------------------------------------------

class StackCard(QFrame):
    """A card representing a single technology stack with checkbox and order control."""

    toggled = Signal(str, bool)  # stack_id, checked

    def __init__(self, stack: StackInfo, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._stack = stack
        self.setObjectName("stack-card")
        self.setStyleSheet(CARD_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # --- Top row: checkbox + name + description ---
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self._checkbox = QCheckBox()
        self._checkbox.stateChanged.connect(self._on_toggled)
        top_row.addWidget(self._checkbox)

        display_name, desc = STACK_DESCRIPTIONS.get(
            self._stack.id, (self._stack.id.replace("-", " ").title(), "")
        )

        name_label = QLabel(display_name)
        name_label.setStyleSheet(LABEL_STYLE)
        top_row.addWidget(name_label)

        desc_label = QLabel(f"— {desc}" if desc else "")
        desc_label.setStyleSheet(DESC_STYLE)
        top_row.addWidget(desc_label, stretch=1)

        # File count badge
        file_count = len(self._stack.files)
        if file_count > 0:
            badge = QLabel(f"{file_count} file{'s' if file_count != 1 else ''}")
            badge.setStyleSheet(FILES_STYLE)
            top_row.addWidget(badge)

        layout.addLayout(top_row)

        # --- Config row (order) ---
        config_row = QHBoxLayout()
        config_row.setSpacing(16)
        config_row.setContentsMargins(28, 0, 0, 0)  # indent under checkbox

        order_label = QLabel("Order:")
        order_label.setStyleSheet(CONFIG_LABEL_STYLE)
        self._order_spin = QSpinBox()
        self._order_spin.setRange(0, 99)
        self._order_spin.setValue(0)
        self._order_spin.setFixedWidth(60)
        config_row.addWidget(order_label)
        config_row.addWidget(self._order_spin)

        config_row.addStretch(1)
        layout.addLayout(config_row)

    # -- State access -------------------------------------------------------

    @property
    def stack_id(self) -> str:
        return self._stack.id

    @property
    def is_selected(self) -> bool:
        return self._checkbox.isChecked()

    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        self._checkbox.setChecked(value)

    def to_stack_selection(self) -> StackSelection:
        """Build a StackSelection from the current card state."""
        return StackSelection(
            id=self._stack.id,
            order=self._order_spin.value(),
        )

    def load_from_selection(self, sel: StackSelection) -> None:
        """Restore card state from a StackSelection."""
        self._checkbox.setChecked(True)
        self._order_spin.setValue(sel.order)

    # -- Slots --------------------------------------------------------------

    def _on_toggled(self, state: int) -> None:
        checked = state == Qt.CheckState.Checked.value
        self.toggled.emit(self._stack.id, checked)
        # Visual feedback — highlight border when selected
        if checked:
            self.setStyleSheet(CARD_STYLE + f"QFrame#stack-card {{ {CARD_SELECTED_BORDER} }}")
        else:
            self.setStyleSheet(CARD_STYLE)


# ---------------------------------------------------------------------------
# StackSelectionPage — wizard page widget
# ---------------------------------------------------------------------------

class StackSelectionPage(QWidget):
    """Wizard page for selecting technology stacks from the library.

    Emits ``selection_changed`` whenever the set of selected stacks changes.
    Call ``get_stack_selections()`` to retrieve the current selections.
    """

    selection_changed = Signal()

    def __init__(
        self,
        library_index: LibraryIndex | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cards: dict[str, StackCard] = {}
        self._warning_label: QLabel | None = None
        self._build_ui()
        if library_index is not None:
            self.load_stacks(library_index)

    # -- UI construction ----------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)

        heading = QLabel("Select Technology Stacks")
        heading.setStyleSheet(HEADING_STYLE)
        outer.addWidget(heading)

        subtitle = QLabel(
            "Choose which technology stack conventions to include. "
            "Each stack adds coding standards and best-practice documents."
        )
        subtitle.setStyleSheet(SUBHEADING_STYLE)
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        # Warning label (hidden by default)
        self._warning_label = QLabel("At least one stack must be selected.")
        self._warning_label.setStyleSheet(WARNING_STYLE)
        self._warning_label.setVisible(False)
        outer.addWidget(self._warning_label)

        # Scrollable area for stack cards
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

    # -- Public API ---------------------------------------------------------

    def load_stacks(self, library_index: LibraryIndex) -> None:
        """Populate the page with stacks from a LibraryIndex."""
        # Clear existing cards
        for card in self._cards.values():
            self._card_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        # Insert cards before the stretch
        insert_idx = 0
        for stack in library_index.stacks:
            card = StackCard(stack)
            card.toggled.connect(self._on_card_toggled)
            self._card_layout.insertWidget(insert_idx, card)
            self._cards[stack.id] = card
            insert_idx += 1

        logger.info("Loaded %d stack cards", len(self._cards))

    def get_stack_selections(self) -> list[StackSelection]:
        """Return a list of StackSelection from currently selected stacks."""
        return [
            card.to_stack_selection()
            for card in self._cards.values()
            if card.is_selected
        ]

    def set_stack_selections(self, selections: list[StackSelection]) -> None:
        """Restore selections from a list of StackSelection."""
        selected_ids = {s.id for s in selections}
        selection_map = {s.id: s for s in selections}

        for sid, card in self._cards.items():
            if sid in selected_ids:
                card.load_from_selection(selection_map[sid])
            else:
                card.is_selected = False

        self._update_warning()

    def selected_count(self) -> int:
        """Return the number of currently selected stacks."""
        return sum(1 for c in self._cards.values() if c.is_selected)

    def is_valid(self) -> bool:
        """Return True if at least one stack is selected."""
        return self.selected_count() > 0

    @property
    def stack_cards(self) -> dict[str, StackCard]:
        """Access cards by stack id (for testing)."""
        return dict(self._cards)

    # -- Slots --------------------------------------------------------------

    def _on_card_toggled(self, stack_id: str, checked: bool) -> None:
        logger.debug("Stack %s toggled: %s", stack_id, checked)
        self._update_warning()
        self.selection_changed.emit()

    def _update_warning(self) -> None:
        if self._warning_label is not None:
            self._warning_label.setVisible(not self.is_valid())
