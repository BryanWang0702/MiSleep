# -*- coding: UTF-8 -*-
"""Logging setup for MiSleep.

MiSleep uses a single module-level :data:`logger` instance so that every
sub-module can simply do ``from misleep.logger import logger`` and log to
the same destination.

The log is written both to the console (stdout) and to a rotating log file
stored under the per-user MiSleep data directory (see :func:`get_data_dir`).
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_data_dir() -> Path:
    """Return the per-user MiSleep data directory.

    The directory is created on first use. On all platforms it defaults to
    ``~/.misleep``, which keeps things simple and cross-platform friendly.

    Returns
    -------
    Path
        Absolute path of the data directory.
    """
    override = os.environ.get("MISLEEP_DATA_DIR")
    data_dir = Path(override).expanduser() if override else Path.home() / ".misleep"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _setup_logger() -> logging.Logger:
    """Create and configure the MiSleep root logger."""
    logger = logging.getLogger("misleep")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Avoid double handlers when the module is reloaded
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler (skipped when launched with pythonw, where both
    # stdout and stderr are None)
    console_stream = sys.stderr if sys.stderr is not None else sys.stdout
    if console_stream is not None:
        stream_handler = logging.StreamHandler(console_stream)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Rotating file handler under the user data directory
    try:
        log_dir = get_data_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "misleep.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:  # pragma: no cover - e.g. read-only home directory
        pass

    return logger


#: The shared logger instance used across the package.
logger = _setup_logger()
