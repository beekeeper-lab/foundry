"""Generation progress screen — displays real-time pipeline stage progress."""

from __future__ import annotations

import logging
import time

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
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
    ("agent_writer", "Write agent files"),
    ("copy_assets", "Copy assets"),
    ("mcp_config", "Write MCP config"),
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
    # Emitted when user clicks "Back to Builder"
    back_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG_BASE};")
        self._start_time: float | None = None
        self._output_path: str = ""
        self._stage_widgets: dict[str, StageStatusWidget] = {}

        # Outer layout hosts: outcome banner (sticky top) + scrollable content.
        # The banner is a sibling of the scroll area, not a child, so it stays
        # visible at the top of the screen on small windows where the back/open
        # buttons would otherwise sit below the fold (BEAN-287).
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._build_outcome_banner(outer)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setStyleSheet(f"background-color: {BG_BASE};")
        outer.addWidget(self._scroll, stretch=1)

        container = QWidget()
        self._scroll.setWidget(container)
        layout = QVBoxLayout(container)
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
        self._log.setFixedHeight(80)
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

        # Output path display (hidden until complete). Stays in the scroll
        # body — the recovery affordance (Back / Open buttons) lives in the
        # sticky banner above; the path is metadata users only need once
        # they've reached for it.
        self._path_label = QLabel("")
        self._path_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
            f" font-family: monospace;"
        )
        self._path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._path_label.setVisible(False)
        layout.addWidget(self._path_label)

        layout.addStretch()

    def _build_outcome_banner(self, outer: QVBoxLayout) -> None:
        """Build the sticky top banner containing the outcome summary and
        recovery actions (BEAN-287). Hidden until ``finish`` or
        ``finish_with_error`` fires.
        """
        self._outcome_banner = QFrame()
        self._outcome_banner.setObjectName("outcome-banner")
        self._outcome_banner.setStyleSheet(f"""
            QFrame#outcome-banner {{
                background-color: {BG_SURFACE};
                border-bottom: 1px solid {BORDER_DEFAULT};
            }}
        """)
        self._outcome_banner.setVisible(False)

        banner_layout = QVBoxLayout(self._outcome_banner)
        banner_layout.setContentsMargins(
            SPACE_XXL, SPACE_MD, SPACE_XXL, SPACE_MD,
        )
        banner_layout.setSpacing(SPACE_SM)

        self._summary_label = QLabel("")
        self._summary_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        self._summary_label.setWordWrap(True)
        banner_layout.addWidget(self._summary_label)

        action_row = QHBoxLayout()
        action_row.setSpacing(SPACE_SM)
        action_row.setContentsMargins(0, SPACE_XS, 0, 0)

        self._back_btn = QPushButton("Back to Builder")
        self._back_btn.setMinimumHeight(36)
        self._back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_MD}px;
                padding: {SPACE_SM}px {SPACE_LG}px;
                font-size: {FONT_SIZE_MD}px;
            }}
            QPushButton:hover {{
                background-color: {BG_INSET};
            }}
        """)
        self._back_btn.setVisible(False)
        self._back_btn.clicked.connect(self.back_requested.emit)
        action_row.addWidget(self._back_btn)

        self._open_btn = QPushButton("Open Project Folder")
        self._open_btn.setToolTip("Open the generated project directory")
        self._open_btn.setMinimumHeight(36)
        self._open_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_PRIMARY};
                color: {TEXT_ON_ACCENT};
                border: none;
                border-radius: {RADIUS_MD}px;
                padding: {SPACE_SM}px {SPACE_LG}px;
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
        self._open_btn.clicked.connect(self._open_output_folder)
        action_row.addWidget(self._open_btn)

        action_row.addStretch(1)
        banner_layout.addLayout(action_row)

        outer.addWidget(self._outcome_banner)

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

    @property
    def back_button(self) -> QPushButton:
        return self._back_btn

    @property
    def path_label(self) -> QLabel:
        return self._path_label

    def set_output_path(self, path: str) -> None:
        """Set the output folder path shown after generation."""
        self._output_path = path
        self._path_label.setText(f"Output: {path}")
        self._path_label.setVisible(True)

    def start(self) -> None:
        """Mark the start of generation."""
        self._start_time = time.monotonic()
        self._progress_bar.setValue(0)
        self._log.clear()
        self._outcome_banner.setVisible(False)
        self._summary_label.setText("")
        self._open_btn.setVisible(False)
        self._back_btn.setVisible(False)
        self._path_label.setVisible(False)
        self._output_path = ""
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
        self.append_log(f"Stage: {stage_key} \u2014 skipped")

    def finish(
        self,
        total_files: int = 0,
        warnings: int = 0,
        warnings_list: list[str] | None = None,
    ) -> None:
        """Mark generation as complete and show summary.

        ``warnings_list`` carries the full warning messages so the user can
        read them in the log area — previously only the count was surfaced.
        """
        elapsed = self._elapsed()
        summary_parts = [f"Generation complete in {elapsed:.1f}s"]
        summary_parts.append(f"{total_files} files written")
        if warnings:
            summary_parts.append(f"{warnings} warnings")
        self._summary_label.setText(" \u2014 ".join(summary_parts))
        self._summary_label.setStyleSheet(
            f"color: {STATUS_SUCCESS}; font-size: {FONT_SIZE_MD}px; "
            f"font-weight: {FONT_WEIGHT_BOLD};"
        )
        self._open_btn.setVisible(True)
        self._back_btn.setVisible(True)
        self._outcome_banner.setVisible(True)
        self._progress_bar.setValue(self._progress_bar.maximum())
        self._spinner.stop()
        self._scroll.verticalScrollBar().setValue(0)
        for warning in warnings_list or ():
            self.append_log(f"\u26a0 {warning}")
        self.append_log(
            f"Finished: {total_files} files, {warnings} warnings, {elapsed:.1f}s"
        )
        self.generation_complete.emit()

    def finish_with_error(self, message: str) -> None:
        """Mark generation as failed."""
        elapsed = self._elapsed()
        self._summary_label.setText(f"Can't generate yet — {message}")
        self._summary_label.setStyleSheet(
            f"color: {STATUS_ERROR}; font-size: {FONT_SIZE_MD}px; "
            f"font-weight: {FONT_WEIGHT_BOLD};"
        )
        self._open_btn.setVisible(False)
        self._back_btn.setVisible(True)
        self._outcome_banner.setVisible(True)
        self._spinner.stop()
        # Safety net: pop the scroll back to the top so the banner — and
        # therefore the Back to Builder button — is on-screen even if a
        # custom theme inflates the banner past the viewport (BEAN-287).
        self._scroll.verticalScrollBar().setValue(0)
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

    def _open_output_folder(self) -> None:
        """Open the output folder in the system file manager."""
        if not self._output_path:
            return

        import subprocess
        import sys

        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", self._output_path])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self._output_path])
            else:
                subprocess.Popen(["xdg-open", self._output_path])
        except OSError:
            # Fallback to Qt method if subprocess fails
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices

            QDesktopServices.openUrl(QUrl.fromLocalFile(self._output_path))
