"""Main application window: three-pane layout with navigation, content, and inspector."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from foundry_app.core.models import LibraryIndex
from foundry_app.core.settings import add_recent_library, load_settings, save_settings
from foundry_app.services.library_indexer import build_library_index


class MainWindow(QMainWindow):
    """Foundry main window with three-pane layout."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Foundry")
        self.resize(1280, 800)

        self._library_root: Path | None = None
        self._library_index: LibraryIndex | None = None
        self._screens: dict[str, QWidget] = {}

        self._build_toolbar()
        self._build_layout()
        self.statusBar().showMessage("Ready — Open a library to get started")

        # Auto-load last library from settings
        self._try_auto_load_library()

    # -- Toolbar --

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Open Library button with recent-libraries dropdown
        self._lib_button = QToolButton()
        self._lib_button.setText("Open Library")
        self._lib_button.setShortcut(QKeySequence("Ctrl+O"))
        self._lib_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self._lib_button.clicked.connect(self._on_open_library)
        self._lib_menu = QMenu(self._lib_button)
        self._lib_button.setMenu(self._lib_menu)
        self._rebuild_recent_libraries_menu()
        toolbar.addWidget(self._lib_button)

        toolbar.addSeparator()

        self._action_new_project = toolbar.addAction("New Project")
        self._action_new_project.setShortcut(QKeySequence("Ctrl+N"))
        self._action_new_project.triggered.connect(self._on_new_project)
        self._action_new_project.setEnabled(False)

        toolbar.addSeparator()

        self._action_generate = toolbar.addAction("Generate")
        self._action_generate.setShortcut(QKeySequence("Ctrl+G"))
        self._action_generate.triggered.connect(self._on_generate)
        self._action_generate.setEnabled(False)

        self._action_export = toolbar.addAction("Export")
        self._action_export.setShortcut(QKeySequence("Ctrl+E"))
        self._action_export.triggered.connect(self._on_export)
        self._action_export.setEnabled(False)

        toolbar.addSeparator()

        self._action_settings = toolbar.addAction("Settings")
        self._action_settings.setShortcut(QKeySequence("Ctrl+,"))
        self._action_settings.triggered.connect(self._on_settings)

    # -- Layout --

    def _build_layout(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: navigation sidebar
        self._nav_tree = QTreeWidget()
        self._nav_tree.setHeaderLabel("Navigation")
        self._nav_tree.setMinimumWidth(200)
        self._nav_tree.currentItemChanged.connect(self._on_nav_changed)
        splitter.addWidget(self._nav_tree)

        # Center: content area (stacked widget for different screens)
        self._content_stack = QStackedWidget()
        self._placeholder_label = QLabel("Open a library to browse personas, stacks, and templates.")
        self._placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder_label.setWordWrap(True)
        self._content_stack.addWidget(self._placeholder_label)
        splitter.addWidget(self._content_stack)

        # Right: inspector / preview panel
        self._inspector_stack = QStackedWidget()
        inspector_placeholder = QLabel("Select an item to see details.")
        inspector_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inspector_placeholder.setWordWrap(True)
        self._inspector_stack.addWidget(inspector_placeholder)
        splitter.addWidget(self._inspector_stack)

        splitter.setSizes([220, 600, 380])

        self.setCentralWidget(splitter)

    # -- Navigation tree population --

    def _populate_nav_tree(self) -> None:
        self._nav_tree.clear()

        # Library section
        library_item = QTreeWidgetItem(["Library"])
        library_item.setData(0, Qt.ItemDataRole.UserRole, ("section", "library"))

        personas_item = QTreeWidgetItem(["Personas"])
        personas_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "personas"))
        library_item.addChild(personas_item)

        stacks_item = QTreeWidgetItem(["Stacks"])
        stacks_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "stacks"))
        library_item.addChild(stacks_item)

        templates_item = QTreeWidgetItem(["Templates (cross-cut)"])
        templates_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "templates"))
        library_item.addChild(templates_item)

        hooks_item = QTreeWidgetItem(["Hooks"])
        hooks_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "hooks"))
        library_item.addChild(hooks_item)

        workflows_item = QTreeWidgetItem(["Workflows"])
        workflows_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "workflows"))
        library_item.addChild(workflows_item)

        skills_item = QTreeWidgetItem(["Skills / Commands"])
        skills_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "skills_commands"))
        library_item.addChild(skills_item)

        self._nav_tree.addTopLevelItem(library_item)
        library_item.setExpanded(True)

        # Project Builder section
        builder_item = QTreeWidgetItem(["Project Builder"])
        builder_item.setData(0, Qt.ItemDataRole.UserRole, ("section", "builder"))

        wizard_item = QTreeWidgetItem(["New Project Wizard"])
        wizard_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "wizard"))
        builder_item.addChild(wizard_item)

        composition_item = QTreeWidgetItem(["Composition Editor"])
        composition_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "composition"))
        builder_item.addChild(composition_item)

        generate_item = QTreeWidgetItem(["Generate"])
        generate_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "generate"))
        builder_item.addChild(generate_item)

        export_item = QTreeWidgetItem(["Export"])
        export_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "export"))
        builder_item.addChild(export_item)

        self._nav_tree.addTopLevelItem(builder_item)
        builder_item.setExpanded(True)

        # History section
        history_item = QTreeWidgetItem(["History"])
        history_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "history"))
        self._nav_tree.addTopLevelItem(history_item)

        # Settings section
        settings_item = QTreeWidgetItem(["Settings"])
        settings_item.setData(0, Qt.ItemDataRole.UserRole, ("nav", "settings"))
        self._nav_tree.addTopLevelItem(settings_item)

    # -- Recent libraries menu --

    def _rebuild_recent_libraries_menu(self) -> None:
        """Rebuild the recent-libraries dropdown from settings."""
        self._lib_menu.clear()
        settings = load_settings()
        recent = settings.recent_libraries

        if not recent:
            action = self._lib_menu.addAction("(no recent libraries)")
            action.setEnabled(False)
            return

        for lib_path_str in recent:
            label = Path(lib_path_str).name or lib_path_str
            action = self._lib_menu.addAction(label)
            action.setToolTip(lib_path_str)
            action.triggered.connect(lambda checked, p=lib_path_str: self._on_open_recent_library(p))

        self._lib_menu.addSeparator()
        clear_action = self._lib_menu.addAction("Clear History")
        clear_action.triggered.connect(self._on_clear_library_history)

    def _on_open_recent_library(self, path_str: str) -> None:
        """Load a library from the recent list."""
        library_path = Path(path_str)
        if not library_path.is_dir():
            QMessageBox.warning(
                self,
                "Library Not Found",
                f"The library directory no longer exists:\n{library_path}",
            )
            return
        if not self.load_library(library_path):
            QMessageBox.warning(
                self,
                "Invalid Library",
                f"No 'personas/' directory found in:\n{library_path}",
            )
            return
        self._show_screen("personas")

    def _on_clear_library_history(self) -> None:
        """Clear the recent libraries list from settings."""
        settings = load_settings()
        settings = settings.model_copy(update={"recent_libraries": []})
        save_settings(settings)
        self._rebuild_recent_libraries_menu()

    # -- Auto-load --

    def _try_auto_load_library(self) -> None:
        """Attempt to load the last-used library from settings."""
        settings = load_settings()
        lib_root = settings.library_root
        if not lib_root:
            return
        library_path = Path(lib_root)
        if not library_path.is_dir() or not (library_path / "personas").is_dir():
            return
        self.load_library(library_path)
        self._show_screen("personas")

    # -- Slots --

    def _on_open_library(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Open Library Root", str(Path.home())
        )
        if not path:
            return

        library_path = Path(path)
        if not self.load_library(library_path):
            QMessageBox.warning(
                self,
                "Invalid Library",
                f"No 'personas/' directory found in:\n{library_path}\n\n"
                "Please select a valid ai-team-library root.",
            )
            return

        # Show persona browser by default
        self._show_screen("personas")

    def _on_nav_changed(self, current: QTreeWidgetItem | None, _prev: QTreeWidgetItem | None) -> None:
        if current is None:
            return
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if data is None:
            return
        kind, key = data
        if kind == "nav":
            self._show_screen(key)

    def _on_new_project(self) -> None:
        self._show_screen("wizard")

    def _on_generate(self) -> None:
        self._show_screen("generate")

    def _on_export(self) -> None:
        self._show_screen("export")

    def _on_settings(self) -> None:
        self._show_screen("settings")

    # -- Screen management --

    def _invalidate_screens(self) -> None:
        """Remove all cached screens so they get rebuilt with current library data."""
        for name, widget in self._screens.items():
            self._content_stack.removeWidget(widget)
            widget.deleteLater()
        self._screens.clear()

    def _show_screen(self, screen_name: str) -> None:
        """Switch the content area to the named screen."""
        if screen_name not in self._screens:
            widget = self._create_screen(screen_name)
            if widget is None:
                return
            self._screens[screen_name] = widget
            self._content_stack.addWidget(widget)

        self._content_stack.setCurrentWidget(self._screens[screen_name])

        # Wire wizard output to generate screen
        if screen_name == "generate":
            wizard = self._screens.get("wizard")
            generate_screen = self._screens[screen_name]
            if (
                wizard is not None
                and hasattr(wizard, "last_composition_path")
                and wizard.last_composition_path is not None
                and hasattr(generate_screen, "set_wizard_result")
            ):
                generate_screen.set_wizard_result(
                    wizard.last_composition_path,
                    wizard.last_project_path,
                )

        # Wire wizard output to export screen source
        if screen_name == "export":
            wizard = self._screens.get("wizard")
            export_screen = self._screens[screen_name]
            if (
                wizard is not None
                and hasattr(wizard, "last_project_path")
                and wizard.last_project_path is not None
                and hasattr(export_screen, "set_source_path")
            ):
                export_screen.set_source_path(wizard.last_project_path)

    def _create_screen(self, screen_name: str) -> QWidget | None:
        """Lazy-create a screen widget by name."""
        # These screens don't need a library loaded
        if self._library_root is None and screen_name not in ("wizard", "settings", "history"):
            return None

        if screen_name == "settings":
            from foundry_app.ui.screens.settings_screen import SettingsScreen
            return SettingsScreen(self._inspector_stack, self)

        if screen_name == "history":
            from foundry_app.ui.screens.history_screen import HistoryScreen
            return HistoryScreen(self._inspector_stack, self)

        if screen_name == "personas":
            from foundry_app.ui.screens.library.persona_browser import PersonaBrowser
            screen = PersonaBrowser(self._library_root, self._library_index, self._inspector_stack)
            return screen

        if screen_name == "stacks":
            from foundry_app.ui.screens.library.stack_browser import StackBrowser
            screen = StackBrowser(self._library_root, self._library_index, self._inspector_stack)
            return screen

        if screen_name == "templates":
            from foundry_app.ui.screens.library.template_browser import TemplateBrowser
            screen = TemplateBrowser(self._library_root, self._library_index, self._inspector_stack)
            return screen

        if screen_name == "hooks":
            from foundry_app.ui.screens.library.hooks_browser import HooksBrowser
            return HooksBrowser(self._library_root, self._library_index, self._inspector_stack)

        if screen_name == "workflows":
            from foundry_app.ui.screens.library.workflows_browser import WorkflowsBrowser
            return WorkflowsBrowser(self._library_root, self._library_index, self._inspector_stack)

        if screen_name == "skills_commands":
            from foundry_app.ui.screens.library.skills_commands_browser import SkillsCommandsBrowser
            return SkillsCommandsBrowser(self._library_root, self._library_index, self._inspector_stack)

        if screen_name == "composition":
            from foundry_app.ui.screens.builder.composition_editor import CompositionEditor
            return CompositionEditor(self._library_root, self._library_index, self._inspector_stack, self)

        if screen_name == "wizard":
            from foundry_app.ui.screens.builder.wizard import ProjectWizard
            screen = ProjectWizard(
                self._library_root,
                self._library_index,
                self._inspector_stack,
                self,
            )
            return screen

        if screen_name == "generate":
            from foundry_app.ui.screens.builder.generate_screen import GenerateScreen
            return GenerateScreen(self._inspector_stack, self)

        if screen_name == "export":
            from foundry_app.ui.screens.builder.export_screen import ExportScreen
            return ExportScreen(self._inspector_stack, self)

        return None

    # -- Public API for child screens --

    @property
    def library_root(self) -> Path | None:
        return self._library_root

    @property
    def library_index(self) -> LibraryIndex | None:
        return self._library_index

    def refresh_library_index(self) -> None:
        if self._library_root:
            self._library_index = build_library_index(self._library_root)

    def show_screen(self, screen_name: str) -> None:
        """Public API: switch to a named screen."""
        self._show_screen(screen_name)

    def load_library(self, library_path: Path) -> bool:
        """Programmatically load a library. Returns True on success."""
        personas_dir = library_path / "personas"
        if not personas_dir.is_dir():
            return False

        self._library_root = library_path
        self._library_index = build_library_index(library_path)
        self._invalidate_screens()
        self._populate_nav_tree()
        self._action_new_project.setEnabled(True)

        settings = load_settings()
        settings = add_recent_library(settings, str(library_path))
        settings = settings.model_copy(update={"library_root": str(library_path)})
        save_settings(settings)
        self._rebuild_recent_libraries_menu()

        self.statusBar().showMessage(
            f"Library loaded: {library_path.name} "
            f"({len(self._library_index.personas)} personas, "
            f"{len(self._library_index.stacks)} stacks)"
        )
        return True

    def enable_generate(self, enabled: bool = True) -> None:
        self._action_generate.setEnabled(enabled)

    def enable_export(self, enabled: bool = True) -> None:
        self._action_export.setEnabled(enabled)
