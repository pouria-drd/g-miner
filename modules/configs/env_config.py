import os
from pathlib import Path
from datetime import time
from dotenv import load_dotenv
from modules.logger import logging

load_dotenv()


logger = logging.getLogger("env_config")


def parse_env_time(env_value: str, default: time) -> time:
    """
    Convert a string like 'HH:MM' to a datetime.time object.
    If parsing fails, return default.
    """
    try:
        hours, minutes = map(int, env_value.split(":"))
        return time(hours, minutes)
    except Exception:
        return default


# ---------------------------------------------------------------
# Scheduler Configuration
# ---------------------------------------------------------------
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"

SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "5"))

SCHEDULER_START_TIME = parse_env_time(
    os.getenv("SCHEDULER_START_TIME", "11:00"), time(11, 0)
)

SCHEDULER_END_TIME = parse_env_time(
    os.getenv("SCHEDULER_END_TIME", "20:30"), time(20, 30)
)

SCHEDULER_TIME_ZONE = os.getenv("SCHEDULER_TIME_ZONE", "Asia/Tehran")

# ---------------------------------------------------------------
# Telegram Bot Configuration
# ---------------------------------------------------------------
ADMIN_CHAT_IDS = [
    str(x.strip()) for x in os.getenv("ADMIN_CHAT_IDS", "").split(",") if x.strip()
]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
# Replace with your channel's @username (e.g., @MyAwesomeChannel)
# If the channel is private, use the numerical ID format:
# CHANNEL_ID = -100123456789

TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")

# ---------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------
DB_FOLDER = Path("db")
DB_FOLDER.mkdir(exist_ok=True)
DB_FILE = DB_FOLDER / "gold_prices.json"


def check_required_configs() -> bool:
    """
    Checks for the existence of critical configuration values.
    Returns True if all required configs are present, False otherwise.
    """

    # Map required variables to their imported values
    required_configs = {
        "ADMIN_CHAT_IDS": ADMIN_CHAT_IDS,
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHANNEL_ID": TELEGRAM_CHANNEL_ID,
    }

    is_valid = True

    for key, value in required_configs.items():
        if not value:
            logger.error(
                f"FATAL: Missing required configuration value for {key}. Please set it in the environment or config file."
            )
            is_valid = False

    return is_valid
