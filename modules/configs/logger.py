import os
import colorlog
import logging
from logging.handlers import RotatingFileHandler

from .settings import get_settings

settings_data = get_settings()

BASE_DIR = settings_data["BASE_DIR"]

LOG_DIR = BASE_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str = "App") -> logging.Logger:
    """Create or return a logger with per-app log file."""

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Separate log file for each app
    log_file = os.path.join(LOG_DIR, f"{name}.log")
    file_formatter = logging.Formatter(
        fmt="[%(asctime)s] | [%(name)s] | [%(levelname)s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # Colored console handler (only level name is colored)
    console_formatter = colorlog.ColoredFormatter(
        "[%(asctime)s] | [%(name)s] | %(log_color)s[%(levelname)s]%(reset)s | %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
