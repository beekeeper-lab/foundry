"""Export screen — archive generated projects as ZIP or tarball."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
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
_GREEN = "#a6e3a1"

_ARCHIVE_FORMATS = [
    ("zip", "ZIP archive"),
    ("tar.gz", "Gzipped tarball"),
    ("tar.bz2", "Bzipped tarball"),
]


class ExportScreen(QWidget):
    """Screen for exporting generated projects as archives."""

    export_complete = Signal(str)  # path to exported archive

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {_BG};")
        self._projects_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Export Project")
        title.setFont(QFont("", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_TEXT};")
        layout.addWidget(title)

        subtitle = QLabel("Select a generated project and export it as an archive.")
        subtitle.setStyleSheet(f"color: {_SUBTEXT}; font-size: 14px;")
        layout.addWidget(subtitle)

        # Project list
        list_label = QLabel("Generated Projects")
        list_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px; margin-top: 8px;")
        layout.addWidget(list_label)

        self._project_list = QListWidget()
        self._project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {_SURFACE};
                color: {_TEXT};
                border: 1px solid {_SURFACE};
                border-radius: 4px;
                font-size: 14px;
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
        layout.addWidget(self._project_list, stretch=1)

        # Format selector and export button
        controls = QHBoxLayout()

        fmt_label = QLabel("Format:")
        fmt_label.setStyleSheet(f"color: {_TEXT}; font-size: 14px;")
        controls.addWidget(fmt_label)

        self._format_combo = QComboBox()
        for fmt_id, fmt_label_text in _ARCHIVE_FORMATS:
            self._format_combo.addItem(fmt_label_text, fmt_id)
        self._format_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {_SURFACE};
                color: {_TEXT};
                border: 1px solid {_SURFACE};
                border-radius: 4px;
                padding: 6px 12px;
            }}
        """)
        controls.addWidget(self._format_combo)
        controls.addStretch()

        self._export_btn = QPushButton("Export")
        self._export_btn.setStyleSheet(f"""
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
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._on_export)
        controls.addWidget(self._export_btn)

        layout.addLayout(controls)

        # Status
        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
        layout.addWidget(self._status_label)

        # Wire selection
        self._project_list.currentRowChanged.connect(self._on_selection_changed)

    # -- Public API --------------------------------------------------------

    @property
    def project_list(self) -> QListWidget:
        return self._project_list

    @property
    def format_combo(self) -> QComboBox:
        return self._format_combo

    @property
    def export_button(self) -> QPushButton:
        return self._export_btn

    @property
    def status_label(self) -> QLabel:
        return self._status_label

    def set_projects_root(self, root: str | Path) -> None:
        """Set the root directory containing generated projects and refresh list."""
        self._projects_root = Path(root)
        self.refresh_projects()

    def refresh_projects(self) -> None:
        """Scan the projects root and populate the list."""
        self._project_list.clear()
        if self._projects_root is None or not self._projects_root.is_dir():
            return

        for entry in sorted(self._projects_root.iterdir()):
            if entry.is_dir():
                # Check for manifest.json as an indicator of a generated project
                has_manifest = (entry / "manifest.json").is_file()
                label = entry.name
                if has_manifest:
                    label += " (manifest found)"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, str(entry))
                self._project_list.addItem(item)

    def selected_project_path(self) -> Path | None:
        """Return the path of the currently selected project."""
        item = self._project_list.currentItem()
        if item is None:
            return None
        return Path(item.data(Qt.ItemDataRole.UserRole))

    # -- Slots -------------------------------------------------------------

    def _on_selection_changed(self, row: int) -> None:
        self._export_btn.setEnabled(row >= 0)

    def _on_export(self) -> None:
        project_path = self.selected_project_path()
        if project_path is None:
            return

        fmt_id = self._format_combo.currentData()
        # Map format ID to shutil format name
        fmt_map = {"zip": "zip", "tar.gz": "gztar", "tar.bz2": "bztar"}
        shutil_fmt = fmt_map.get(fmt_id, "zip")

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Project",
            str(project_path.parent / f"{project_path.name}.{fmt_id}"),
        )
        if not save_path:
            return

        try:
            # shutil.make_archive wants base name without extension
            base_name = save_path
            for ext in [".zip", ".tar.gz", ".tar.bz2"]:
                if base_name.endswith(ext):
                    base_name = base_name[: -len(ext)]

            result_path = shutil.make_archive(
                base_name, shutil_fmt, root_dir=str(project_path),
            )
            self._status_label.setText(f"Exported: {result_path}")
            self._status_label.setStyleSheet(f"color: {_GREEN}; font-size: 12px;")
            self.export_complete.emit(result_path)
            logger.info("Exported project %s to %s", project_path.name, result_path)
        except Exception as exc:
            self._status_label.setText(f"Export failed: {exc}")
            self._status_label.setStyleSheet("color: #f38ba8; font-size: 12px;")
            logger.error("Export failed: %s", exc)
