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
    QStackedWidget,
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
    BG_OVERLAY,
    BG_SURFACE,
    BORDER_DEFAULT,
    BORDER_SUBTLE,
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
from foundry_app.ui.widgets.branded_empty_state import BrandedEmptyState

logger = logging.getLogger(__name__)

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
        self.setStyleSheet(f"background-color: {BG_BASE};")
        self._projects_root: Path | None = None

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self._page_stack = QStackedWidget()
        root_layout.addWidget(self._page_stack)

        self._empty_state = BrandedEmptyState(
            heading="No Projects to Export",
            description=(
                "Generated projects will appear here for export.\n"
                "Use the Builder to create a project first."
            ),
        )
        self._page_stack.addWidget(self._empty_state)

        content_page = QWidget()
        layout = QVBoxLayout(content_page)
        layout.setContentsMargins(SPACE_XXL, SPACE_XL, SPACE_XXL, SPACE_XL)
        layout.setSpacing(SPACE_LG)

        # Title
        title = QLabel("Export Project")
        title.setFont(QFont("", FONT_SIZE_XL, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("Select a generated project and export it as an archive.")
        subtitle.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_MD}px;"
        )
        layout.addWidget(subtitle)

        # Project list
        list_label = QLabel("Generated Projects")
        list_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
            f" margin-top: {SPACE_SM}px;"
        )
        layout.addWidget(list_label)

        self._project_list = QListWidget()
        self._project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_SM}px;
                font-size: {FONT_SIZE_MD}px;
                padding: {SPACE_XS}px;
            }}
            QListWidget::item {{
                padding: {SPACE_SM}px {SPACE_MD}px;
                border-bottom: 1px solid {BORDER_SUBTLE};
            }}
            QListWidget::item:selected {{
                background-color: {BG_OVERLAY};
                color: {ACCENT_PRIMARY};
                border-left: 2px solid {ACCENT_PRIMARY};
            }}
            QListWidget::item:hover {{
                background-color: {BG_OVERLAY};
            }}
        """)
        layout.addWidget(self._project_list, stretch=1)

        # Format selector and export button
        controls = QHBoxLayout()

        fmt_label = QLabel("Format:")
        fmt_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        controls.addWidget(fmt_label)

        self._format_combo = QComboBox()
        for fmt_id, fmt_label_text in _ARCHIVE_FORMATS:
            self._format_combo.addItem(fmt_label_text, fmt_id)
        self._format_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_INSET};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_SM}px;
                padding: {SPACE_SM}px {SPACE_MD}px;
                font-size: {FONT_SIZE_MD}px;
            }}
            QComboBox:hover {{
                border-color: {ACCENT_SECONDARY};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: {SPACE_SM}px;
            }}
        """)
        controls.addWidget(self._format_combo)
        controls.addStretch()

        self._export_btn = QPushButton("Export")
        self._export_btn.setToolTip("Export the selected project as an archive")
        self._export_btn.setStyleSheet(f"""
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
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._on_export)
        controls.addWidget(self._export_btn)

        layout.addLayout(controls)

        # Status
        self._status_label = QLabel("")
        self._status_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        layout.addWidget(self._status_label)

        # Wire selection
        self._project_list.currentRowChanged.connect(self._on_selection_changed)

        self._page_stack.addWidget(content_page)
        self._page_stack.setCurrentIndex(0)

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
            self._page_stack.setCurrentIndex(0)
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

        if self._project_list.count() > 0:
            self._page_stack.setCurrentIndex(1)
        else:
            self._page_stack.setCurrentIndex(0)

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
            self._status_label.setStyleSheet(
                f"color: {STATUS_SUCCESS}; font-size: {FONT_SIZE_SM}px;"
            )
            self.export_complete.emit(result_path)
            logger.info("Exported project %s to %s", project_path.name, result_path)
        except Exception as exc:
            self._status_label.setText(f"Export failed: {exc}")
            self._status_label.setStyleSheet(
                f"color: {STATUS_ERROR}; font-size: {FONT_SIZE_SM}px;"
            )
            logger.error("Export failed: %s", exc)
