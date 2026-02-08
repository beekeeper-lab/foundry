"""Foundry main window — sidebar navigation with stacked widget for screens."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.settings import FoundrySettings
from foundry_app.ui import theme
from foundry_app.ui.widgets.branded_empty_state import BrandedEmptyState

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
#sidebar QListWidget {{{{
    background-color: transparent;
    border: none;
    outline: none;
    font-size: {theme.FONT_SIZE_MD}px;
    color: {theme.TEXT_PRIMARY};
    padding: {theme.SPACE_SM}px 0;
}}}}
#sidebar QListWidget::item {{{{
    padding: {theme.SPACE_MD}px {theme.SPACE_XL}px;
    border-radius: 0;
}}}}
#sidebar QListWidget::item:selected {{{{
    background-color: {theme.BG_SURFACE};
    color: {theme.ACCENT_PRIMARY};
    font-weight: {theme.FONT_WEIGHT_BOLD};
    border-left: 3px solid {theme.ACCENT_PRIMARY};
}}}}
#sidebar QListWidget::item:hover:!selected {{{{
    background-color: {theme.BG_BASE};
    color: {theme.ACCENT_PRIMARY_HOVER};
}}}}

/* Brand label — brass accent header */
#brand-label {{{{
    color: {theme.ACCENT_PRIMARY};
    font-size: {theme.FONT_SIZE_XL}px;
    font-weight: {theme.FONT_WEIGHT_BOLD};
    padding: {theme.SPACE_XL}px {theme.SPACE_XL}px {theme.SPACE_MD}px {theme.SPACE_XL}px;
    border-bottom: 1px solid {theme.BORDER_SUBTLE};
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

/* Menu bar */
QMenuBar {{{{
    background-color: {theme.BG_INSET};
    color: {theme.TEXT_PRIMARY};
    border-bottom: 1px solid {theme.BORDER_DEFAULT};
    padding: 2px;
}}}}
QMenuBar::item:selected {{{{
    background-color: {theme.BG_SURFACE};
}}}}
QMenu {{{{
    background-color: {theme.BG_SURFACE};
    color: {theme.TEXT_PRIMARY};
    border: 1px solid {theme.BORDER_DEFAULT};
}}}}
QMenu::item:selected {{{{
    background-color: {theme.BG_OVERLAY};
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

SCREENS: list[tuple[str, str, str]] = [
    ("Builder", "Project Builder", "Create a new Claude Code project from building blocks."),
    ("Library", "Library Manager", "Browse and explore the library structure."),
    ("History", "Generation History", "View past generation runs and their manifests."),
    ("Settings", "Settings", "Configure library paths, workspace root, and preferences."),
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

        self._build_menu_bar()
        self._build_ui()
        self._restore_geometry()
        logger.info("MainWindow initialised")

    # -- UI construction ---------------------------------------------------

    def _build_menu_bar(self) -> None:
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About Foundry", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

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

        brand = QLabel("Foundry")
        brand.setObjectName("brand-label")
        sidebar_layout.addWidget(brand)

        self._nav_list = QListWidget()
        for label, _, _ in SCREENS:
            item = QListWidgetItem(label)
            self._nav_list.addItem(item)
        sidebar_layout.addWidget(self._nav_list, stretch=1)
        sidebar_layout.addStretch(0)

        # --- Content stack ---
        self._stack = QStackedWidget()
        self._stack.setObjectName("content-stack")
        for label, title, desc in SCREENS:
            if label == "Builder":
                self._stack.addWidget(BrandedEmptyState(
                    heading="Welcome to Foundry",
                    description="Create a new Claude Code project from reusable building blocks.\n"
                    "Select a composition to get started.",
                ))
            else:
                self._stack.addWidget(_placeholder(title, desc))

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self._stack, stretch=1)

        # Wire navigation
        self._nav_list.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav_list.setCurrentRow(0)

    # -- Public API --------------------------------------------------------

    @property
    def stack(self) -> QStackedWidget:
        """Access the stacked widget to replace placeholder screens later."""
        return self._stack

    @property
    def nav_list(self) -> QListWidget:
        """Access the navigation list for programmatic control."""
        return self._nav_list

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

    # -- Slots -------------------------------------------------------------

    def _show_about(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        from foundry_app import __version__
        from foundry_app.core.resources import logo_icon_path

        logo_html = ""
        logo_file = logo_icon_path()
        if logo_file.is_file():
            logo_html = f'<p align="center"><img src="{logo_file}" width="64" height="64"></p>'

        QMessageBox.about(
            self,
            "About Foundry",
            f"{logo_html}"
            f"<h3 style='color: {theme.ACCENT_PRIMARY};'>Foundry v{__version__}</h3>"
            f"<p style='color: {theme.TEXT_PRIMARY};'>"
            "Generate Claude Code project folders from reusable building blocks.</p>",
        )
