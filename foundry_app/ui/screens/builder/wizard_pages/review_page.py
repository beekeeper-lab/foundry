"""Step 4: Review & Generate — summary, task depth choice, validation, generate."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class ReviewPage(QWidget):
    """Display composition summary, generation options, and validation results."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Composition Summary"))

        self.summary_browser = QTextBrowser()
        self.summary_browser.setOpenExternalLinks(False)
        layout.addWidget(self.summary_browser, stretch=2)

        # --- Generation options ---
        options_row = QHBoxLayout()

        # Task depth
        depth_group = QGroupBox("Task Depth")
        depth_layout = QVBoxLayout(depth_group)
        self._depth_group = QButtonGroup(self)
        self.radio_detailed = QRadioButton("Detailed (full wave: BA→Architect→Dev→QA)")
        self.radio_detailed.setChecked(True)
        self._depth_group.addButton(self.radio_detailed)
        depth_layout.addWidget(self.radio_detailed)
        self.radio_kickoff = QRadioButton("Kickoff (single Team Lead task)")
        self._depth_group.addButton(self.radio_kickoff)
        depth_layout.addWidget(self.radio_kickoff)
        options_row.addWidget(depth_group)

        # Other generation options
        gen_group = QGroupBox("Output Options")
        gen_layout = QVBoxLayout(gen_group)
        self.chk_seed_tasks = QCheckBox("Seed initial tasks")
        self.chk_seed_tasks.setChecked(True)
        gen_layout.addWidget(self.chk_seed_tasks)
        self.chk_write_manifest = QCheckBox("Write manifest.json")
        self.chk_write_manifest.setChecked(True)
        gen_layout.addWidget(self.chk_write_manifest)
        self.chk_write_diff_report = QCheckBox("Write diff report")
        gen_layout.addWidget(self.chk_write_diff_report)
        options_row.addWidget(gen_group)

        layout.addLayout(options_row)

        # --- Validation results ---
        self.validation_browser = QTextBrowser()
        self.validation_browser.setMaximumHeight(140)
        layout.addWidget(self.validation_browser)

    @property
    def seed_mode(self) -> str:
        return "kickoff" if self.radio_kickoff.isChecked() else "detailed"

    def set_summary(self, html: str) -> None:
        self.summary_browser.setHtml(html)

    def set_validation(self, html: str) -> None:
        self.validation_browser.setHtml(html)
