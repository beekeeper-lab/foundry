"""Wizard page 2 — Persona Selection.

Displays all personas from the library index with checkboxes for multi-select.
Each persona row shows name/role and expandable per-persona config options
(include agent, include templates, strictness level).
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    Strictness,
    TeamConfig,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Human-readable persona descriptions (keyed by directory id)
# ---------------------------------------------------------------------------

PERSONA_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "architect": ("Software Architect", "System design, ADRs, component boundaries"),
    "ba": ("Business Analyst", "Requirements, user stories, acceptance criteria"),
    "code-quality-reviewer": ("Code Quality Reviewer", "Code review and quality gates"),
    "compliance-risk": ("Compliance / Risk Analyst", "Compliance and risk management"),
    "developer": ("Developer", "Implementation, features, bug fixes"),
    "devops-release": ("DevOps / Release Engineer", "CI/CD, deployment, release management"),
    "integrator-merge-captain": (
        "Integrator / Merge Captain", "Git integration, merge coordination"
    ),
    "researcher-librarian": ("Researcher / Librarian", "Research and library maintenance"),
    "security-engineer": ("Security Engineer", "Security review and threat modeling"),
    "team-lead": ("Team Lead", "Project orchestration, task decomposition"),
    "tech-qa": ("Tech QA / Test Engineer", "Test planning and quality assurance"),
    "technical-writer": ("Technical Writer", "Documentation and doc ownership"),
    "ux-ui-designer": ("UX / UI Designer", "UI/UX design and prototyping"),
}

# ---------------------------------------------------------------------------
# Stylesheet constants
# ---------------------------------------------------------------------------

CARD_STYLE = """
QFrame#persona-card {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 12px;
}
QFrame#persona-card:hover {
    border-color: #585b70;
}
"""

CARD_SELECTED_BORDER = "border-color: #cba6f7;"

LABEL_STYLE = "color: #cdd6f4; font-size: 14px; font-weight: bold;"
DESC_STYLE = "color: #6c7086; font-size: 12px;"
CONFIG_LABEL_STYLE = "color: #a6adc8; font-size: 12px;"
HEADING_STYLE = "color: #cdd6f4; font-size: 18px; font-weight: bold;"
SUBHEADING_STYLE = "color: #6c7086; font-size: 13px;"
WARNING_STYLE = "color: #f38ba8; font-size: 12px;"
TEMPLATES_STYLE = "color: #a6adc8; font-size: 11px; font-style: italic;"


# ---------------------------------------------------------------------------
# PersonaCard — single persona row widget
# ---------------------------------------------------------------------------

class PersonaCard(QFrame):
    """A card representing a single persona with checkbox and config options."""

    toggled = Signal(str, bool)  # persona_id, checked

    def __init__(self, persona: PersonaInfo, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._persona = persona
        self.setObjectName("persona-card")
        self.setStyleSheet(CARD_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # --- Top row: checkbox + name + role ---
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self._checkbox = QCheckBox()
        self._checkbox.stateChanged.connect(self._on_toggled)
        top_row.addWidget(self._checkbox)

        display_name, role_desc = PERSONA_DESCRIPTIONS.get(
            self._persona.id, (self._persona.id.replace("-", " ").title(), "")
        )

        name_label = QLabel(display_name)
        name_label.setStyleSheet(LABEL_STYLE)
        top_row.addWidget(name_label)

        role_label = QLabel(f"— {role_desc}" if role_desc else "")
        role_label.setStyleSheet(DESC_STYLE)
        top_row.addWidget(role_label, stretch=1)

        # Template count badge
        tmpl_count = len(self._persona.templates)
        if tmpl_count > 0:
            badge = QLabel(f"{tmpl_count} template{'s' if tmpl_count != 1 else ''}")
            badge.setStyleSheet(TEMPLATES_STYLE)
            top_row.addWidget(badge)

        layout.addLayout(top_row)

        # --- Config row (agent, templates, strictness) ---
        config_row = QHBoxLayout()
        config_row.setSpacing(16)
        config_row.setContentsMargins(28, 0, 0, 0)  # indent under checkbox

        agent_label = QLabel("Agent file:")
        agent_label.setStyleSheet(CONFIG_LABEL_STYLE)
        self._agent_check = QCheckBox()
        self._agent_check.setChecked(True)
        config_row.addWidget(agent_label)
        config_row.addWidget(self._agent_check)

        templates_label = QLabel("Templates:")
        templates_label.setStyleSheet(CONFIG_LABEL_STYLE)
        self._templates_check = QCheckBox()
        self._templates_check.setChecked(True)
        config_row.addWidget(templates_label)
        config_row.addWidget(self._templates_check)

        strictness_label = QLabel("Strictness:")
        strictness_label.setStyleSheet(CONFIG_LABEL_STYLE)
        self._strictness_combo = QComboBox()
        self._strictness_combo.addItems(["light", "standard", "strict"])
        self._strictness_combo.setCurrentText("standard")
        self._strictness_combo.setFixedWidth(100)
        config_row.addWidget(strictness_label)
        config_row.addWidget(self._strictness_combo)

        config_row.addStretch(1)
        layout.addLayout(config_row)

    # -- State access -------------------------------------------------------

    @property
    def persona_id(self) -> str:
        return self._persona.id

    @property
    def is_selected(self) -> bool:
        return self._checkbox.isChecked()

    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        self._checkbox.setChecked(value)

    def to_persona_selection(self) -> PersonaSelection:
        """Build a PersonaSelection from the current card state."""
        return PersonaSelection(
            id=self._persona.id,
            include_agent=self._agent_check.isChecked(),
            include_templates=self._templates_check.isChecked(),
            strictness=Strictness(self._strictness_combo.currentText()),
        )

    def load_from_selection(self, sel: PersonaSelection) -> None:
        """Restore card state from a PersonaSelection."""
        self._checkbox.setChecked(True)
        self._agent_check.setChecked(sel.include_agent)
        self._templates_check.setChecked(sel.include_templates)
        self._strictness_combo.setCurrentText(sel.strictness.value)

    # -- Slots --------------------------------------------------------------

    def _on_toggled(self, state: int) -> None:
        checked = state == Qt.CheckState.Checked.value
        self.toggled.emit(self._persona.id, checked)
        # Visual feedback — highlight border when selected
        if checked:
            self.setStyleSheet(CARD_STYLE + f"QFrame#persona-card {{ {CARD_SELECTED_BORDER} }}")
        else:
            self.setStyleSheet(CARD_STYLE)


# ---------------------------------------------------------------------------
# PersonaSelectionPage — wizard page widget
# ---------------------------------------------------------------------------

class PersonaSelectionPage(QWidget):
    """Wizard page for selecting team personas from the library.

    Emits ``selection_changed`` whenever the set of selected personas changes.
    Call ``get_team_config()`` to retrieve the current selections as a TeamConfig.
    """

    selection_changed = Signal()

    def __init__(
        self,
        library_index: LibraryIndex | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cards: dict[str, PersonaCard] = {}
        self._warning_label: QLabel | None = None
        self._build_ui()
        if library_index is not None:
            self.load_personas(library_index)

    # -- UI construction ----------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)

        heading = QLabel("Select Team Personas")
        heading.setStyleSheet(HEADING_STYLE)
        outer.addWidget(heading)

        subtitle = QLabel(
            "Choose which AI team members to include in your project. "
            "Each persona brings specialised skills and outputs."
        )
        subtitle.setStyleSheet(SUBHEADING_STYLE)
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        # Warning label (hidden by default)
        self._warning_label = QLabel("At least one persona must be selected.")
        self._warning_label.setStyleSheet(WARNING_STYLE)
        self._warning_label.setVisible(False)
        outer.addWidget(self._warning_label)

        # Scrollable area for persona cards
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

    def load_personas(self, library_index: LibraryIndex) -> None:
        """Populate the page with personas from a LibraryIndex."""
        # Clear existing cards
        for card in self._cards.values():
            self._card_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        # Insert cards before the stretch
        insert_idx = 0
        for persona in library_index.personas:
            card = PersonaCard(persona)
            card.toggled.connect(self._on_card_toggled)
            self._card_layout.insertWidget(insert_idx, card)
            self._cards[persona.id] = card
            insert_idx += 1

        logger.info("Loaded %d persona cards", len(self._cards))

    def get_team_config(self) -> TeamConfig:
        """Return a TeamConfig from currently selected personas."""
        selections = [
            card.to_persona_selection()
            for card in self._cards.values()
            if card.is_selected
        ]
        return TeamConfig(personas=selections)

    def set_team_config(self, config: TeamConfig) -> None:
        """Restore selections from a TeamConfig (e.g. when navigating back)."""
        selected_ids = {p.id for p in config.personas}
        selection_map = {p.id: p for p in config.personas}

        for pid, card in self._cards.items():
            if pid in selected_ids:
                card.load_from_selection(selection_map[pid])
            else:
                card.is_selected = False

        self._update_warning()

    def selected_count(self) -> int:
        """Return the number of currently selected personas."""
        return sum(1 for c in self._cards.values() if c.is_selected)

    def is_valid(self) -> bool:
        """Return True if at least one persona is selected."""
        return self.selected_count() > 0

    @property
    def persona_cards(self) -> dict[str, PersonaCard]:
        """Access cards by persona id (for testing)."""
        return dict(self._cards)

    # -- Slots --------------------------------------------------------------

    def _on_card_toggled(self, persona_id: str, checked: bool) -> None:
        logger.debug("Persona %s toggled: %s", persona_id, checked)
        self._update_warning()
        self.selection_changed.emit()

    def _update_warning(self) -> None:
        if self._warning_label is not None:
            self._warning_label.setVisible(not self.is_valid())
