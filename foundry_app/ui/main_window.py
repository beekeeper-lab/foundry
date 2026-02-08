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

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------

STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
}

/* Sidebar */
#sidebar {
    background-color: #181825;
    border-right: 1px solid #313244;
}
#sidebar QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    font-size: 14px;
    color: #cdd6f4;
    padding: 8px 0;
}
#sidebar QListWidget::item {
    padding: 12px 20px;
    border-radius: 0;
}
#sidebar QListWidget::item:selected {
    background-color: #313244;
    color: #cba6f7;
    font-weight: bold;
}
#sidebar QListWidget::item:hover:!selected {
    background-color: #1e1e2e;
}

/* Brand label */
#brand-label {
    color: #cba6f7;
    font-size: 20px;
    font-weight: bold;
    padding: 20px 20px 12px 20px;
}

/* Content area */
#content-stack {
    background-color: #1e1e2e;
}

/* Placeholder screens */
.placeholder-screen {
    background-color: #1e1e2e;
}
.placeholder-screen QLabel {
    color: #6c7086;
    font-size: 16px;
}

/* Menu bar */
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
    padding: 2px;
}
QMenuBar::item:selected {
    background-color: #313244;
}
QMenu {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
}
QMenu::item:selected {
    background-color: #313244;
}
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
    heading.setStyleSheet("color: #cdd6f4;")

    subtitle = QLabel(description)
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setStyleSheet("color: #6c7086; font-size: 14px;")

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
        for _, title, desc in SCREENS:
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

        QMessageBox.about(
            self,
            "About Foundry",
            f"<h3>Foundry v{__version__}</h3>"
            "<p>Generate Claude Code project folders from reusable building blocks.</p>",
        )
