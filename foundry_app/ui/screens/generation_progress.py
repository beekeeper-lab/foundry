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

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Catppuccin Mocha colours
# ---------------------------------------------------------------------------

_BG = "#1e1e2e"
_SURFACE = "#313244"
_TEXT = "#cdd6f4"
_SUBTEXT = "#6c7086"
_ACCENT = "#cba6f7"
_GREEN = "#a6e3a1"
_RED = "#f38ba8"
_YELLOW = "#f9e2af"


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
        layout.setContentsMargins(0, 4, 0, 4)

        self._icon = QLabel("\u2022")  # bullet
        self._icon.setFixedWidth(24)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet(f"color: {_SUBTEXT}; font-size: 16px;")

        self._label = QLabel(label)
        self._label.setStyleSheet(f"color: {_TEXT}; font-size: 14px;")

        self._status_label = QLabel("Pending")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._status_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")

        layout.addWidget(self._icon)
        layout.addWidget(self._label, stretch=1)
        layout.addWidget(self._status_label)

    @property
    def status(self) -> str:
        return self._status

    def set_running(self) -> None:
        self._status = "running"
        self._icon.setText("\u25B6")  # play symbol
        self._icon.setStyleSheet(f"color: {_ACCENT}; font-size: 16px;")
        self._status_label.setText("Running...")
        self._status_label.setStyleSheet(f"color: {_ACCENT}; font-size: 12px;")

    def set_done(self, file_count: int = 0) -> None:
        self._status = "done"
        self._icon.setText("\u2713")  # checkmark
        self._icon.setStyleSheet(f"color: {_GREEN}; font-size: 16px;")
        text = "Done"
        if file_count:
            text += f" ({file_count} files)"
        self._status_label.setText(text)
        self._status_label.setStyleSheet(f"color: {_GREEN}; font-size: 12px;")

    def set_error(self, message: str = "Error") -> None:
        self._status = "error"
        self._icon.setText("\u2717")  # x-mark
        self._icon.setStyleSheet(f"color: {_RED}; font-size: 16px;")
        self._status_label.setText(message)
        self._status_label.setStyleSheet(f"color: {_RED}; font-size: 12px;")

    def set_skipped(self) -> None:
        self._status = "skipped"
        self._icon.setText("\u2013")  # en-dash
        self._icon.setStyleSheet(f"color: {_SUBTEXT}; font-size: 16px;")
        self._status_label.setText("Skipped")
        self._status_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")


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
        self.setStyleSheet(f"background-color: {_BG};")
        self._start_time: float | None = None
        self._stage_widgets: dict[str, StageStatusWidget] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Generation Progress")
        title.setFont(QFont("", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_TEXT};")
        layout.addWidget(title)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, len(PIPELINE_STAGES))
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {_SURFACE};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {_ACCENT};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self._progress_bar)

        # Elapsed time
        self._elapsed_label = QLabel("Elapsed: 0.0s")
        self._elapsed_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
        layout.addWidget(self._elapsed_label)

        # Stage list
        for stage_key, label in PIPELINE_STAGES:
            widget = StageStatusWidget(stage_key, label)
            self._stage_widgets[stage_key] = widget
            layout.addWidget(widget)

        # Log area
        log_label = QLabel("Log")
        log_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px; margin-top: 8px;")
        layout.addWidget(log_label)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(120)
        self._log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {_SURFACE};
                color: {_TEXT};
                border: 1px solid {_SURFACE};
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                padding: 8px;
            }}
        """)
        layout.addWidget(self._log)

        # Summary (hidden until complete)
        self._summary_label = QLabel("")
        self._summary_label.setStyleSheet(f"color: {_TEXT}; font-size: 14px;")
        self._summary_label.setVisible(False)
        layout.addWidget(self._summary_label)

        # Open project button (hidden until complete)
        self._open_btn = QPushButton("Open Project Folder")
        self._open_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_ACCENT};
                color: {_BG};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #b4befe;
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

    def start(self) -> None:
        """Mark the start of generation."""
        self._start_time = time.monotonic()
        self._progress_bar.setValue(0)
        self._log.clear()
        self._summary_label.setVisible(False)
        self._open_btn.setVisible(False)
        for w in self._stage_widgets.values():
            w._status = "pending"
            w._icon.setText("\u2022")
            w._icon.setStyleSheet(f"color: {_SUBTEXT}; font-size: 16px;")
            w._status_label.setText("Pending")
            w._status_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
        self.append_log("Generation started...")

    def mark_stage_running(self, stage_key: str) -> None:
        """Mark a stage as currently running."""
        widget = self._stage_widgets.get(stage_key)
        if widget:
            widget.set_running()
            self.append_log(f"Stage: {stage_key} — running")

    def mark_stage_done(self, stage_key: str, file_count: int = 0) -> None:
        """Mark a stage as completed."""
        widget = self._stage_widgets.get(stage_key)
        if widget:
            widget.set_done(file_count)
        self._update_progress()
        self.append_log(f"Stage: {stage_key} — done ({file_count} files)")

    def mark_stage_error(self, stage_key: str, message: str = "Error") -> None:
        """Mark a stage as failed."""
        widget = self._stage_widgets.get(stage_key)
        if widget:
            widget.set_error(message)
        self.append_log(f"Stage: {stage_key} — ERROR: {message}")

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
        self._summary_label.setStyleSheet(f"color: {_GREEN}; font-size: 14px;")
        self._summary_label.setVisible(True)
        self._open_btn.setVisible(True)
        self._progress_bar.setValue(self._progress_bar.maximum())
        self.append_log(f"Finished: {total_files} files, {warnings} warnings, {elapsed:.1f}s")
        self.generation_complete.emit()

    def finish_with_error(self, message: str) -> None:
        """Mark generation as failed."""
        elapsed = self._elapsed()
        self._summary_label.setText(f"Generation failed: {message}")
        self._summary_label.setStyleSheet(f"color: {_RED}; font-size: 14px;")
        self._summary_label.setVisible(True)
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
