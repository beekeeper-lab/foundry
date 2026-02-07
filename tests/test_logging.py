"""Tests for foundry_app.core.logging: setup_logging configuration."""

from __future__ import annotations

import logging
from pathlib import Path

import foundry_app.core.logging as flog
from foundry_app.core.logging import setup_logging


def test_setup_logging_creates_log_file(tmp_path: Path) -> None:
    """setup_logging should create a foundry.log file in the given directory."""
    flog._configured = False

    log_path = setup_logging(log_dir=tmp_path, console=False)

    assert log_path.exists()
    assert log_path.name == "foundry.log"
    assert log_path.parent == tmp_path

    # Clean up handlers to avoid polluting other tests
    logger = logging.getLogger("foundry_app")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    flog._configured = False


def test_setup_logging_configures_logger(tmp_path: Path) -> None:
    """After setup_logging, the 'foundry_app' logger should have at least one handler."""
    flog._configured = False

    # Remove any pre-existing handlers first
    logger = logging.getLogger("foundry_app")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    setup_logging(log_dir=tmp_path, console=False)

    logger = logging.getLogger("foundry_app")
    assert len(logger.handlers) >= 1

    # Clean up handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    flog._configured = False


def test_setup_logging_with_console(tmp_path: Path) -> None:
    """setup_logging with console=True should add both file and console handlers."""
    flog._configured = False

    logger = logging.getLogger("foundry_app")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    setup_logging(log_dir=tmp_path, console=True)

    logger = logging.getLogger("foundry_app")
    # Should have at least 2 handlers: file + console
    assert len(logger.handlers) >= 2

    # Clean up handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    flog._configured = False


def test_setup_logging_returns_path_in_log_dir(tmp_path: Path) -> None:
    """The returned path should be inside the specified log_dir."""
    flog._configured = False

    logger = logging.getLogger("foundry_app")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    log_path = setup_logging(log_dir=tmp_path, console=False)

    assert str(log_path).startswith(str(tmp_path))

    # Clean up handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    flog._configured = False
