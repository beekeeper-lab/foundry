"""Foundry main window — sidebar navigation with stacked widget for screens."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import CompositionSpec
from foundry_app.core.settings import FoundrySettings
from foundry_app.ui import theme
from foundry_app.ui.generation_worker import GenerationWorker
from foundry_app.ui.icons import load_icon
from foundry_app.ui.screens.builder_screen import BuilderScreen
from foundry_app.ui.screens.generation_progress import GenerationProgressScreen
from foundry_app.ui.screens.history_screen import HistoryScreen
from foundry_app.ui.screens.library_manager import LibraryManagerScreen
from foundry_app.ui.screens.settings_screen import SettingsScreen

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stylesheet — built from centralised theme constants
# ---------------------------------------------------------------------------

STYLESHEET = f"""
QMainWindow {{{{
    background-color: {theme.BG_BASE};
}}}}

/* Sidebar — darker recessed panel, control-room feel */
#sidebar {{{{
    background-color: {theme.BG_INSET};
    border-right: 1px solid {theme.BORDER_DEFAULT};
}}}}

/* Nav buttons — icon-over-text, large targets */
#sidebar QToolButton {{{{
    background-color: transparent;
    border: none;
    border-left: 3px solid transparent;
    color: {theme.TEXT_PRIMARY};
    font-size: {theme.FONT_SIZE_SM}px;
    padding: {theme.SPACE_MD}px {theme.SPACE_SM}px;
    margin: 2px 0;
    text-align: center;
}}}}
#sidebar QToolButton:hover {{{{
    background-color: {theme.BG_BASE};
    color: {theme.ACCENT_PRIMARY_HOVER};
}}}}
#sidebar QToolButton:checked {{{{
    background-color: {theme.BG_OVERLAY};
    color: {theme.ACCENT_PRIMARY};
    font-weight: {theme.FONT_WEIGHT_BOLD};
    border-left: 3px solid {theme.ACCENT_PRIMARY};
}}}}
#sidebar QToolButton:focus {{{{
    outline: none;
    border-left: 3px solid {theme.ACCENT_SECONDARY};
}}}}
#sidebar QToolButton:checked:focus {{{{
    border-left: 3px solid {theme.ACCENT_PRIMARY};
}}}}

/* Sidebar footer — version & info */
#sidebar-footer {{{{
    border-top: 1px solid {theme.BORDER_SUBTLE};
    padding: {theme.SPACE_SM}px {theme.SPACE_LG}px;
}}}}
#sidebar-footer QLabel {{{{
    color: {theme.TEXT_DISABLED};
    font-size: {theme.FONT_SIZE_XS}px;
}}}}
#sidebar-footer QPushButton {{{{
    background: transparent;
    border: none;
    color: {theme.TEXT_DISABLED};
    font-size: {theme.FONT_SIZE_XS}px;
    text-align: left;
    padding: {theme.SPACE_XS}px 0;
}}}}
#sidebar-footer QPushButton:hover {{{{
    color: {theme.ACCENT_PRIMARY_HOVER};
}}}}

/* Content area */
#content-stack {{{{
    background-color: {theme.BG_BASE};
}}}}

/* Placeholder screens */
.placeholder-screen {{{{
    background-color: {theme.BG_BASE};
}}}}
.placeholder-screen QLabel {{{{
    color: {theme.TEXT_DISABLED};
    font-size: {theme.FONT_SIZE_LG}px;
}}}}

