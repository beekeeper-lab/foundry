"""Generation progress screen — displays real-time pipeline stage progress."""

from __future__ import annotations

import logging
import time

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_PRIMARY_MUTED,
    ACCENT_SECONDARY,
    BG_BASE,
    BG_INSET,
    BG_SURFACE,
    BORDER_DEFAULT,
    BORDER_SUBTLE,
    FONT_SIZE_LG,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XL,
    FONT_WEIGHT_BOLD,
    RADIUS_MD,
    RADIUS_SM,
    SPACE_LG,
    SPACE_MD,
    SPACE_SM,
    SPACE_XL,
    SPACE_XS,
    SPACE_XXL,
    STATUS_ERROR,
    STATUS_SUCCESS,
    TEXT_ON_ACCENT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from foundry_app.ui.widgets.spinner_widget import SpinnerWidget

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pipeline stage names
# ---------------------------------------------------------------------------

PIPELINE_STAGES = [
    ("scaffold", "Scaffold directories"),
    ("compile", "Compile prompts"),
    ("copy_assets", "Copy assets"),
    ("seed_tasks", "Seed tasks"),
    ("safety", "Write safety config"),
    ("diff_report", "Generate diff report"),
]


# ---------------------------------------------------------------------------
# Stage status widget
# ---------------------------------------------------------------------------

class StageStatusWidget(QWidget):
    """A single row showing a pipeline stage's status."""

    def __init__(self, stage_key: str, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.stage_key = stage_key
        self._status = "pending"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, SPACE_XS, 0, SPACE_XS)

        self._icon = QLabel("\u2022")  # bullet
        self._icon.setFixedWidth(24)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_LG}px;"
        )

        self._label = QLabel(label)
        self._label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )

        self._status_label = QLabel("Pending")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._status_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )

        layout.addWidget(self._icon)
        layout.addWidget(self._label, stretch=1)
        layout.addWidget(self._status_label)

    @property
    def status(self) -> str:
        return self._status

    def set_running(self) -> None:
        self._status = "running"
        self._icon.setText("\u25B6")  # play symbol
        self._icon.setStyleSheet(
            f"color: {ACCENT_PRIMARY}; font-size: {FONT_SIZE_LG}px;"
        )
        self._status_label.setText("Running...")
        self._status_label.setStyleSheet(
            f"color: {ACCENT_PRIMARY}; font-size: {FONT_SIZE_SM}px;"
        )

    def set_done(self, file_count: int = 0) -> None:
        self._status = "done"
        self._icon.setText("\u2713")  # checkmark
        self._icon.setStyleSheet(
            f"color: {STATUS_SUCCESS}; font-size: {FONT_SIZE_LG}px;"
        )
        text = "Done"
        if file_count:
            text += f" ({file_count} files)"
        self._status_label.setText(text)
        self._status_label.setStyleSheet(
            f"color: {STATUS_SUCCESS}; font-size: {FONT_SIZE_SM}px;"
        )

    def set_error(self, message: str = "Error") -> None:
        self._status = "error"
        self._icon.setText("\u2717")  # x-mark
        self._icon.setStyleSheet(
            f"color: {STATUS_ERROR}; font-size: {FONT_SIZE_LG}px;"
        )
        self._status_label.setText(message)
        self._status_label.setStyleSheet(
            f"color: {STATUS_ERROR}; font-size: {FONT_SIZE_SM}px;"
        )

    def set_skipped(self) -> None:
        self._status = "skipped"
        self._icon.setText("\u2013")  # en-dash
        self._icon.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_LG}px;"
        )
        self._status_label.setText("Skipped")
        self._status_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )


# ---------------------------------------------------------------------------
# Main progress screen
# ---------------------------------------------------------------------------

