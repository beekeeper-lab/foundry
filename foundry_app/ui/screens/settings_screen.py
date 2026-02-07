"""Settings screen: persistent user preferences for the Foundry application."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.settings import AppSettings, load_settings, save_settings


class SettingsScreen(QWidget):
    """Application settings editor with save/reset support."""

    def __init__(
        self,
        inspector_stack: QStackedWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._inspector_stack = inspector_stack
        self._build_ui()
        self._load_and_populate()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        outer.addWidget(QLabel("<b>Settings</b>"))

        # Wrap the form in a scroll area so it remains usable on small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # -- 1. Paths ----------------------------------------------------------
        paths_group = QGroupBox("Paths")
        paths_layout = QVBoxLayout(paths_group)

        # Library root
        lib_row = QHBoxLayout()
        lib_row.addWidget(QLabel("Library root:"))
        self._library_root_edit = QLineEdit()
        self._library_root_edit.setPlaceholderText("Path to ai-team-library root...")
        lib_row.addWidget(self._library_root_edit, stretch=1)
        self._btn_browse_library = QPushButton("Browse...")
        self._btn_browse_library.clicked.connect(self._on_browse_library)
        lib_row.addWidget(self._btn_browse_library)
        paths_layout.addLayout(lib_row)

        # Workspace root
        ws_row = QHBoxLayout()
        ws_row.addWidget(QLabel("Workspace root:"))
        self._workspace_root_edit = QLineEdit()
        self._workspace_root_edit.setPlaceholderText("Default output directory...")
        ws_row.addWidget(self._workspace_root_edit, stretch=1)
        self._btn_browse_workspace = QPushButton("Browse...")
        self._btn_browse_workspace.clicked.connect(self._on_browse_workspace)
        ws_row.addWidget(self._btn_browse_workspace)
        paths_layout.addLayout(ws_row)

        form_layout.addWidget(paths_group)

        # -- 2. Editor Preferences ---------------------------------------------
        editor_group = QGroupBox("Editor Preferences")
        editor_layout = QVBoxLayout(editor_group)

        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font size:"))
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(8, 24)
        self._font_size_spin.setValue(11)
        font_row.addWidget(self._font_size_spin)
        font_row.addStretch()
        editor_layout.addLayout(font_row)

        tab_row = QHBoxLayout()
        tab_row.addWidget(QLabel("Tab width:"))
        self._tab_width_spin = QSpinBox()
        self._tab_width_spin.setRange(2, 8)
        self._tab_width_spin.setValue(4)
        tab_row.addWidget(self._tab_width_spin)
        tab_row.addStretch()
        editor_layout.addLayout(tab_row)

        form_layout.addWidget(editor_group)

        # -- 3. Validation -----------------------------------------------------
        validation_group = QGroupBox("Validation")
        validation_layout = QVBoxLayout(validation_group)

        strictness_row = QHBoxLayout()
        strictness_row.addWidget(QLabel("Default strictness:"))
        self._strictness_combo = QComboBox()
        self._strictness_combo.addItems(["light", "standard", "strict"])
        strictness_row.addWidget(self._strictness_combo)
        strictness_row.addStretch()
        validation_layout.addLayout(strictness_row)

        form_layout.addWidget(validation_group)

        # -- 4. Git Integration ------------------------------------------------
        git_group = QGroupBox("Git Integration")
        git_layout = QVBoxLayout(git_group)

        self._git_auto_init_chk = QCheckBox("Auto git init on export")
        self._git_auto_init_chk.setChecked(False)
        git_layout.addWidget(self._git_auto_init_chk)

        form_layout.addWidget(git_group)

        # -- 5. Recent Items ---------------------------------------------------
        recent_group = QGroupBox("Recent Items")
        recent_layout = QVBoxLayout(recent_group)

        recent_layout.addWidget(QLabel("Recent libraries:"))
        self._recent_libraries_list = QListWidget()
        self._recent_libraries_list.setMaximumHeight(120)
        self._recent_libraries_list.setSelectionMode(
            QListWidget.SelectionMode.NoSelection
        )
        recent_layout.addWidget(self._recent_libraries_list)

        self._btn_clear_libraries = QPushButton("Clear Recent Libraries")
        self._btn_clear_libraries.clicked.connect(self._on_clear_recent_libraries)
        recent_layout.addWidget(self._btn_clear_libraries)

        recent_layout.addWidget(QLabel("Recent projects:"))
        self._recent_projects_list = QListWidget()
        self._recent_projects_list.setMaximumHeight(160)
        self._recent_projects_list.setSelectionMode(
            QListWidget.SelectionMode.NoSelection
        )
        recent_layout.addWidget(self._recent_projects_list)

        self._btn_clear_projects = QPushButton("Clear Recent Projects")
        self._btn_clear_projects.clicked.connect(self._on_clear_recent_projects)
        recent_layout.addWidget(self._btn_clear_projects)

        form_layout.addWidget(recent_group)

        form_layout.addStretch()

        scroll.setWidget(form_container)
        outer.addWidget(scroll, stretch=1)

        # -- 6. Actions --------------------------------------------------------
        actions_row = QHBoxLayout()

        self._btn_save = QPushButton("Save")
        self._btn_save.clicked.connect(self._on_save)
        actions_row.addWidget(self._btn_save)

        self._btn_reset = QPushButton("Reset to Defaults")
        self._btn_reset.clicked.connect(self._on_reset)
        actions_row.addWidget(self._btn_reset)

        actions_row.addStretch()
        outer.addLayout(actions_row)

    # -- Data population -------------------------------------------------------

    def _load_and_populate(self) -> None:
        """Load settings from disk and populate all form fields."""
        settings = load_settings()
        self._populate_form(settings)

    def _populate_form(self, settings: AppSettings) -> None:
        """Write an AppSettings instance into every form widget."""
        self._library_root_edit.setText(settings.library_root)
        self._workspace_root_edit.setText(settings.workspace_root)
        self._font_size_spin.setValue(settings.editor_font_size)
        self._tab_width_spin.setValue(settings.editor_tab_width)

        # Set combo box to matching strictness value
        idx = self._strictness_combo.findText(settings.validation_strictness)
        if idx >= 0:
            self._strictness_combo.setCurrentIndex(idx)
        else:
            self._strictness_combo.setCurrentText("standard")

        self._git_auto_init_chk.setChecked(settings.git_auto_init)

        # Recent lists
        self._recent_libraries_list.clear()
        for path in settings.recent_libraries:
            self._recent_libraries_list.addItem(path)

        self._recent_projects_list.clear()
        for path in settings.recent_projects:
            self._recent_projects_list.addItem(path)

    def _build_settings_from_form(self) -> AppSettings:
        """Read current form state and return a validated AppSettings."""
        # Preserve recent lists from the list widgets
        recent_libs = [
            self._recent_libraries_list.item(i).text()
            for i in range(self._recent_libraries_list.count())
        ]
        recent_projs = [
            self._recent_projects_list.item(i).text()
            for i in range(self._recent_projects_list.count())
        ]

        return AppSettings(
            library_root=self._library_root_edit.text().strip(),
            workspace_root=self._workspace_root_edit.text().strip(),
            editor_font_size=self._font_size_spin.value(),
            editor_tab_width=self._tab_width_spin.value(),
            validation_strictness=self._strictness_combo.currentText(),
            git_auto_init=self._git_auto_init_chk.isChecked(),
            recent_libraries=recent_libs,
            recent_projects=recent_projs,
        )

    # -- Slots -----------------------------------------------------------------

    def _on_browse_library(self) -> None:
        current = self._library_root_edit.text().strip()
        start_dir = current if current else str(Path.home())
        path = QFileDialog.getExistingDirectory(
            self, "Select Library Root", start_dir
        )
        if path:
            self._library_root_edit.setText(path)

    def _on_browse_workspace(self) -> None:
        current = self._workspace_root_edit.text().strip()
        start_dir = current if current else str(Path.home())
        path = QFileDialog.getExistingDirectory(
            self, "Select Workspace Root", start_dir
        )
        if path:
            self._workspace_root_edit.setText(path)

    def _on_save(self) -> None:
        settings = self._build_settings_from_form()
        try:
            save_settings(settings)
            QMessageBox.information(
                self,
                "Settings Saved",
                "Your settings have been saved successfully.",
            )
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Could not save settings:\n{exc}",
            )

    def _on_reset(self) -> None:
        confirm = QMessageBox.question(
            self,
            "Reset Settings",
            "Reset all settings to their default values?\n\n"
            "This will also clear recent items.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        defaults = AppSettings()
        self._populate_form(defaults)
        try:
            save_settings(defaults)
        except OSError:
            pass  # best-effort; form is already reset

    def _on_clear_recent_libraries(self) -> None:
        self._recent_libraries_list.clear()

    def _on_clear_recent_projects(self) -> None:
        self._recent_projects_list.clear()
