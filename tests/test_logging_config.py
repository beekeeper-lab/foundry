"""Tests for foundry_app.core.logging_config — rotating file handler setup."""

import logging
from logging.handlers import RotatingFileHandler
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from foundry_app.core.logging_config import (
    LOG_BACKUP_COUNT,
    LOG_MAX_BYTES,
    setup_logging,
)

_app = QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _isolate_log_dir(tmp_path):
    """Route log files to tmp_path instead of real QStandardPaths location."""
    with patch(
        "foundry_app.core.logging_config.QStandardPaths.writableLocation",
        return_value=str(tmp_path),
    ):
        yield


class TestSetupLogging:
    def setup_method(self):
        """Reset root logger handlers before each test."""
        root = logging.getLogger()
        for h in root.handlers[:]:
            h.close()
            root.removeHandler(h)

    def test_returns_path(self):
        path = setup_logging()
        assert path.name == "foundry.log"
        assert path.parent.exists()

    def test_creates_handlers(self):
        setup_logging()
        root = logging.getLogger()
        # console + file = 2 handlers
        assert len(root.handlers) >= 2

    def test_idempotent(self):
        setup_logging()
        count = len(logging.getLogger().handlers)
        setup_logging()
        assert len(logging.getLogger().handlers) == count

    def test_custom_log_file(self):
        path = setup_logging(log_file="test-run.log")
        assert path.name == "test-run.log"

    def test_rotating_handler_config(self):
        root = logging.getLogger()
        # pytest may re-add its log-capture handlers after setup_method;
        # check if they exist and clear again before testing
        pre = root.handlers[:]
        for h in pre:
            h.close()
            root.removeHandler(h)
        setup_logging()
        rh = [h for h in root.handlers if isinstance(h, RotatingFileHandler)]
        assert len(rh) == 1
        assert rh[0].maxBytes == LOG_MAX_BYTES
        assert rh[0].backupCount == LOG_BACKUP_COUNT

    def test_log_level_applied(self):
        setup_logging(level=logging.DEBUG)
        assert logging.getLogger().level == logging.DEBUG
