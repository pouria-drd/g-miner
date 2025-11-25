from modules.logger import logging

from modules.configs import (
    SCHEDULER_TIME_ZONE,
    SCHEDULER_START_TIME,
    SCHEDULER_END_TIME,
    SCHEDULER_MINUTES,
    ADMIN_CHAT_IDS,
    TELEGRAM_TOKEN,
    TELEGRAM_PROXY_URL,
    TELEGRAM_CHANNEL_ID,
)


logger = logging.getLogger(__name__)


def validate_configs() -> bool:
    """
    Checks for the existence of critical configuration values.
    Returns True if all required configs are present, False otherwise.
    """

    # Map required variables to their imported values
    required_configs = {
        "SCHEDULER_TIME_ZONE": SCHEDULER_TIME_ZONE,
        "SCHEDULER_START_TIME": SCHEDULER_START_TIME,
        "SCHEDULER_END_TIME": SCHEDULER_END_TIME,
        "SCHEDULER_MINUTES": SCHEDULER_MINUTES,
        "ADMIN_CHAT_IDS": ADMIN_CHAT_IDS,
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHANNEL_ID": TELEGRAM_CHANNEL_ID,
        # TELEGRAM_PROXY_URL is optional, so it's not listed here for strict validation
    }

    is_valid = True
    for key, value in required_configs.items():
        if not value:
            logger.error(
                f"FATAL: Missing required configuration value for {key}. Please set it in the environment or config file."
            )
            is_valid = False

    # Proxy check (Optional, but useful to confirm load)
    if TELEGRAM_PROXY_URL:
        logger.info(f"Telegram proxy configured: {TELEGRAM_PROXY_URL}")

    return is_valid
