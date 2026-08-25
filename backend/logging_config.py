"""Logging configuration for SyncAgent.

Sets up structured logging with appropriate levels and formatting.
"""

import logging
import logging.config
from pathlib import Path

from backend.config import PROJECT_ROOT


# Create logs directory if it doesn't exist
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "[%(filename)s:%(lineno)d] - %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOGS_DIR / "syncagent.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": str(LOGS_DIR / "syncagent_errors.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "backend": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False,
        },
        "google": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "clickhouse_connect": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}


def setup_logging() -> None:
    """Initialize logging configuration.
    
    Called once at application startup to configure all loggers.
    Creates logs directory if needed and sets up rotating file handlers.
    """
    logging.config.dictConfig(LOG_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")


# Auto-initialize logging when this module is imported
setup_logging()