"""


# ---------------------------------------------------------------------------
# Placeholder screen factory
# ---------------------------------------------------------------------------

def _placeholder(title: str, description: str) -> QWidget:
    """Create a simple centered placeholder screen."""
    page = QWidget()
    page.setProperty("class", "placeholder-screen")
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    heading = QLabel(title)
    heading.setFont(QFont("", 22, QFont.Weight.Bold))
    heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
    heading.setStyleSheet(f"color: {theme.TEXT_PRIMARY};")

    subtitle = QLabel(description)
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setStyleSheet(
        f"color: {theme.TEXT_SECONDARY}; font-size: {theme.FONT_SIZE_MD}px;"
    )

    layout.addWidget(heading)
    layout.addWidget(subtitle)
    return page


# ---------------------------------------------------------------------------
# Screen registry
# ---------------------------------------------------------------------------

# (label, icon_name, screen_title, screen_description)
SCREENS: list[tuple[str, str, str, str]] = [
    ("Builder", "builder", "Project Builder",
     "Create a new Claude Code project from building blocks."),
    ("Library", "library", "Library Manager",
     "Browse and explore the library structure."),
    ("History", "history", "Generation History",
     "View past generation runs and their manifests."),
    ("Settings", "settings", "Settings",
     "Configure library paths, workspace root, and preferences."),
]


# ---------------------------------------------------------------------------
# MainWindow
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """Application shell with sidebar navigation and stacked content area."""

    def __init__(self, settings: FoundrySettings | None = None) -> None:
        super().__init__()
        self._settings = settings or FoundrySettings()
        self.setWindowTitle("Foundry")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(STYLESHEET)

        self._build_ui()
        self._setup_shortcuts()
        self._restore_geometry()
        self._apply_initial_settings()
        logger.info("MainWindow initialised")

    # -- UI construction ---------------------------------------------------

    def _setup_shortcuts(self) -> None:
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, theme.SPACE_LG, 0, theme.SPACE_SM)
        nav_layout.setSpacing(0)

        self._nav_buttons: list[QToolButton] = []
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        for i, (label, icon_name, _, _) in enumerate(SCREENS):
            btn = QToolButton()
            btn.setText(label)
            btn.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextUnderIcon
            )
            btn.setIconSize(QSize(36, 36))
            btn.setCheckable(True)
            btn.setProperty("class", "nav-button")
            btn.setFixedHeight(72)
            btn.setSizePolicy(btn.sizePolicy())
            btn.setMinimumWidth(180)
            try:
                btn.setIcon(load_icon(icon_name, color=theme.TEXT_SECONDARY, size=36))
            except FileNotFoundError:
                logger.warning("Icon not found for nav: %s", icon_name)
            self._nav_buttons.append(btn)
            self._nav_group.addButton(btn, i)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        sidebar_layout.addWidget(nav_container, stretch=1)

        # --- Sidebar footer: version + about ---
        footer = QWidget()
        footer.setObjectName("sidebar-footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(theme.SPACE_XS)

        from foundry_app import __version__

        about_btn = QPushButton(f"v{__version__}")
        about_btn.setObjectName("sidebar-about-btn")
        about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        about_btn.setToolTip("About Foundry")
        about_btn.clicked.connect(self._show_about)
        footer_layout.addWidget(about_btn)
        footer_layout.addStretch()
        sidebar_layout.addWidget(footer)

        # --- Content stack ---
        self._stack = QStackedWidget()
        self._stack.setObjectName("content-stack")

        # Index 0: Builder wizard
        self._builder_screen = BuilderScreen()
        self._builder_screen.generate_requested.connect(self._on_generate_requested)
        self._stack.addWidget(self._builder_screen)

        # Index 1: Library Manager
        self._library_screen = LibraryManagerScreen()
        self._stack.addWidget(self._library_screen)

        # Index 2: History
        self._history_screen = HistoryScreen()
        self._stack.addWidget(self._history_screen)

        # Index 3: Settings
        self._settings_screen = SettingsScreen(settings=self._settings)
        self._settings_screen.settings_changed.connect(self._on_library_root_changed)
        self._stack.addWidget(self._settings_screen)

        # Index 4: Generation progress (not in nav — shown programmatically)
        self._progress_screen = GenerationProgressScreen()
        self._progress_screen.back_requested.connect(self._on_back_to_builder)
        self._stack.addWidget(self._progress_screen)
        self._generation_worker: GenerationWorker | None = None

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self._stack, stretch=1)

        # Wire navigation
        self._nav_group.idClicked.connect(self._stack.setCurrentIndex)
        self._nav_buttons[0].setChecked(True)

    def _apply_initial_settings(self) -> None:
        """Pass persisted settings to screens on startup."""
        lib_root = self._settings.library_root
        if not lib_root:
            lib_root = self._detect_library_root()
            if lib_root:
                self._settings.library_root = lib_root
                self._settings.sync()
                logger.info("Auto-detected library root persisted: %s", lib_root)
        if lib_root:
            self._library_screen.set_library_root(lib_root)
            self._load_builder_library(lib_root)
            logger.info("Library root loaded: %s", lib_root)

        ws_root = self._settings.workspace_root
        if ws_root:
            self._history_screen.set_projects_root(ws_root)

    @staticmethod
    def _detect_library_root() -> str:
        """Auto-detect ai-team-library/ relative to the foundry_app package."""
        try:
            # foundry_app/ui/main_window.py -> foundry_app/ui -> foundry_app
            package_dir = Path(__file__).resolve().parent.parent
            candidate = package_dir.parent / "ai-team-library"
            if (candidate / "personas").is_dir():
                logger.info("Auto-detected library root: %s", candidate)
                return str(candidate)
        except Exception:
            logger.debug("Library auto-detection failed", exc_info=True)
        return ""

    def _on_library_root_changed(self, path: str) -> None:
        """React to library root changes from the settings screen."""
        self._library_screen.set_library_root(path)
        self._load_builder_library(path)
        logger.info("Library root updated: %s", path)

    def _load_builder_library(self, path: str) -> None:
        """Index the library and load it into the builder wizard."""
        from pathlib import Path

        from foundry_app.services.library_indexer import build_library_index

        lib_path = Path(path)
        if lib_path.is_dir():
            try:
                index = build_library_index(lib_path)
                self._builder_screen.set_library_index(index)
            except Exception:
                logger.warning("Failed to index library at %s", path, exc_info=True)

    # -- Public API --------------------------------------------------------

    @property
    def stack(self) -> QStackedWidget:
        """Access the stacked widget to replace placeholder screens later."""
        return self._stack

    @property
    def nav_buttons(self) -> list[QToolButton]:
        """Access the navigation buttons for programmatic control."""
        return self._nav_buttons

    @property
    def nav_group(self) -> QButtonGroup:
        """Access the navigation button group."""
        return self._nav_group

    @property
    def builder_screen(self) -> BuilderScreen:
        return self._builder_screen

    @property
    def library_screen(self) -> LibraryManagerScreen:
        return self._library_screen

    @property
    def history_screen(self) -> HistoryScreen:
        return self._history_screen

    @property
    def settings_screen(self) -> SettingsScreen:
        return self._settings_screen

    @property
    def progress_screen(self) -> GenerationProgressScreen:
        return self._progress_screen

    def replace_screen(self, index: int, widget: QWidget) -> None:
        """Replace a placeholder screen at *index* with a real widget."""
        old = self._stack.widget(index)
        self._stack.removeWidget(old)
        old.deleteLater()
        self._stack.insertWidget(index, widget)

    # -- Geometry persistence ----------------------------------------------

    def _restore_geometry(self) -> None:
        geo = self._settings.window_geometry
        if geo and not geo.isEmpty():
            self.restoreGeometry(geo)
        state = self._settings.window_state
        if state and not state.isEmpty():
            self.restoreState(state)

    def closeEvent(self, event) -> None:  # noqa: N802
        self._settings.window_geometry = self.saveGeometry()
        self._settings.window_state = self.saveState()
        self._settings.sync()
        logger.info("MainWindow closed — geometry saved")
        super().closeEvent(event)

    # -- Generation --------------------------------------------------------

    def _on_generate_requested(self, spec: CompositionSpec) -> None:
        """Handle generate button: switch to progress screen and start worker."""
        lib_root = self._settings.library_root
        if not lib_root:
            logger.warning("No library root configured — cannot generate")
            return

        # Switch to progress screen and start spinner
        self._progress_screen.start()
        self._stack.setCurrentWidget(self._progress_screen)

        # Launch generation on background thread
        self._generation_worker = GenerationWorker(spec, lib_root, parent=self)
        self._generation_worker.stage_progress.connect(self._on_stage_progress)
        self._generation_worker.finished_ok.connect(self._on_generation_ok)
        self._generation_worker.finished_err.connect(self._on_generation_err)
        self._generation_worker.start()
        logger.info("Generation worker started for project: %s", spec.project.name)

    def _on_stage_progress(self, stage_key: str, status: str, file_count: int) -> None:
        """Update progress screen with stage transitions."""
        if status == "running":
            self._progress_screen.mark_stage_running(stage_key)
        elif status == "done":
            self._progress_screen.mark_stage_done(stage_key, file_count)

    def _on_generation_ok(self, total_files: int, warnings: int, output_path: str) -> None:
        """Handle successful generation."""
        self._progress_screen.set_output_path(output_path)
        self._progress_screen.finish(total_files=total_files, warnings=warnings)
        logger.info("Generation complete: %d files at %s", total_files, output_path)

    def _on_generation_err(self, message: str) -> None:
        """Handle generation failure."""
        self._progress_screen.finish_with_error(message)
        logger.error("Generation failed: %s", message)

    def _on_back_to_builder(self) -> None:
        """Return to the builder screen from the progress screen."""
        self._stack.setCurrentIndex(0)
        self._nav_buttons[0].setChecked(True)

    # -- Slots -------------------------------------------------------------

    def _show_about(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        from foundry_app import __version__
        from foundry_app.core.resources import logo_icon_path

        logo_html = ""
        logo_file = logo_icon_path()
        if logo_file.is_file():
            logo_html = f'<p align="center"><img src="{logo_file}" width="64" height="64"></p>'

        # About dialog uses a native QMessageBox with a light background,
        # so use dark text instead of theme.TEXT_PRIMARY (which is light).
        _about_text = "#2a2a2a"
        _about_bold = theme.ACCENT_PRIMARY
        QMessageBox.about(
            self,
            "About Foundry",
            f"{logo_html}"
            f"<h3 style='color: {theme.ACCENT_PRIMARY};'>Foundry v{__version__}</h3>"
            f"<p style='color: {_about_text};'>"
            "Foundry is a desktop application for generating fully configured "
            "Claude Code project folders from a library of reusable building blocks. "
            "Instead of hand-crafting project scaffolding from scratch each time, "
            "compose a project by selecting from curated "
            f"<b style='color: {_about_bold};'>personas</b>, "
            f"<b style='color: {_about_bold};'>technology stacks</b>, and "
            f"<b style='color: {_about_bold};'>templates</b> that encode team "
            "conventions and best practices.</p>"
            f"<p style='color: {_about_text};'>"
            "A Foundry composition defines the AI team personas that will collaborate "
            "on your project, the language and framework stack to target, and the "
            "directory templates that seed your repository with the right structure. "
            "When you generate, Foundry compiles these selections into a complete "
            "Claude Code workspace\u2014ready for agents to pick up and start building.</p>"
            f"<p style='color: {_about_text};'>"
            "Built with PySide6 and Python. Licensed under MIT.</p>",
        )
