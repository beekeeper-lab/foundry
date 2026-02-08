"""History screen — browse past generation runs and their manifests."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

# Catppuccin Mocha
_BG = "#1e1e2e"
_SURFACE = "#313244"
_TEXT = "#cdd6f4"
_SUBTEXT = "#6c7086"
_ACCENT = "#cba6f7"


class HistoryScreen(QWidget):
    """Screen for browsing past generation runs and viewing manifests."""

    regenerate_requested = Signal(str)  # path to composition YAML

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {_BG};")
        self._projects_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Generation History")
        title.setFont(QFont("", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_TEXT};")
        layout.addWidget(title)

        subtitle = QLabel("Browse past generation runs and view their manifests.")
        subtitle.setStyleSheet(f"color: {_SUBTEXT}; font-size: 14px;")
        layout.addWidget(subtitle)

        # Split view: run list (left) + manifest details (right)
        content = QHBoxLayout()

        # Run list
        left = QVBoxLayout()
        list_label = QLabel("Past Runs")
        list_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
        left.addWidget(list_label)

        self._run_list = QListWidget()
        self._run_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {_SURFACE};
                color: {_TEXT};
                border: 1px solid {_SURFACE};
                border-radius: 4px;
                font-size: 13px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
            }}
            QListWidget::item:selected {{
                background-color: {_BG};
                color: {_ACCENT};
            }}
        """)
        self._run_list.currentRowChanged.connect(self._on_run_selected)
        left.addWidget(self._run_list, stretch=1)

        # Manifest details
        right = QVBoxLayout()
        details_label = QLabel("Manifest Details")
        details_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
        right.addWidget(details_label)

        self._details = QTextEdit()
        self._details.setReadOnly(True)
        self._details.setStyleSheet(f"""
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
        right.addWidget(self._details, stretch=1)

        # Metadata summary
        self._meta_label = QLabel("")
        self._meta_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
        right.addWidget(self._meta_label)

        # Regenerate button
        self._regen_btn = QPushButton("Re-generate from this composition")
        self._regen_btn.setStyleSheet(f"""
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
            QPushButton:disabled {{
                background-color: {_SURFACE};
                color: {_SUBTEXT};
            }}
        """)
        self._regen_btn.setEnabled(False)
        self._regen_btn.clicked.connect(self._on_regenerate)
        right.addWidget(self._regen_btn)

        content.addLayout(left, stretch=1)
        content.addLayout(right, stretch=2)
        layout.addLayout(content)

    # -- Public API --------------------------------------------------------

    @property
    def run_list(self) -> QListWidget:
        return self._run_list

    @property
    def details_widget(self) -> QTextEdit:
        return self._details

    @property
    def meta_label(self) -> QLabel:
        return self._meta_label

    @property
    def regenerate_button(self) -> QPushButton:
        return self._regen_btn

    def set_projects_root(self, root: str | Path) -> None:
        """Set the root directory and refresh the run list."""
        self._projects_root = Path(root)
        self.refresh_runs()

    def refresh_runs(self) -> None:
        """Scan for manifest.json files and populate the run list."""
        self._run_list.clear()
        self._details.clear()
        self._meta_label.setText("")
        self._regen_btn.setEnabled(False)

        if self._projects_root is None or not self._projects_root.is_dir():
            return

        for entry in sorted(self._projects_root.iterdir(), reverse=True):
            manifest_path = entry / "manifest.json"
            if entry.is_dir() and manifest_path.is_file():
                item = QListWidgetItem(entry.name)
                item.setData(Qt.ItemDataRole.UserRole, str(manifest_path))
                self._run_list.addItem(item)

    def selected_manifest_path(self) -> Path | None:
        """Return the path of the currently selected manifest."""
        item = self._run_list.currentItem()
        if item is None:
            return None
        return Path(item.data(Qt.ItemDataRole.UserRole))

    # -- Slots -------------------------------------------------------------

    def _on_run_selected(self, row: int) -> None:
        if row < 0:
            self._details.clear()
            self._meta_label.setText("")
            self._regen_btn.setEnabled(False)
            return

        manifest_path = self.selected_manifest_path()
        if manifest_path is None or not manifest_path.is_file():
            self._details.setPlainText("Manifest file not found.")
            return

        try:
            raw = manifest_path.read_text(encoding="utf-8")
            data = json.loads(raw)
            self._details.setPlainText(json.dumps(data, indent=2))

            # Extract summary metadata
            run_id = data.get("run_id", "unknown")
            generated_at = data.get("generated_at", "unknown")
            lib_version = data.get("library_version", "")
            stages = data.get("stages", {})
            total_files = sum(len(s.get("wrote", [])) for s in stages.values())

            meta = f"Run: {run_id}  |  Date: {generated_at}  |  Files: {total_files}"
            if lib_version:
                meta += f"  |  Library: {lib_version}"
            self._meta_label.setText(meta)
            self._regen_btn.setEnabled(True)

        except (json.JSONDecodeError, OSError) as exc:
            self._details.setPlainText(f"Error reading manifest: {exc}")
            self._meta_label.setText("")
            self._regen_btn.setEnabled(False)

    def _on_regenerate(self) -> None:
        manifest_path = self.selected_manifest_path()
        if manifest_path is None:
            return
        # Signal with the project directory (parent of manifest.json)
        self.regenerate_requested.emit(str(manifest_path.parent))
