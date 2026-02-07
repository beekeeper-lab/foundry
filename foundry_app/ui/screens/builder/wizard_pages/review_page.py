"""Wizard page 6 — Review & Generate.

Displays a read-only summary of the full CompositionSpec so the user can
verify all selections before triggering project generation.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    CompositionSpec,
    Strictness,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stylesheet constants (Catppuccin Mocha theme)
# ---------------------------------------------------------------------------

PAGE_STYLE = """
QWidget#review-page {
    background-color: transparent;
}
"""

SECTION_STYLE = """
QFrame#review-section {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 16px;
}
"""

SECTION_TITLE_STYLE = "color: #89b4fa; font-size: 15px; font-weight: bold;"
HEADING_STYLE = "color: #cdd6f4; font-size: 22px; font-weight: bold;"
SUBHEADING_STYLE = "color: #6c7086; font-size: 13px;"
LABEL_STYLE = "color: #a6adc8; font-size: 13px;"
VALUE_STYLE = "color: #cdd6f4; font-size: 13px; font-weight: bold;"
ITEM_STYLE = "color: #cdd6f4; font-size: 13px;"
BADGE_STYLE = "color: #a6adc8; font-size: 11px; font-style: italic;"
EMPTY_STYLE = "color: #585b70; font-size: 13px; font-style: italic;"
GENERATE_BTN_STYLE = """
QPushButton#generate-btn {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton#generate-btn:hover {
    background-color: #b4d0fb;
}
QPushButton#generate-btn:pressed {
    background-color: #74a8fc;
}
"""


# ---------------------------------------------------------------------------
# ReviewSection — a collapsible section with a title and content area
# ---------------------------------------------------------------------------

class ReviewSection(QFrame):
    """A titled section card for displaying a group of review items."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("review-section")
        self.setStyleSheet(SECTION_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 12)
        self._layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet(SECTION_TITLE_STYLE)
        self._layout.addWidget(title_label)

        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 4, 0, 0)
        self._content_layout.setSpacing(4)
        self._layout.addLayout(self._content_layout)

    @property
    def content_layout(self) -> QVBoxLayout:
        """Access the content area layout for adding widgets."""
        return self._content_layout

    def add_field(self, label: str, value: str) -> QLabel:
        """Add a label: value pair to the section."""
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(f"{label}:")
        lbl.setStyleSheet(LABEL_STYLE)
        lbl.setFixedWidth(140)
        row.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(VALUE_STYLE)
        val.setWordWrap(True)
        val.setObjectName(f"value-{label.lower().replace(' ', '-')}")
        row.addWidget(val, stretch=1)

        self._content_layout.addLayout(row)
        return val

    def add_item(self, text: str) -> QLabel:
        """Add a single text item to the section."""
        item = QLabel(text)
        item.setStyleSheet(ITEM_STYLE)
        item.setWordWrap(True)
        self._content_layout.addWidget(item)
        return item

    def add_empty_message(self, text: str) -> QLabel:
        """Add an 'empty' placeholder message."""
        msg = QLabel(text)
        msg.setStyleSheet(EMPTY_STYLE)
        self._content_layout.addWidget(msg)
        return msg


# ---------------------------------------------------------------------------
# ReviewPage — the wizard page widget
# ---------------------------------------------------------------------------

