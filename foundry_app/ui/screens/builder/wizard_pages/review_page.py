"""Wizard page 5 — Review & Generate.

Displays a read-only summary of the full CompositionSpec, runs pre-generation
validation, and provides a Generate button gated on validation success.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Signal
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
    LibraryIndex,
    Severity,
    ValidationResult,
)
from foundry_app.services.validator import run_pre_generation_validation

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stylesheet constants (Catppuccin Mocha theme)
# ---------------------------------------------------------------------------

HEADING_STYLE = "color: #cdd6f4; font-size: 18px; font-weight: bold;"
SUBHEADING_STYLE = "color: #6c7086; font-size: 13px;"
SECTION_TITLE_STYLE = "color: #cdd6f4; font-size: 15px; font-weight: bold;"
LABEL_STYLE = "color: #a6adc8; font-size: 13px;"
VALUE_STYLE = "color: #cdd6f4; font-size: 13px;"
ITEM_STYLE = "color: #cdd6f4; font-size: 12px;"

ERROR_STYLE = "color: #f38ba8; font-size: 12px;"
WARNING_STYLE = "color: #fab387; font-size: 12px;"
INFO_STYLE = "color: #89b4fa; font-size: 12px;"
SUCCESS_STYLE = "color: #a6e3a1; font-size: 13px; font-weight: bold;"

SECTION_FRAME_STYLE = """
QFrame#review-section {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 12px;
}
"""

GENERATE_BTN_STYLE = """
QPushButton#generate-btn {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-size: 15px;
    font-weight: bold;
}
QPushButton#generate-btn:hover {
    background-color: #94e2d5;
}
QPushButton#generate-btn:disabled {
    background-color: #45475a;
    color: #585b70;
}
"""

SEVERITY_STYLES: dict[Severity, str] = {
    Severity.ERROR: ERROR_STYLE,
    Severity.WARNING: WARNING_STYLE,
    Severity.INFO: INFO_STYLE,
}

SEVERITY_ICONS: dict[Severity, str] = {
    Severity.ERROR: "\u2718",  # ✘
    Severity.WARNING: "\u26a0",  # ⚠
    Severity.INFO: "\u2139",  # ℹ
}


# ---------------------------------------------------------------------------
# ReviewPage — wizard page widget
# ---------------------------------------------------------------------------

class ReviewPage(QWidget):
    """Wizard page for reviewing the composition spec before generation.

    Displays a read-only summary of all wizard selections, runs validation,
    and provides a Generate button gated on validation success.

    Emits ``generate_requested`` when the user clicks Generate.
    """

    generate_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._spec: CompositionSpec | None = None
        self._library_index: LibraryIndex | None = None
        self._validation_result: ValidationResult | None = None
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
            "Fix any validation errors before generating."
        )
        subtitle.setStyleSheet(SUBHEADING_STYLE)
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(12)

        # Placeholder sections — rebuilt on each load
        self._project_section = self._make_section("Project")
        self._content_layout.addWidget(self._project_section)

        self._personas_section = self._make_section("Personas")
        self._content_layout.addWidget(self._personas_section)

        self._stacks_section = self._make_section("Technology Stacks")
        self._content_layout.addWidget(self._stacks_section)

        self._hooks_section = self._make_section("Hooks & Safety")
        self._content_layout.addWidget(self._hooks_section)

        self._validation_section = self._make_section("Validation")
        self._content_layout.addWidget(self._validation_section)

        self._content_layout.addStretch(1)

        scroll.setWidget(self._content_widget)
        outer.addWidget(scroll, stretch=1)

        # Generate button
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        self._generate_btn = QPushButton("Generate Project")
        self._generate_btn.setObjectName("generate-btn")
        self._generate_btn.setStyleSheet(GENERATE_BTN_STYLE)
        self._generate_btn.setEnabled(False)
        self._generate_btn.clicked.connect(self._on_generate_clicked)
        btn_row.addWidget(self._generate_btn)

        btn_row.addStretch(1)
        outer.addLayout(btn_row)

    @staticmethod
    def _make_section(title: str) -> QFrame:
        """Create a styled section frame with a title label."""
        frame = QFrame()
        frame.setObjectName("review-section")
        frame.setStyleSheet(SECTION_FRAME_STYLE)
        frame.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet(SECTION_TITLE_STYLE)
        title_label.setObjectName("section-title")
        layout.addWidget(title_label)

        return frame

    # -- Public API ---------------------------------------------------------

    def load_spec(
        self,
        spec: CompositionSpec,
        library_index: LibraryIndex,
    ) -> None:
        """Load a composition spec and library index, then refresh the display."""
        self._spec = spec
        self._library_index = library_index
        self._refresh_summary()
        self._run_validation()

    @property
    def spec(self) -> CompositionSpec | None:
        """The currently loaded composition spec."""
        return self._spec

    @property
    def library_index(self) -> LibraryIndex | None:
        """The currently loaded library index."""
        return self._library_index

    @property
    def validation_result(self) -> ValidationResult | None:
        """The most recent validation result."""
        return self._validation_result

    @property
    def generate_button(self) -> QPushButton:
        """Access the generate button (for testing)."""
        return self._generate_btn

    def is_valid(self) -> bool:
        """Return True if validation passed (no errors)."""
        if self._validation_result is None:
            return False
        return self._validation_result.is_valid

    @property
    def project_section(self) -> QFrame:
        """Access the project section frame (for testing)."""
        return self._project_section

    @property
    def personas_section(self) -> QFrame:
        """Access the personas section frame (for testing)."""
        return self._personas_section

    @property
    def stacks_section(self) -> QFrame:
        """Access the stacks section frame (for testing)."""
        return self._stacks_section

    @property
    def hooks_section(self) -> QFrame:
        """Access the hooks section frame (for testing)."""
        return self._hooks_section

    @property
    def validation_section(self) -> QFrame:
        """Access the validation section frame (for testing)."""
        return self._validation_section

    # -- Display refresh ----------------------------------------------------

    def _refresh_summary(self) -> None:
        """Rebuild all summary sections from the current spec."""
        if self._spec is None:
            return

        self._refresh_project_section()
        self._refresh_personas_section()
        self._refresh_stacks_section()
        self._refresh_hooks_section()

    def _clear_section_content(self, section: QFrame) -> None:
        """Remove all widgets from a section except the title label."""
        layout = section.layout()
        if layout is None:
            return
        # Remove all items except the first (title label)
        while layout.count() > 1:
            item = layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _add_field(self, section: QFrame, label: str, value: str) -> QLabel:
        """Add a label: value row to a section. Returns the value label."""
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(f"{label}:")
        lbl.setStyleSheet(LABEL_STYLE)
        row.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(VALUE_STYLE)
        val.setWordWrap(True)
        row.addWidget(val, stretch=1)

        container = QWidget()
        container.setLayout(row)
        section.layout().addWidget(container)
        return val

    def _add_item(self, section: QFrame, text: str) -> QLabel:
        """Add a bullet-point item to a section."""
        item = QLabel(f"  \u2022 {text}")
        item.setStyleSheet(ITEM_STYLE)
        item.setWordWrap(True)
        section.layout().addWidget(item)
        return item

    def _refresh_project_section(self) -> None:
        """Rebuild the project identity summary."""
        self._clear_section_content(self._project_section)
        if self._spec is None:
            return

        proj = self._spec.project
        self._add_field(self._project_section, "Name", proj.name)
        self._add_field(self._project_section, "Slug", proj.slug)
        self._add_field(
            self._project_section, "Output",
            f"{proj.output_root}/{proj.resolved_output_folder}",
        )

    def _refresh_personas_section(self) -> None:
        """Rebuild the personas summary."""
        self._clear_section_content(self._personas_section)
        if self._spec is None:
            return

        personas = self._spec.team.personas
        if not personas:
            self._add_item(self._personas_section, "No personas selected")
            return

        count_label = QLabel(f"{len(personas)} persona{'s' if len(personas) != 1 else ''}")
        count_label.setStyleSheet(LABEL_STYLE)
        self._personas_section.layout().addWidget(count_label)

        for ps in personas:
            parts = [ps.id]
            if not ps.include_agent:
                parts.append("no agent")
            if not ps.include_templates:
                parts.append("no templates")
            if ps.strictness.value != "standard":
                parts.append(ps.strictness.value)
            self._add_item(self._personas_section, " | ".join(parts))

    def _refresh_stacks_section(self) -> None:
        """Rebuild the stacks summary."""
        self._clear_section_content(self._stacks_section)
        if self._spec is None:
            return

        stacks = sorted(self._spec.stacks, key=lambda s: s.order)
        if not stacks:
            self._add_item(self._stacks_section, "No stacks selected")
            return

        count_label = QLabel(f"{len(stacks)} stack{'s' if len(stacks) != 1 else ''}")
        count_label.setStyleSheet(LABEL_STYLE)
        self._stacks_section.layout().addWidget(count_label)

        for idx, ss in enumerate(stacks):
            self._add_item(self._stacks_section, f"{idx + 1}. {ss.id}")

    def _refresh_hooks_section(self) -> None:
        """Rebuild the hooks/safety summary."""
        self._clear_section_content(self._hooks_section)
        if self._spec is None:
            return

        hooks = self._spec.hooks
        self._add_field(self._hooks_section, "Posture", hooks.posture.value)

        if hooks.packs:
            for hp in hooks.packs:
                mode_str = f" ({hp.mode.value})" if hp.enabled else " (disabled)"
                self._add_item(self._hooks_section, f"{hp.id}{mode_str}")
        else:
            self._add_item(self._hooks_section, "No hook packs selected")

    # -- Validation ---------------------------------------------------------

    def _run_validation(self) -> None:
        """Run pre-generation validation and update the display."""
        if self._spec is None or self._library_index is None:
            self._validation_result = None
            self._generate_btn.setEnabled(False)
            return

        self._validation_result = run_pre_generation_validation(
            self._spec, self._library_index,
        )
        self._refresh_validation_section()
        self._generate_btn.setEnabled(self._validation_result.is_valid)

    def _refresh_validation_section(self) -> None:
        """Rebuild the validation results display."""
        self._clear_section_content(self._validation_section)

        if self._validation_result is None:
            self._add_item(self._validation_section, "No validation results")
            return

        result = self._validation_result

        if not result.messages:
            ok_label = QLabel("\u2714 All checks passed")
            ok_label.setStyleSheet(SUCCESS_STYLE)
            ok_label.setObjectName("validation-ok")
            self._validation_section.layout().addWidget(ok_label)
        else:
            for msg in result.messages:
                icon = SEVERITY_ICONS.get(msg.severity, "")
                style = SEVERITY_STYLES.get(msg.severity, INFO_STYLE)
                msg_label = QLabel(f"{icon} [{msg.code}] {msg.message}")
                msg_label.setStyleSheet(style)
                msg_label.setWordWrap(True)
                msg_label.setObjectName(f"validation-{msg.severity.value}")
                self._validation_section.layout().addWidget(msg_label)

        # Summary line
        n_err = len(result.errors)
        n_warn = len(result.warnings)
        n_info = len(result.infos)
        summary = f"{n_err} error{'s' if n_err != 1 else ''}, "
        summary += f"{n_warn} warning{'s' if n_warn != 1 else ''}, "
        summary += f"{n_info} info"
        summary_label = QLabel(summary)
        summary_label.setStyleSheet(LABEL_STYLE)
        summary_label.setObjectName("validation-summary")
        self._validation_section.layout().addWidget(summary_label)

    # -- Slots --------------------------------------------------------------

    def _on_generate_clicked(self) -> None:
        logger.info("Generate requested")
        self.generate_requested.emit()
