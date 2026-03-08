"""Shared test fixtures.

Provides a session-scoped QApplication so that all UI tests share a single
instance, avoiding Shiboken segfaults when Qt objects from one test module
are garbage-collected while another module constructs widgets.
"""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication instance."""
    app = QApplication.instance() or QApplication([])
    yield app
