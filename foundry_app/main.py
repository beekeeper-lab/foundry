"""Foundry application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from foundry_app.ui.main_window import MainWindow


def main() -> None:
    """Launch the Foundry desktop application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
