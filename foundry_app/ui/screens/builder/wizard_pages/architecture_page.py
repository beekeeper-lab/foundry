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

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Human-readable descriptions
# ---------------------------------------------------------------------------

PATTERN_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "monolith": (
        "Monolith",
        "Single deployable unit; simple to develop, test, and deploy",
    ),
    "modular-monolith": (
        "Modular Monolith",
        "Single deployment with clear module boundaries and internal APIs",
    ),
    "microservices": (
        "Microservices",
        "Independently deployable services communicating over the network",
    ),
    "serverless": (
        "Serverless",
        "Function-as-a-service with managed infrastructure and event triggers",
    ),
    "event-driven": (
        "Event-Driven",
        "Asynchronous messaging, event sourcing, and reactive architectures",
    ),
}

CLOUD_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "aws": (
        "Amazon Web Services",
        "EC2, Lambda, S3, RDS, DynamoDB, and the broader AWS ecosystem",
    ),
    "azure": (
        "Microsoft Azure",
        "App Service, Functions, Blob Storage, Cosmos DB, and Azure DevOps",
    ),
    "gcp": (
        "Google Cloud Platform",
        "Cloud Run, Cloud Functions, GCS, Firestore, and BigQuery",
    ),
    "self-hosted": (
        "Self-Hosted / On-Prem",
        "Docker, Kubernetes, bare-metal, or private cloud deployments",
    ),
}

# ---------------------------------------------------------------------------
# Stylesheet constants (Catppuccin Mocha theme)
# ---------------------------------------------------------------------------

CARD_STYLE = """
QFrame#arch-card {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 12px;
}
QFrame#arch-card:hover {
    border-color: #585b70;
}
"""

CARD_SELECTED_BORDER = "border-color: #a6e3a1;"

LABEL_STYLE = "color: #cdd6f4; font-size: 14px; font-weight: bold;"
DESC_STYLE = "color: #6c7086; font-size: 12px;"
HEADING_STYLE = "color: #cdd6f4; font-size: 18px; font-weight: bold;"
SUBHEADING_STYLE = "color: #6c7086; font-size: 13px;"
SECTION_LABEL_STYLE = "color: #89b4fa; font-size: 15px; font-weight: bold;"


# ---------------------------------------------------------------------------
# ArchitectureCard — single item row widget
# ---------------------------------------------------------------------------

class ArchitectureCard(QFrame):
    """A card representing a single architecture pattern or cloud provider."""

    toggled = Signal(str, bool)  # item_id, checked

    def __init__(
        self,
        item_id: str,
        display_name: str,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
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

    # -- State access -------------------------------------------------------

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

    # -- Slots --------------------------------------------------------------

    def _on_toggled(self, state: int) -> None:
        checked = state == Qt.CheckState.Checked.value
        self.toggled.emit(self._item_id, checked)
        if checked:
            self.setStyleSheet(CARD_STYLE + f"QFrame#arch-card {{ {CARD_SELECTED_BORDER} }}")
        else:
            self.setStyleSheet(CARD_STYLE)


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — wizard page widget
# ---------------------------------------------------------------------------

class ArchitectureCloudPage(QWidget):
    """Wizard page for selecting architecture patterns and cloud providers.

    This page is optional — ``is_valid()`` always returns True because
    users may skip architecture/cloud configuration entirely.

    Emits ``selection_changed`` whenever selections change.
    """

    selection_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pattern_cards: dict[str, ArchitectureCard] = {}
        self._cloud_cards: dict[str, ArchitectureCard] = {}
        self._build_ui()

    # -- UI construction ----------------------------------------------------

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

        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self._scroll_container = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_container)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(12)

        # Architecture patterns section
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

        # Cloud providers section
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

    # -- Public API ---------------------------------------------------------

    def get_architecture_config(self) -> ArchitectureConfig:
        """Return an ArchitectureConfig from current selections."""
        patterns = [
            ArchitecturePattern(pid)
            for pid, card in self._pattern_cards.items()
            if card.is_selected
        ]
        providers = [
            CloudProvider(cid)
            for cid, card in self._cloud_cards.items()
            if card.is_selected
        ]
        return ArchitectureConfig(patterns=patterns, cloud_providers=providers)

    def set_architecture_config(self, config: ArchitectureConfig) -> None:
        """Restore selections from an ArchitectureConfig (e.g. when navigating back)."""
        pattern_values = {p.value for p in config.patterns}
        for pid, card in self._pattern_cards.items():
            card.is_selected = pid in pattern_values

        provider_values = {c.value for c in config.cloud_providers}
        for cid, card in self._cloud_cards.items():
            card.is_selected = cid in provider_values

    def selected_pattern_count(self) -> int:
        """Return the number of selected architecture patterns."""
        return sum(1 for c in self._pattern_cards.values() if c.is_selected)

    def selected_cloud_count(self) -> int:
        """Return the number of selected cloud providers."""
        return sum(1 for c in self._cloud_cards.values() if c.is_selected)

    def is_valid(self) -> bool:
        """Always returns True — this page is optional."""
        return True

    @property
    def pattern_cards(self) -> dict[str, ArchitectureCard]:
        """Access pattern cards by id (for testing)."""
        return dict(self._pattern_cards)

    @property
    def cloud_cards(self) -> dict[str, ArchitectureCard]:
        """Access cloud cards by id (for testing)."""
        return dict(self._cloud_cards)

    # -- Slots --------------------------------------------------------------

    def _on_card_toggled(self, item_id: str, checked: bool) -> None:
        logger.debug("Architecture/cloud item %s toggled: %s", item_id, checked)
        self.selection_changed.emit()