class GenerationProgressScreen(QWidget):
    """Screen showing generation pipeline progress and results."""

    # Emitted when generation completes successfully
    generation_complete = Signal()
    # Emitted when generation fails
    generation_failed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG_BASE};")
        self._start_time: float | None = None
        self._stage_widgets: dict[str, StageStatusWidget] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XXL, SPACE_XL, SPACE_XXL, SPACE_XL)
        layout.setSpacing(SPACE_LG)

        # Title row with spinner
        title_row = QHBoxLayout()
        title_row.setSpacing(SPACE_MD)

        self._spinner = SpinnerWidget(size=32)
        title_row.addWidget(self._spinner)

        title = QLabel("Generation Progress")
        title.setFont(QFont("", FONT_SIZE_XL, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, len(PIPELINE_STAGES))
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_SURFACE};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: {RADIUS_SM}px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_PRIMARY};
                border-radius: {RADIUS_SM}px;
            }}
        """)
        layout.addWidget(self._progress_bar)

        # Elapsed time
        self._elapsed_label = QLabel("Elapsed: 0.0s")
        self._elapsed_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        layout.addWidget(self._elapsed_label)

        # Stage list
        for stage_key, label in PIPELINE_STAGES:
            widget = StageStatusWidget(stage_key, label)
            self._stage_widgets[stage_key] = widget
            layout.addWidget(widget)

        # Log area
        log_label = QLabel("Log")
        log_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
            f" margin-top: {SPACE_SM}px;"
        )
        layout.addWidget(log_label)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(120)
        self._log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG_INSET};
                color: {ACCENT_SECONDARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_SM}px;
                font-family: monospace;
                font-size: {FONT_SIZE_SM}px;
                padding: {SPACE_SM}px;
            }}
        """)
        layout.addWidget(self._log)

        # Summary (hidden until complete)
        self._summary_label = QLabel("")
        self._summary_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        self._summary_label.setVisible(False)
        layout.addWidget(self._summary_label)

        # Open project button (hidden until complete)
        self._open_btn = QPushButton("Open Project Folder")
        self._open_btn.setToolTip("Open the generated project directory")
        self._open_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_PRIMARY};
                color: {TEXT_ON_ACCENT};
                border: none;
                border-radius: {RADIUS_MD}px;
                padding: {SPACE_MD}px {SPACE_XL}px;
                font-size: {FONT_SIZE_MD}px;
                font-weight: {FONT_WEIGHT_BOLD};
            }}
            QPushButton:hover {{
                background-color: {ACCENT_PRIMARY_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {ACCENT_PRIMARY_MUTED};
                color: {TEXT_SECONDARY};
            }}
        """)
        self._open_btn.setVisible(False)
        layout.addWidget(self._open_btn)

        layout.addStretch()

    # -- Public API --------------------------------------------------------

    @property
    def progress_bar(self) -> QProgressBar:
        return self._progress_bar

    @property
    def log_widget(self) -> QTextEdit:
        return self._log

    @property
    def summary_label(self) -> QLabel:
        return self._summary_label

    @property
    def open_button(self) -> QPushButton:
        return self._open_btn

    def stage_widget(self, key: str) -> StageStatusWidget | None:
        return self._stage_widgets.get(key)

    @property
    def spinner(self) -> SpinnerWidget:
        return self._spinner

    def start(self) -> None:
        """Mark the start of generation."""
        self._start_time = time.monotonic()
        self._progress_bar.setValue(0)
        self._log.clear()
        self._summary_label.setVisible(False)
        self._open_btn.setVisible(False)
        self._spinner.start()
        for w in self._stage_widgets.values():
            w._status = "pending"
            w._icon.setText("\u2022")
            w._icon.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_LG}px;"
            )
            w._status_label.setText("Pending")
            w._status_label.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
            )
        self.append_log("Generation started...")

    def mark_stage_running(self, stage_key: str) -> None:
        """Mark a stage as currently running."""
        widget = self._stage_widgets.get(stage_key)
        if widget:
            widget.set_running()
            self.append_log(f"Stage: {stage_key} \u2014 running")

    def mark_stage_done(self, stage_key: str, file_count: int = 0) -> None:
        """Mark a stage as completed."""
        widget = self._stage_widgets.get(stage_key)
        if widget:
            widget.set_done(file_count)
        self._update_progress()
        self.append_log(f"Stage: {stage_key} \u2014 done ({file_count} files)")

    def mark_stage_error(self, stage_key: str, message: str = "Error") -> None:
        """Mark a stage as failed."""
        widget = self._stage_widgets.get(stage_key)
        if widget:
            widget.set_error(message)
        self.append_log(f"Stage: {stage_key} \u2014 ERROR: {message}")

    def mark_stage_skipped(self, stage_key: str) -> None:
        """Mark a stage as skipped."""
        widget = self._stage_widgets.get(stage_key)
        if widget:
            widget.set_skipped()
        self._update_progress()

    def finish(self, total_files: int = 0, warnings: int = 0) -> None:
        """Mark generation as complete and show summary."""
        elapsed = self._elapsed()
        summary_parts = [f"Generation complete in {elapsed:.1f}s"]
        summary_parts.append(f"{total_files} files written")
        if warnings:
            summary_parts.append(f"{warnings} warnings")
        self._summary_label.setText(" \u2014 ".join(summary_parts))
        self._summary_label.setStyleSheet(
            f"color: {STATUS_SUCCESS}; font-size: {FONT_SIZE_MD}px;"
        )
        self._summary_label.setVisible(True)
        self._open_btn.setVisible(True)
        self._progress_bar.setValue(self._progress_bar.maximum())
        self._spinner.stop()
        self.append_log(
            f"Finished: {total_files} files, {warnings} warnings, {elapsed:.1f}s"
        )
        self.generation_complete.emit()

    def finish_with_error(self, message: str) -> None:
        """Mark generation as failed."""
        elapsed = self._elapsed()
        self._summary_label.setText(f"Generation failed: {message}")
        self._summary_label.setStyleSheet(
            f"color: {STATUS_ERROR}; font-size: {FONT_SIZE_MD}px;"
        )
        self._summary_label.setVisible(True)
        self._spinner.stop()
        self.append_log(f"FAILED after {elapsed:.1f}s: {message}")
        self.generation_failed.emit(message)

    def append_log(self, text: str) -> None:
        """Add a line to the log area."""
        self._log.append(text)

    # -- Internal ----------------------------------------------------------

    def _update_progress(self) -> None:
        """Update the progress bar based on completed/skipped stages."""
        done_count = sum(
            1 for w in self._stage_widgets.values()
            if w.status in ("done", "skipped")
        )
        self._progress_bar.setValue(done_count)
        elapsed = self._elapsed()
        self._elapsed_label.setText(f"Elapsed: {elapsed:.1f}s")

    def _elapsed(self) -> float:
        if self._start_time is None:
            return 0.0
        return time.monotonic() - self._start_time
