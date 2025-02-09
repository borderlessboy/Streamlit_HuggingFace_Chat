"""Logging configuration module."""

import logging
import sys
from datetime import datetime
from pathlib import Path

from config.settings import LOGS_DIR


def setup_logger(name: str) -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: Name for the logger instance

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s"
    )

    # Create handlers
    log_file = LOGS_DIR / f"chat_app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Create and configure logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
