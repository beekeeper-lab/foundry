"""Foundry GUI entry point — launched by ``uv run foundry``."""

from __future__ import annotations

import sys


def main() -> None:
    """Bootstrap the QApplication and show the main window."""
    from PySide6.QtWidgets import QApplication

    from foundry_app.core.logging_config import setup_logging
    from foundry_app.core.settings import FoundrySettings
    from foundry_app.ui.main_window import MainWindow

    log_path = setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("Foundry")
    app.setOrganizationName("Foundry")

    settings = FoundrySettings()
    window = MainWindow(settings=settings)
    window.show()

    # Deferred import keeps startup fast; log for diagnostics
    import logging

    logging.getLogger(__name__).info("Foundry GUI started — log file: %s", log_path)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
