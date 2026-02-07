"""Foundry logging: configure structured logging with file and console handlers."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_DEFAULT_LOG_DIR = Path.home() / ".local" / "share" / "foundry" / "logs"
_LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"
_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_BACKUP_COUNT = 3
_configured = False


def setup_logging(
    level: int = logging.INFO,
    log_dir: Path | None = None,
    console: bool = True,
) -> Path:
    """Configure the root ``foundry_app`` logger.

    Args:
        level: Logging level (default ``INFO``).
        log_dir: Directory for the rotating log file. Defaults to
            ``~/.local/share/foundry/logs/``.
        console: If True, also log to stderr.

    Returns:
        The path to the log file that was created.
    """
    global _configured
    if log_dir is None:
        log_dir = _DEFAULT_LOG_DIR

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "foundry.log"

    logger = logging.getLogger("foundry_app")
    logger.setLevel(level)

    # Avoid duplicate handlers on repeated calls
    if not _configured:
        formatter = logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE_FORMAT)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        _configured = True

    return log_file
