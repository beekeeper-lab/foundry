"""Wizard page 2 — Persona Selection.

Displays all personas from the library index with checkboxes for multi-select.
Each persona row shows name/role and expandable per-persona config options
(include agent, include templates, strictness level).
"""

from __future__ import annotations

import logging
from collections import defaultdict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGroupBox,
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
from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    ACCENT_SECONDARY_MUTED,
    BG_SURFACE,
    BORDER_DEFAULT,
    FONT_SIZE_LG,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XL,
    FONT_SIZE_XS,
    FONT_WEIGHT_BOLD,
    RADIUS_MD,
    SPACE_MD,
    STATUS_ERROR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Human-readable persona descriptions (keyed by directory id)
# ---------------------------------------------------------------------------

PERSONA_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "architect": ("Software Architect", "System design, ADRs, component boundaries"),
    "ba": ("Business Analyst", "Requirements, user stories, acceptance criteria"),
    "change-management": (
        "Change Management / Adoption Lead", "Organizational adoption and transition planning"
    ),
    "code-quality-reviewer": ("Code Quality Reviewer", "Code review and quality gates"),
    "compliance-risk": ("Compliance / Risk Analyst", "Compliance and risk management"),
    "customer-success": ("Customer Success Lead", "Customer onboarding, retention, satisfaction"),
    "data-analyst": ("Data Analyst", "KPI definition, dashboards, data-driven insights"),
    "data-engineer": ("Data Engineer", "Data pipelines, ETL, data infrastructure"),
    "database-administrator": ("Database Administrator", "Database design, tuning, maintenance"),
    "developer": ("Developer", "Implementation, features, bug fixes"),
    "devops-release": ("DevOps / Release Engineer", "CI/CD, deployment, release management"),
    "financial-operations": (
        "Financial Operations / Budget Officer", "Cost estimation, budgeting, financial governance"
    ),
    "integrator-merge-captain": (
        "Integrator / Merge Captain", "Git integration, merge coordination"
    ),
    "legal-counsel": ("Legal Counsel", "Contract review, IP protection, regulatory compliance"),
    "mobile-developer": ("Mobile Developer", "Mobile app development, cross-platform delivery"),
    "platform-sre-engineer": (
        "Platform SRE Engineer", "Reliability engineering, observability, incident response"
    ),
    "product-owner": ("Product Owner", "Product vision, backlog prioritization, stakeholder mgmt"),
    "researcher-librarian": ("Researcher / Librarian", "Research and library maintenance"),
    "sales-engineer": ("Sales Engineer", "Technical demos, proof-of-concept, sales support"),
    "security-engineer": ("Security Engineer", "Security review and threat modeling"),
    "team-lead": ("Team Lead", "Project orchestration, task decomposition"),
    "tech-qa": ("Tech QA / Test Engineer", "Test planning and quality assurance"),
    "technical-writer": ("Technical Writer", "Documentation and doc ownership"),
    "ux-ui-designer": ("UX / UI Designer", "UI/UX design and prototyping"),
}

# ---------------------------------------------------------------------------
# Stylesheet constants (theme-based)
# ---------------------------------------------------------------------------

CARD_STYLE = f"""
QFrame#persona-card {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD}px;
    padding: {SPACE_MD}px;
}}
QFrame#persona-card:hover {{
    border-color: {ACCENT_SECONDARY_MUTED};
}}
"""

CARD_SELECTED_BORDER = f"border-color: {ACCENT_PRIMARY};"

LABEL_STYLE = (
    f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px; font-weight: {FONT_WEIGHT_BOLD};"
)
DESC_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
CONFIG_LABEL_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
HEADING_STYLE = (
    f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_XL}px; font-weight: {FONT_WEIGHT_BOLD};"
)
SUBHEADING_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
WARNING_STYLE = f"color: {STATUS_ERROR}; font-size: {FONT_SIZE_SM}px;"
TEMPLATES_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_XS}px; font-style: italic;"

CATEGORY_GROUP_STYLE = f"""
QGroupBox {{
    font-size: {FONT_SIZE_LG}px;
    font-weight: {FONT_WEIGHT_BOLD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD}px;
    margin-top: 12px;
    padding-top: 24px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
}}
"""


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
        self._category_groups: dict[str, QGroupBox] = {}
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
        """Populate the page with personas from a LibraryIndex, grouped by category."""
        # Clear existing cards and group boxes
        for card in self._cards.values():
            card.deleteLater()
        self._cards.clear()

        for group_box in self._category_groups.values():
            self._card_layout.removeWidget(group_box)
            group_box.deleteLater()
        self._category_groups.clear()

        # Group personas by category
        groups: dict[str, list[PersonaInfo]] = defaultdict(list)
        for persona in library_index.personas:
            cat = persona.category.strip() if persona.category else ""
            if not cat:
                cat = "Other"
            groups[cat].append(persona)

        # Sort category names alphabetically, with "Other" always last
        sorted_cats = sorted(
            groups.keys(), key=lambda c: (c == "Other", c)
        )

        insert_idx = 0
        for cat_name in sorted_cats:
            personas_in_cat = groups[cat_name]
            group_box = QGroupBox(f"{cat_name} ({len(personas_in_cat)})")
            group_box.setCheckable(False)
            group_box.setStyleSheet(CATEGORY_GROUP_STYLE)
            group_layout = QVBoxLayout()
            group_layout.setContentsMargins(8, 8, 8, 8)
            group_layout.setSpacing(8)

            for persona in personas_in_cat:
                card = PersonaCard(persona)
                card.toggled.connect(self._on_card_toggled)
                group_layout.addWidget(card)
                self._cards[persona.id] = card

            group_box.setLayout(group_layout)
            self._card_layout.insertWidget(insert_idx, group_box)
            self._category_groups[cat_name] = group_box
            insert_idx += 1

        self._empty_label.setVisible(len(self._cards) == 0)
        logger.info("Loaded %d persona cards in %d categories",
                     len(self._cards), len(self._category_groups))

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

    @property
    def category_groups(self) -> dict[str, QGroupBox]:
        """Access category group boxes by name (for testing)."""
        return dict(self._category_groups)

    # -- Slots --------------------------------------------------------------

    def _on_card_toggled(self, persona_id: str, checked: bool) -> None:
        logger.debug("Persona %s toggled: %s", persona_id, checked)
        self._update_warning()
        self.selection_changed.emit()

    def _update_warning(self) -> None:
        if self._warning_label is not None:
            self._warning_label.setVisible(not self.is_valid())
