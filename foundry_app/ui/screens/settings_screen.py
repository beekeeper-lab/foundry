"""Settings screen — core path configuration for Foundry."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
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
    STATUS_ERROR,
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
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {BG_BASE}; border: none; }}
            QScrollBar:vertical {{
                background-color: {BG_INSET}; width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {BORDER_DEFAULT}; border-radius: 4px;
            }}
        """)
        outer_layout.addWidget(scroll)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(SPACE_XXL, SPACE_XL, SPACE_XXL, SPACE_XL)
        layout.setSpacing(SPACE_LG)
        scroll.setWidget(content)

        # Title
        title = QLabel("Settings")
        title.setFont(QFont("", FONT_SIZE_XL, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("Configure paths, generation behavior, and safety defaults.")
        subtitle.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_MD}px;"
        )
        layout.addWidget(subtitle)

        # -- Library Root section --
        layout.addSpacing(SPACE_MD)
        self._add_section_header(layout, "LIBRARY ROOT")

        lib_desc = QLabel(
            "Path to the ai-team-library directory containing personas, expertise, "
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

        # -- Generation Defaults section --
        layout.addSpacing(SPACE_LG)
        self._add_section_header(layout, "GENERATION DEFAULTS")

        gen_desc = QLabel(
            "Default generation behavior for new compositions. "
            "These can be overridden per-composition in the wizard."
        )
        gen_desc.setWordWrap(True)
        gen_desc.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        layout.addWidget(gen_desc)

        # Overlay mode checkbox
        self._overlay_check = QCheckBox("Enable overlay mode (preserve existing files)")
        self._overlay_check.setStyleSheet(f"""
            QCheckBox {{ color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; }}
        """)
        self._overlay_check.toggled.connect(self._on_overlay_changed)
        layout.addWidget(self._overlay_check)

        # Strictness dropdown
        strict_row = QHBoxLayout()
        strict_row.setSpacing(SPACE_SM)
        strict_label = QLabel("Validation strictness:")
        strict_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        strict_row.addWidget(strict_label)
        self._strictness_combo = QComboBox()
        self._strictness_combo.addItem("Light", "light")
        self._strictness_combo.addItem("Standard", "standard")
        self._strictness_combo.addItem("Strict", "strict")
        self._strictness_combo.setStyleSheet(self._combo_style())
        self._strictness_combo.currentIndexChanged.connect(self._on_strictness_changed)
        strict_row.addWidget(self._strictness_combo)
        strict_row.addStretch()
        layout.addLayout(strict_row)

        # Seed mode dropdown
        seed_row = QHBoxLayout()
        seed_row.setSpacing(SPACE_SM)
        seed_label = QLabel("Default seed mode:")
        seed_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        seed_row.addWidget(seed_label)
        self._seed_combo = QComboBox()
        self._seed_combo.addItem("Detailed", "detailed")
        self._seed_combo.addItem("Kickoff", "kickoff")
        self._seed_combo.addItem("None", "none")
        self._seed_combo.setStyleSheet(self._combo_style())
        self._seed_combo.currentIndexChanged.connect(self._on_seed_mode_changed)
        seed_row.addWidget(self._seed_combo)
        seed_row.addStretch()
        layout.addLayout(seed_row)

        # -- Safety Defaults section --
        layout.addSpacing(SPACE_LG)
        self._add_section_header(layout, "SAFETY DEFAULTS")

        safety_desc = QLabel(
            "Default safety posture for generated projects. "
            "Controls git policies, shell restrictions, and secret scanning."
        )
        safety_desc.setWordWrap(True)
        safety_desc.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        layout.addWidget(safety_desc)

        # Write safety config checkbox
        self._write_safety_check = QCheckBox("Write safety config to generated projects")
        self._write_safety_check.setStyleSheet(f"""
            QCheckBox {{ color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; }}
        """)
        self._write_safety_check.toggled.connect(self._on_write_safety_changed)
        layout.addWidget(self._write_safety_check)

        # Safety posture dropdown
        posture_row = QHBoxLayout()
        posture_row.setSpacing(SPACE_SM)
        posture_label = QLabel("Default safety posture:")
        posture_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        posture_row.addWidget(posture_label)
        self._posture_combo = QComboBox()
        self._posture_combo.addItem("Baseline", "baseline")
        self._posture_combo.addItem("Hardened", "hardened")
        self._posture_combo.addItem("Regulated", "regulated")
        self._posture_combo.setStyleSheet(self._combo_style())
        self._posture_combo.currentIndexChanged.connect(self._on_posture_changed)
        posture_row.addWidget(self._posture_combo)
        posture_row.addStretch()
        layout.addLayout(posture_row)

        # -- Appearance section --
        layout.addSpacing(SPACE_LG)
        self._add_section_header(layout, "APPEARANCE")

        appear_desc = QLabel(
            "Visual preferences for the application. "
            "Font size changes take effect immediately."
        )
        appear_desc.setWordWrap(True)
        appear_desc.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        layout.addWidget(appear_desc)

        # Font size dropdown
        font_row = QHBoxLayout()
        font_row.setSpacing(SPACE_SM)
        font_label = QLabel("Font size:")
        font_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        font_row.addWidget(font_label)
        self._font_size_combo = QComboBox()
        self._font_size_combo.addItem("Small", "small")
        self._font_size_combo.addItem("Medium", "medium")
        self._font_size_combo.addItem("Large", "large")
        self._font_size_combo.setStyleSheet(self._combo_style())
        self._font_size_combo.currentIndexChanged.connect(self._on_font_size_changed)
        font_row.addWidget(self._font_size_combo)
        font_row.addStretch()
        layout.addLayout(font_row)

        # Theme dropdown (placeholder for future)
        theme_row = QHBoxLayout()
        theme_row.setSpacing(SPACE_SM)
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        theme_row.addWidget(theme_label)
        self._theme_combo = QComboBox()
        self._theme_combo.addItem("Dark (Industrial)", "dark")
        self._theme_combo.setStyleSheet(self._combo_style())
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self._theme_combo)
        theme_row.addStretch()
        layout.addLayout(theme_row)

        # -- Advanced section --
        layout.addSpacing(SPACE_LG)
        self._add_section_header(layout, "ADVANCED")

        from foundry_app import __version__

        version_label = QLabel(f"Foundry v{__version__}")
        version_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
        )
        layout.addWidget(version_label)

        config_path = QLabel(f"Config: {self._settings._qs.fileName()}")
        config_path.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        config_path.setWordWrap(True)
        layout.addWidget(config_path)

        self._reset_btn = QPushButton("Reset All Settings")
        self._reset_btn.setStyleSheet(self._danger_button_style())
        self._reset_btn.clicked.connect(self._on_reset_all)
        self._reset_btn.setFixedWidth(200)
        layout.addWidget(self._reset_btn)

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

    @property
    def overlay_check(self) -> QCheckBox:
        return self._overlay_check

    @property
    def strictness_combo(self) -> QComboBox:
        return self._strictness_combo

    @property
    def seed_combo(self) -> QComboBox:
        return self._seed_combo

    @property
    def write_safety_check(self) -> QCheckBox:
        return self._write_safety_check

    @property
    def posture_combo(self) -> QComboBox:
        return self._posture_combo

    @property
    def font_size_combo(self) -> QComboBox:
        return self._font_size_combo

    @property
    def theme_combo(self) -> QComboBox:
        return self._theme_combo

    @property
    def reset_button(self) -> QPushButton:
        return self._reset_btn

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

    def _on_overlay_changed(self, checked: bool) -> None:
        self._settings.default_overlay_mode = checked
        logger.info("Overlay mode default set to: %s", checked)

    def _on_strictness_changed(self, index: int) -> None:
        val = self._strictness_combo.itemData(index)
        if val:
            self._settings.default_strictness = val
            logger.info("Strictness default set to: %s", val)

    def _on_seed_mode_changed(self, index: int) -> None:
        val = self._seed_combo.itemData(index)
        if val:
            self._settings.default_seed_mode = val
            logger.info("Seed mode default set to: %s", val)

    def _on_write_safety_changed(self, checked: bool) -> None:
        self._settings.write_safety_config = checked
        logger.info("Write safety config default set to: %s", checked)

    def _on_posture_changed(self, index: int) -> None:
        val = self._posture_combo.itemData(index)
        if val:
            self._settings.default_safety_posture = val
            logger.info("Safety posture default set to: %s", val)

    def _on_font_size_changed(self, index: int) -> None:
        val = self._font_size_combo.itemData(index)
        if val:
            self._settings.font_size_preference = val
            logger.info("Font size preference set to: %s", val)

    def _on_theme_changed(self, index: int) -> None:
        val = self._theme_combo.itemData(index)
        if val:
            self._settings.theme_preference = val
            logger.info("Theme preference set to: %s", val)

    def _on_reset_all(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        result = QMessageBox.question(
            self,
            "Reset All Settings",
            "This will clear all settings and restore defaults.\n\n"
            "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            self._settings.reset_all()
            self._load_values()
            logger.info("All settings reset to defaults")

    # -- Internal ----------------------------------------------------------

    def _load_values(self) -> None:
        lib = self._settings.library_root
        if lib:
            self._library_root_edit.setText(lib)

        ws = self._settings.workspace_root
        if ws:
            self._workspace_root_edit.setText(ws)

        self._refresh_recent()

        # Generation defaults
        self._overlay_check.setChecked(self._settings.default_overlay_mode)

        strictness = self._settings.default_strictness
        for i in range(self._strictness_combo.count()):
            if self._strictness_combo.itemData(i) == strictness:
                self._strictness_combo.setCurrentIndex(i)
                break

        seed_mode = self._settings.default_seed_mode
        for i in range(self._seed_combo.count()):
            if self._seed_combo.itemData(i) == seed_mode:
                self._seed_combo.setCurrentIndex(i)
                break

        # Safety defaults
        self._write_safety_check.setChecked(self._settings.write_safety_config)

        posture = self._settings.default_safety_posture
        for i in range(self._posture_combo.count()):
            if self._posture_combo.itemData(i) == posture:
                self._posture_combo.setCurrentIndex(i)
                break

        # Appearance
        font_size = self._settings.font_size_preference
        for i in range(self._font_size_combo.count()):
            if self._font_size_combo.itemData(i) == font_size:
                self._font_size_combo.setCurrentIndex(i)
                break

        theme_pref = self._settings.theme_preference
        for i in range(self._theme_combo.count()):
            if self._theme_combo.itemData(i) == theme_pref:
                self._theme_combo.setCurrentIndex(i)
                break

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

    def _danger_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {STATUS_ERROR};
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: {RADIUS_SM}px;
                padding: {SPACE_SM}px {SPACE_LG}px;
                font-size: {FONT_SIZE_MD}px;
                font-weight: {FONT_WEIGHT_BOLD};
            }}
            QPushButton:hover {{
                background-color: #cc6666;
            }}
        """
