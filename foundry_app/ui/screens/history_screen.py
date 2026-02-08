"""History screen — browse past generation runs and their manifests."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
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
    TEXT_ON_ACCENT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from foundry_app.ui.widgets.branded_empty_state import BrandedEmptyState

logger = logging.getLogger(__name__)


class HistoryScreen(QWidget):
    """Screen for browsing past generation runs and viewing manifests."""

    regenerate_requested = Signal(str)  # path to composition YAML

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG_BASE};")
        self._projects_root: Path | None = None

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self._page_stack = QStackedWidget()
        root_layout.addWidget(self._page_stack)

        self._empty_state = BrandedEmptyState(
            heading="No Generation History",
            description=(
                "Past generation runs will appear here.\n"
                "Use the Builder to create your first project."
            ),
        )
        self._page_stack.addWidget(self._empty_state)

        content_page = QWidget()
        layout = QVBoxLayout(content_page)
        layout.setContentsMargins(SPACE_XXL, SPACE_XL, SPACE_XXL, SPACE_XL)
        layout.setSpacing(SPACE_LG)

        # Title
        title = QLabel("Generation History")
        title.setFont(QFont("", FONT_SIZE_XL, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("Browse past generation runs and view their manifests.")
        subtitle.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_MD}px;"
        )
        layout.addWidget(subtitle)

        # Split view: run list (left) + manifest details (right)
        content = QHBoxLayout()
        content.setSpacing(0)

        # Run list
        left = QVBoxLayout()
        left.setSpacing(SPACE_SM)
        list_label = QLabel("Past Runs")
        list_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        left.addWidget(list_label)

        self._run_list = QListWidget()
        self._run_list.setStyleSheet(f"""
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
        self._run_list.currentRowChanged.connect(self._on_run_selected)
        left.addWidget(self._run_list, stretch=1)

        # Vertical separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet(
            f"color: {BORDER_DEFAULT}; margin: 0 {SPACE_MD}px;"
        )

        # Manifest details
        right = QVBoxLayout()
        right.setSpacing(SPACE_SM)
        details_label = QLabel("Manifest Details")
        details_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        right.addWidget(details_label)

        self._details = QTextEdit()
        self._details.setReadOnly(True)
        self._details.setStyleSheet(f"""
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
        right.addWidget(self._details, stretch=1)

        # Metadata summary
        self._meta_label = QLabel("")
        self._meta_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        right.addWidget(self._meta_label)

        # Regenerate button
        self._regen_btn = QPushButton("Re-generate from this composition")
        self._regen_btn.setToolTip("Re-run project generation using this composition")
        self._regen_btn.setStyleSheet(f"""
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
        self._regen_btn.setEnabled(False)
        self._regen_btn.clicked.connect(self._on_regenerate)
        right.addWidget(self._regen_btn)

        content.addLayout(left, stretch=1)
        content.addWidget(separator)
        content.addLayout(right, stretch=2)
        layout.addLayout(content)

        self._page_stack.addWidget(content_page)
        self._page_stack.setCurrentIndex(0)

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
            self._page_stack.setCurrentIndex(0)
            return

        for entry in sorted(self._projects_root.iterdir(), reverse=True):
            manifest_path = entry / "manifest.json"
            if entry.is_dir() and manifest_path.is_file():
                item = QListWidgetItem(entry.name)
                item.setData(Qt.ItemDataRole.UserRole, str(manifest_path))
                self._run_list.addItem(item)

        if self._run_list.count() > 0:
            self._page_stack.setCurrentIndex(1)
        else:
            self._page_stack.setCurrentIndex(0)

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