class ReviewPage(QWidget):
    """Wizard page for reviewing the full composition spec before generation.

    Emits ``generate_requested`` when the user clicks the Generate button.
    """

    generate_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("review-page")
        self.setStyleSheet(PAGE_STYLE)

        self._sections: dict[str, ReviewSection] = {}
        self._spec: CompositionSpec | None = None
        self._build_ui()

    # -- UI construction ----------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)

        heading = QLabel("Review & Generate")
        heading.setStyleSheet(HEADING_STYLE)
        outer.addWidget(heading)

        subtitle = QLabel(
            "Review your project configuration below. "
            "When everything looks good, click Generate to create your project."
        )
        subtitle.setStyleSheet(SUBHEADING_STYLE)
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        # Scrollable area for review sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background-color: transparent; border: none; }"
        )

        self._scroll_container = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_container)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(12)
        self._scroll_layout.addStretch(1)

        scroll.setWidget(self._scroll_container)
        outer.addWidget(scroll, stretch=1)

        # Generate button
        self._generate_btn = QPushButton("Generate Project")
        self._generate_btn.setObjectName("generate-btn")
        self._generate_btn.setStyleSheet(GENERATE_BTN_STYLE)
        self._generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._generate_btn.clicked.connect(self._on_generate_clicked)
        outer.addWidget(self._generate_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    # -- Public API ---------------------------------------------------------

    def set_composition_spec(self, spec: CompositionSpec) -> None:
        """Populate all review sections from a CompositionSpec."""
        self._spec = spec
        self._clear_sections()
        self._build_project_section(spec)
        self._build_team_section(spec)
        self._build_stacks_section(spec)
        self._build_architecture_section(spec)
        self._build_hooks_section(spec)
        self._build_generation_section(spec)
        if spec.safety is not None:
            self._build_safety_section(spec)
        logger.info("Review page populated from CompositionSpec")

    def get_composition_spec(self) -> CompositionSpec | None:
        """Return the currently displayed CompositionSpec, or None."""
        return self._spec

    def is_complete(self) -> bool:
        """Review page is always complete — user can always proceed."""
        return True

    @property
    def sections(self) -> dict[str, ReviewSection]:
        """Access sections by name (for testing)."""
        return dict(self._sections)

    # -- Section builders ---------------------------------------------------

    def _build_project_section(self, spec: CompositionSpec) -> None:
        section = self._add_section("project", "Project Identity")
        section.add_field("Name", spec.project.name)
        section.add_field("Slug", spec.project.slug)
        section.add_field("Output Path", spec.project.resolved_output_folder)

    def _build_team_section(self, spec: CompositionSpec) -> None:
        section = self._add_section("team", "Team Composition")
        personas = spec.team.personas
        if not personas:
            section.add_empty_message("No personas selected")
            return
        for p in personas:
            parts = [p.id]
            if not p.include_agent:
                parts.append("no agent")
            if not p.include_templates:
                parts.append("no templates")
            if p.strictness != Strictness.STANDARD:
                parts.append(p.strictness.value)
            text = parts[0]
            if len(parts) > 1:
                text += f"  ({', '.join(parts[1:])})"
            section.add_item(f"\u2022 {text}")

    def _build_stacks_section(self, spec: CompositionSpec) -> None:
        section = self._add_section("stacks", "Technology Stacks")
        stacks = sorted(spec.stacks, key=lambda s: s.order)
        if not stacks:
            section.add_empty_message("No stacks selected")
            return
        for idx, s in enumerate(stacks):
            section.add_item(f"{idx + 1}. {s.id}")

    def _build_architecture_section(self, spec: CompositionSpec) -> None:
        section = self._add_section("architecture", "Architecture & Cloud")
        arch = spec.architecture
        if not arch.patterns and not arch.cloud_providers:
            section.add_empty_message("No architecture or cloud selections")
            return
        if arch.patterns:
            names = ", ".join(p.value for p in arch.patterns)
            section.add_field("Patterns", names)
        if arch.cloud_providers:
            names = ", ".join(c.value for c in arch.cloud_providers)
            section.add_field("Cloud Providers", names)

    def _build_hooks_section(self, spec: CompositionSpec) -> None:
        section = self._add_section("hooks", "Hooks & Safety Posture")
        section.add_field("Posture", spec.hooks.posture.value.title())
        packs = spec.hooks.packs
        if packs:
            enabled = [p for p in packs if p.enabled]
            disabled = [p for p in packs if not p.enabled]
            if enabled:
                ids = ", ".join(p.id for p in enabled)
                section.add_field("Enabled Packs", ids)
            if disabled:
                ids = ", ".join(p.id for p in disabled)
                section.add_field("Disabled Packs", ids)
        else:
            section.add_field("Hook Packs", "None")

    def _build_generation_section(self, spec: CompositionSpec) -> None:
        section = self._add_section("generation", "Generation Options")
        gen = spec.generation
        section.add_field("Seed Tasks", "Yes" if gen.seed_tasks else "No")
        if gen.seed_tasks:
            section.add_field("Seed Mode", gen.seed_mode.value.title())
        section.add_field("Write Manifest", "Yes" if gen.write_manifest else "No")
        section.add_field("Diff Report", "Yes" if gen.write_diff_report else "No")

    def _build_safety_section(self, spec: CompositionSpec) -> None:
        if spec.safety is None:
            return
        section = self._add_section("safety", "Safety Configuration")
        safety = spec.safety
        section.add_field("Git Push", "Allowed" if safety.git.allow_push else "Blocked")
        section.add_field(
            "Force Push", "Allowed" if safety.git.allow_force_push else "Blocked"
        )
        section.add_field("Shell Access", "Allowed" if safety.shell.allow_shell else "Blocked")
        section.add_field(
            "File Delete", "Allowed" if safety.filesystem.allow_delete else "Blocked"
        )
        section.add_field(
            "Network Access", "Allowed" if safety.network.allow_network else "Blocked"
        )
        section.add_field(
            "Secret Scanning", "Enabled" if safety.secrets.scan_for_secrets else "Disabled"
        )

    # -- Helpers ------------------------------------------------------------

    def _add_section(self, key: str, title: str) -> ReviewSection:
        """Create a ReviewSection and insert before the stretch."""
        section = ReviewSection(title, self._scroll_container)
        insert_idx = self._scroll_layout.count() - 1  # before the stretch
        self._scroll_layout.insertWidget(insert_idx, section)
        self._sections[key] = section
        return section

    def _clear_sections(self) -> None:
        """Remove all existing review sections."""
        for section in self._sections.values():
            self._scroll_layout.removeWidget(section)
            section.deleteLater()
        self._sections.clear()

    # -- Slots --------------------------------------------------------------

    def _on_generate_clicked(self) -> None:
        logger.info("Generate button clicked")
        self.generate_requested.emit()
