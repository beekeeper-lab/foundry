"""Wizard page 4 — Architecture & Cloud Configuration.

Displays architecture patterns and cloud providers as selectable cards.
This page is optional — users may skip it without selecting anything.
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
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    ArchitectureConfig,
    ArchitecturePattern,
    CloudProvider,
)
from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    ACCENT_SECONDARY,
    ACCENT_SECONDARY_MUTED,
    BG_SURFACE,
    BORDER_DEFAULT,
    FONT_SIZE_LG,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XL,
    FONT_WEIGHT_BOLD,
    RADIUS_MD,
    SPACE_MD,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

logger = logging.getLogger(__name__)

PATTERN_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "monolith": ("Monolith", "Single deployable unit; simple to develop, test, and deploy"),
    "modular-monolith": ("Modular Monolith", "Single deployment with clear module boundaries and internal APIs"),
    "microservices": ("Microservices", "Independently deployable services communicating over the network"),
    "serverless": ("Serverless", "Function-as-a-service with managed infrastructure and event triggers"),
    "event-driven": ("Event-Driven", "Asynchronous messaging, event sourcing, and reactive architectures"),
}

CLOUD_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "aws": ("Amazon Web Services", "EC2, Lambda, S3, RDS, DynamoDB, and the broader AWS ecosystem"),
    "azure": ("Microsoft Azure", "App Service, Functions, Blob Storage, Cosmos DB, and Azure DevOps"),
    "gcp": ("Google Cloud Platform", "Cloud Run, Cloud Functions, GCS, Firestore, and BigQuery"),
    "self-hosted": ("Self-Hosted / On-Prem", "Docker, Kubernetes, bare-metal, or private cloud deployments"),
}

CARD_STYLE = f"""
QFrame#arch-card {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD}px;
    padding: {SPACE_MD}px;
}}
QFrame#arch-card:hover {{
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
SECTION_LABEL_STYLE = (
    f"color: {ACCENT_SECONDARY}; font-size: {FONT_SIZE_LG}px; font-weight: {FONT_WEIGHT_BOLD};"
)


class ArchitectureCard(QFrame):
    """A card representing a single architecture pattern or cloud provider."""

    toggled = Signal(str, bool)

    def __init__(self, item_id: str, display_name: str, description: str,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._item_id = item_id
        self._display_name = display_name
        self._description = description
        self.setObjectName("arch-card")
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

        name_label = QLabel(self._display_name)
        name_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(name_label)

        desc_label = QLabel(f"— {self._description}" if self._description else "")
        desc_label.setStyleSheet(DESC_STYLE)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label, stretch=1)

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def is_selected(self) -> bool:
        return self._checkbox.isChecked()

    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        self._checkbox.setChecked(value)

    def _on_toggled(self, state: int) -> None:
        checked = state == Qt.CheckState.Checked.value
        self.toggled.emit(self._item_id, checked)
        if checked:
            self.setStyleSheet(CARD_STYLE + f"QFrame#arch-card {{ {CARD_SELECTED_BORDER} }}")
        else:
            self.setStyleSheet(CARD_STYLE)


class ArchitectureCloudPage(QWidget):
    """Wizard page for selecting architecture patterns and cloud providers."""

    selection_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pattern_cards: dict[str, ArchitectureCard] = {}
        self._cloud_cards: dict[str, ArchitectureCard] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)

        heading = QLabel("Architecture & Cloud")
        heading.setStyleSheet(HEADING_STYLE)
        outer.addWidget(heading)

        subtitle = QLabel(
            "Optionally select architecture patterns and cloud deployment targets. "
            "These guide the conventions and templates included in your project. "
            "You can skip this page if your project doesn't need architecture guidance."
        )
        subtitle.setStyleSheet(SUBHEADING_STYLE)
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self._scroll_container = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_container)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(12)

        pattern_label = QLabel("Architecture Patterns")
        pattern_label.setStyleSheet(SECTION_LABEL_STYLE)
        self._scroll_layout.addWidget(pattern_label)

        self._pattern_container = QVBoxLayout()
        self._pattern_container.setSpacing(8)
        self._scroll_layout.addLayout(self._pattern_container)

        for pattern in ArchitecturePattern:
            display_name, desc = PATTERN_DESCRIPTIONS.get(
                pattern.value, (pattern.value.replace("-", " ").title(), "")
            )
            card = ArchitectureCard(pattern.value, display_name, desc)
            card.toggled.connect(self._on_card_toggled)
            self._pattern_container.addWidget(card)
            self._pattern_cards[pattern.value] = card

        cloud_label = QLabel("Cloud Providers")
        cloud_label.setStyleSheet(SECTION_LABEL_STYLE)
        self._scroll_layout.addWidget(cloud_label)

        self._cloud_container = QVBoxLayout()
        self._cloud_container.setSpacing(8)
        self._scroll_layout.addLayout(self._cloud_container)

        for provider in CloudProvider:
            display_name, desc = CLOUD_DESCRIPTIONS.get(
                provider.value, (provider.value.replace("-", " ").title(), "")
            )
            card = ArchitectureCard(provider.value, display_name, desc)
            card.toggled.connect(self._on_card_toggled)
            self._cloud_container.addWidget(card)
            self._cloud_cards[provider.value] = card

        self._scroll_layout.addStretch(1)
        scroll.setWidget(self._scroll_container)
        outer.addWidget(scroll, stretch=1)

    def get_architecture_config(self) -> ArchitectureConfig:
        patterns = [
            ArchitecturePattern(pid) for pid, card in self._pattern_cards.items()
            if card.is_selected
        ]
        providers = [
            CloudProvider(cid) for cid, card in self._cloud_cards.items()
            if card.is_selected
        ]
        return ArchitectureConfig(patterns=patterns, cloud_providers=providers)

    def set_architecture_config(self, config: ArchitectureConfig) -> None:
        pattern_values = {p.value for p in config.patterns}
        for pid, card in self._pattern_cards.items():
            card.is_selected = pid in pattern_values
        provider_values = {c.value for c in config.cloud_providers}
        for cid, card in self._cloud_cards.items():
            card.is_selected = cid in provider_values

    def selected_pattern_count(self) -> int:
        return sum(1 for c in self._pattern_cards.values() if c.is_selected)

    def selected_cloud_count(self) -> int:
        return sum(1 for c in self._cloud_cards.values() if c.is_selected)

    def is_valid(self) -> bool:
        return True

    @property
    def pattern_cards(self) -> dict[str, ArchitectureCard]:
        return dict(self._pattern_cards)

    @property
    def cloud_cards(self) -> dict[str, ArchitectureCard]:
        return dict(self._cloud_cards)

    def _on_card_toggled(self, item_id: str, checked: bool) -> None:
        logger.debug("Architecture/cloud item %s toggled: %s", item_id, checked)
        self.selection_changed.emit()
