"""Foundry GUI entry point — launched by ``uv run foundry``."""

from __future__ import annotations

import sys


def main() -> None:
    """Bootstrap the QApplication and show the main window."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QFont, QIcon, QPixmap
    from PySide6.QtWidgets import QApplication, QSplashScreen

    from foundry_app import __version__
    from foundry_app.core.logging_config import setup_logging
    from foundry_app.core.resources import logo_icon_path, splash_image_path
    from foundry_app.core.settings import FoundrySettings
    from foundry_app.ui.main_window import MainWindow

    log_path = setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("Foundry")
    app.setOrganizationName("Foundry")

    # -- Application icon ------------------------------------------------------
    icon_file = logo_icon_path()
    if icon_file.is_file():
        app.setWindowIcon(QIcon(str(icon_file)))

    # -- Splash screen -----------------------------------------------------
    splash: QSplashScreen | None = None
    img_path = splash_image_path()
    if img_path.is_file():
        pixmap = QPixmap(str(img_path)).scaled(
            720, 405,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        splash = QSplashScreen(pixmap)
        splash.setFont(QFont("", 12))
        splash.showMessage(
            f"Foundry v{__version__}",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            QColor(205, 214, 244),
        )
        splash.show()
        app.processEvents()

    # -- Main window -------------------------------------------------------
    settings = FoundrySettings()
    window = MainWindow(settings=settings)
    window.show()

    if splash is not None:
        splash.finish(window)

    # Deferred import keeps startup fast; log for diagnostics
    import logging

    logging.getLogger(__name__).info("Foundry GUI started — log file: %s", log_path)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
