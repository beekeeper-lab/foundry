"""Settings screen — core path configuration for Foundry."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.settings import FoundrySettings
from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    BG_BASE,
    BG_INSET,
    BG_SURFACE,
    BORDER_DEFAULT,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XL,
    FONT_WEIGHT_BOLD,
    RADIUS_SM,
    SPACE_LG,
    SPACE_MD,
    SPACE_SM,
    SPACE_XL,
    SPACE_XXL,
    TEXT_ON_ACCENT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

logger = logging.getLogger(__name__)


class SettingsScreen(QWidget):
    """Screen for configuring core Foundry paths (library root, workspace root)."""

    settings_changed = Signal(str)  # emits new library_root path

    def __init__(
        self,
        settings: FoundrySettings | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings or FoundrySettings()
        self.setStyleSheet(f"background-color: {BG_BASE};")
        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XXL, SPACE_XL, SPACE_XXL, SPACE_XL)
        layout.setSpacing(SPACE_LG)

        # Title
        title = QLabel("Settings")
        title.setFont(QFont("", FONT_SIZE_XL, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("Configure library and workspace paths.")
        subtitle.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_MD}px;"
        )
        layout.addWidget(subtitle)

        # -- Library Root section --
        layout.addSpacing(SPACE_MD)
        self._add_section_header(layout, "LIBRARY ROOT")

        lib_desc = QLabel(
            "Path to the ai-team-library directory containing personas, stacks, "
            "templates, and workflows."
        )
        lib_desc.setWordWrap(True)
        lib_desc.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        layout.addWidget(lib_desc)

        lib_row = QHBoxLayout()
        lib_row.setSpacing(SPACE_SM)

        self._library_root_edit = QLineEdit()
        self._library_root_edit.setPlaceholderText("Select library directory...")
        self._library_root_edit.setReadOnly(True)
        self._library_root_edit.setStyleSheet(self._input_style())
        lib_row.addWidget(self._library_root_edit, stretch=1)

        self._library_browse_btn = QPushButton("Browse...")
        self._library_browse_btn.setStyleSheet(self._button_style())
        self._library_browse_btn.clicked.connect(self._browse_library)
        lib_row.addWidget(self._library_browse_btn)

        layout.addLayout(lib_row)

        # Recent libraries dropdown
        recent_label = QLabel("Recent Libraries")
        recent_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        layout.addWidget(recent_label)

        self._recent_combo = QComboBox()
        self._recent_combo.setStyleSheet(self._combo_style())
        self._recent_combo.currentIndexChanged.connect(self._on_recent_selected)
        layout.addWidget(self._recent_combo)

        # -- Workspace Root section --
        layout.addSpacing(SPACE_LG)
        self._add_section_header(layout, "WORKSPACE ROOT")

        ws_desc = QLabel(
            "Default output directory for generated projects."
        )
        ws_desc.setWordWrap(True)
        ws_desc.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        layout.addWidget(ws_desc)

        ws_row = QHBoxLayout()
        ws_row.setSpacing(SPACE_SM)

        self._workspace_root_edit = QLineEdit()
        self._workspace_root_edit.setPlaceholderText("Select workspace directory...")
        self._workspace_root_edit.setReadOnly(True)
        self._workspace_root_edit.setStyleSheet(self._input_style())
        ws_row.addWidget(self._workspace_root_edit, stretch=1)

        self._workspace_browse_btn = QPushButton("Browse...")
        self._workspace_browse_btn.setStyleSheet(self._button_style())
        self._workspace_browse_btn.clicked.connect(self._browse_workspace)
        ws_row.addWidget(self._workspace_browse_btn)

        layout.addLayout(ws_row)

        layout.addStretch(1)

    # -- Public API --------------------------------------------------------

    @property
    def library_root_edit(self) -> QLineEdit:
        return self._library_root_edit

    @property
    def workspace_root_edit(self) -> QLineEdit:
        return self._workspace_root_edit

    @property
    def recent_combo(self) -> QComboBox:
        return self._recent_combo

    @property
    def library_browse_button(self) -> QPushButton:
        return self._library_browse_btn

    @property
    def workspace_browse_button(self) -> QPushButton:
        return self._workspace_browse_btn

    def set_library_root(self, path: str) -> None:
        """Programmatically set the library root and persist it."""
        self._library_root_edit.setText(path)
        self._settings.library_root = path
        self._settings.add_recent_library(path)
        self._refresh_recent()
        self.settings_changed.emit(path)
        logger.info("Library root set to: %s", path)

    # -- Slots -------------------------------------------------------------

    def _browse_library(self) -> None:
        start_dir = self._library_root_edit.text() or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(
            self, "Select Library Root", start_dir,
        )
        if chosen:
            self.set_library_root(chosen)

    def _browse_workspace(self) -> None:
        start_dir = self._workspace_root_edit.text() or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(
            self, "Select Workspace Root", start_dir,
        )
        if chosen:
            self._workspace_root_edit.setText(chosen)
            self._settings.workspace_root = chosen
            logger.info("Workspace root set to: %s", chosen)

    def _on_recent_selected(self, index: int) -> None:
        if index < 0:
            return
        path = self._recent_combo.itemData(index)
        if path and path != self._library_root_edit.text():
            self.set_library_root(path)

    # -- Internal ----------------------------------------------------------

    def _load_values(self) -> None:
        lib = self._settings.library_root
        if lib:
            self._library_root_edit.setText(lib)

        ws = self._settings.workspace_root
        if ws:
            self._workspace_root_edit.setText(ws)

        self._refresh_recent()

    def _refresh_recent(self) -> None:
        self._recent_combo.blockSignals(True)
        self._recent_combo.clear()
        for path in self._settings.recent_libraries:
            label = path
            # Show just the last two path components for brevity
            parts = Path(path).parts
            if len(parts) > 2:
                label = str(Path(*parts[-2:]))
            self._recent_combo.addItem(label, userData=path)
        self._recent_combo.blockSignals(False)

        # Select the current library root in the combo
        current = self._library_root_edit.text()
        for i in range(self._recent_combo.count()):
            if self._recent_combo.itemData(i) == current:
                self._recent_combo.blockSignals(True)
                self._recent_combo.setCurrentIndex(i)
                self._recent_combo.blockSignals(False)
                break

    def _add_section_header(self, layout: QVBoxLayout, text: str) -> None:
        header = QLabel(text)
        header.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: {FONT_SIZE_SM}px;
            font-weight: {FONT_WEIGHT_BOLD};
            letter-spacing: 1px;
            padding-bottom: {SPACE_SM}px;
            border-bottom: 1px solid {BORDER_DEFAULT};
        """)
        layout.addWidget(header)

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                background-color: {BG_INSET};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_SM}px;
                padding: {SPACE_SM}px {SPACE_MD}px;
                font-size: {FONT_SIZE_MD}px;
            }}
        """

    def _button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {ACCENT_PRIMARY};
                color: {TEXT_ON_ACCENT};
                border: none;
                border-radius: {RADIUS_SM}px;
                padding: {SPACE_SM}px {SPACE_LG}px;
                font-size: {FONT_SIZE_MD}px;
                font-weight: {FONT_WEIGHT_BOLD};
            }}
            QPushButton:hover {{
                background-color: {ACCENT_PRIMARY_HOVER};
            }}
        """

    def _combo_style(self) -> str:
        return f"""
            QComboBox {{
                background-color: {BG_INSET};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_SM}px;
                padding: {SPACE_SM}px {SPACE_MD}px;
                font-size: {FONT_SIZE_MD}px;
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: {SPACE_SM}px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                selection-background-color: {ACCENT_PRIMARY};
                selection-color: {TEXT_ON_ACCENT};
            }}
        """
