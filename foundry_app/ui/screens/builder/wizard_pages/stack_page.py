"""Wizard page 3 — Technology Stack Selection.

Displays all stacks from the library index with checkboxes for multi-select.
Each stack row shows name/description and file count badge.
Selected stacks can be reordered to control compilation priority.
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
    LibraryIndex,
    StackInfo,
    StackSelection,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Human-readable stack descriptions (keyed by directory id)
# ---------------------------------------------------------------------------

STACK_DESCRIPTIONS: dict[str, tuple[str, str]] = {
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

# ---------------------------------------------------------------------------
# Stylesheet constants (Catppuccin Mocha theme)
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
HEADING_STYLE = "color: #cdd6f4; font-size: 18px; font-weight: bold;"
SUBHEADING_STYLE = "color: #6c7086; font-size: 13px;"
WARNING_STYLE = "color: #f38ba8; font-size: 12px;"
FILES_STYLE = "color: #a6adc8; font-size: 11px; font-style: italic;"
ORDER_BTN_STYLE = """
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #45475a;
}
QPushButton:disabled {
    color: #585b70;
    background-color: #1e1e2e;
    border-color: #313244;
}
"""


# ---------------------------------------------------------------------------
# StackCard — single stack row widget
# ---------------------------------------------------------------------------

class StackCard(QFrame):
    """A card representing a single technology stack with checkbox."""

    toggled = Signal(str, bool)  # stack_id, checked

    def __init__(self, stack: StackInfo, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._stack = stack
        self.setObjectName("stack-card")
        self.setStyleSheet(CARD_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # Checkbox
        self._checkbox = QCheckBox()
        self._checkbox.stateChanged.connect(self._on_toggled)
        layout.addWidget(self._checkbox)

        # Name and description
        display_name, desc = STACK_DESCRIPTIONS.get(
            self._stack.id, (self._stack.id.replace("-", " ").title(), "")
        )

        name_label = QLabel(display_name)
        name_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(name_label)

        desc_label = QLabel(f"— {desc}" if desc else "")
        desc_label.setStyleSheet(DESC_STYLE)
        layout.addWidget(desc_label, stretch=1)

        # File count badge
        file_count = len(self._stack.files)
        if file_count > 0:
            badge = QLabel(f"{file_count} file{'s' if file_count != 1 else ''}")
            badge.setStyleSheet(FILES_STYLE)
            layout.addWidget(badge)

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

    @property
    def file_count(self) -> int:
        return len(self._stack.files)

    def to_stack_selection(self, order: int = 0) -> StackSelection:
        """Build a StackSelection from the current card state."""
        return StackSelection(id=self._stack.id, order=order)

    def load_from_selection(self, sel: StackSelection) -> None:
        """Restore card state from a StackSelection."""
        self._checkbox.setChecked(True)

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
        self._ordered_ids: list[str] = []  # tracks selection order
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
            "Choose the technology stacks for your project. "
            "Each stack provides coding conventions, testing patterns, and best practices. "
            "Use the arrow buttons to set compilation priority (higher = compiled first)."
        )
        subtitle.setStyleSheet(SUBHEADING_STYLE)
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        # Warning label (hidden by default)
        self._warning_label = QLabel("At least one stack must be selected.")
        self._warning_label.setStyleSheet(WARNING_STYLE)
        self._warning_label.setVisible(False)
        outer.addWidget(self._warning_label)

        # Order controls
        order_row = QHBoxLayout()
        order_row.setSpacing(8)

        self._move_up_btn = QPushButton("\u25b2 Move Up")
        self._move_up_btn.setStyleSheet(ORDER_BTN_STYLE)
        self._move_up_btn.setEnabled(False)
        self._move_up_btn.clicked.connect(self._on_move_up)
        order_row.addWidget(self._move_up_btn)

        self._move_down_btn = QPushButton("\u25bc Move Down")
        self._move_down_btn.setStyleSheet(ORDER_BTN_STYLE)
        self._move_down_btn.setEnabled(False)
        self._move_down_btn.clicked.connect(self._on_move_down)
        order_row.addWidget(self._move_down_btn)

        order_row.addStretch(1)
        outer.addLayout(order_row)

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
        self._ordered_ids.clear()

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
        """Return a list of StackSelection from currently selected stacks, ordered."""
        selections: list[StackSelection] = []

        # First add ordered (explicitly ordered) stacks
        for idx, sid in enumerate(self._ordered_ids):
            if sid in self._cards and self._cards[sid].is_selected:
                selections.append(self._cards[sid].to_stack_selection(order=idx))

        # Then add any selected stacks not yet in the ordered list
        next_order = len(selections)
        for sid, card in self._cards.items():
            if card.is_selected and sid not in self._ordered_ids:
                selections.append(card.to_stack_selection(order=next_order))
                next_order += 1

        return selections

    def set_stack_selections(self, selections: list[StackSelection]) -> None:
        """Restore selections from a list of StackSelection (e.g. when navigating back)."""
        # Sort by order to restore ordering
        sorted_sels = sorted(selections, key=lambda s: s.order)

        # Reset all cards
        for card in self._cards.values():
            card.is_selected = False

        # Restore ordered list
        self._ordered_ids = [s.id for s in sorted_sels if s.id in self._cards]

        # Restore card states
        for sel in sorted_sels:
            if sel.id in self._cards:
                self._cards[sel.id].load_from_selection(sel)

        self._update_warning()
        self._update_order_buttons()

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

    @property
    def ordered_ids(self) -> list[str]:
        """Access the current ordering (for testing)."""
        return list(self._ordered_ids)

    def move_stack_up(self, stack_id: str) -> None:
        """Move a stack up in the ordering (lower index = higher priority)."""
        if stack_id not in self._ordered_ids:
            return
        idx = self._ordered_ids.index(stack_id)
        if idx <= 0:
            return
        self._ordered_ids[idx], self._ordered_ids[idx - 1] = (
            self._ordered_ids[idx - 1],
            self._ordered_ids[idx],
        )
        self._update_order_buttons()
        self.selection_changed.emit()

    def move_stack_down(self, stack_id: str) -> None:
        """Move a stack down in the ordering (higher index = lower priority)."""
        if stack_id not in self._ordered_ids:
            return
        idx = self._ordered_ids.index(stack_id)
        if idx >= len(self._ordered_ids) - 1:
            return
        self._ordered_ids[idx], self._ordered_ids[idx + 1] = (
            self._ordered_ids[idx + 1],
            self._ordered_ids[idx],
        )
        self._update_order_buttons()
        self.selection_changed.emit()

    # -- Slots --------------------------------------------------------------

    def _on_card_toggled(self, stack_id: str, checked: bool) -> None:
        logger.debug("Stack %s toggled: %s", stack_id, checked)
        if checked:
            if stack_id not in self._ordered_ids:
                self._ordered_ids.append(stack_id)
        else:
            if stack_id in self._ordered_ids:
                self._ordered_ids.remove(stack_id)

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
        """Move the last selected stack up one position."""
        if len(self._ordered_ids) >= 2:
            # Move the last item up
            self.move_stack_up(self._ordered_ids[-1])

    def _on_move_down(self) -> None:
        """Move the first selected stack down one position."""
        if len(self._ordered_ids) >= 2:
            # Move the first item down
            self.move_stack_down(self._ordered_ids[0])
