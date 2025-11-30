import os
from pathlib import Path
from datetime import time
from dotenv import load_dotenv


class EnvConfig:
    """Central configuration manager with reloadable settings."""

    def __init__(self, env_file: str = ".env"):
        """
        Load the .env file and initialize all config values.

        Args:
            env_file: Optional path to a specific .env file.
        """
        self.env_file = env_file
        self.reload()

    @staticmethod
    def parse_env_time(env_value: str, default: time) -> time:
        """Convert 'HH:MM' string to datetime.time. Fallback to default if invalid."""
        try:
            hours, minutes = map(int, env_value.split(":"))
            return time(hours, minutes)
        except Exception:
            return default

    def reload(self):
        """Reload .env file and update all config values."""
        if self.env_file:
            load_dotenv(self.env_file, override=True)
        else:
            load_dotenv(override=True)

        # Scheduler
        self.SCHEDULER_ENABLED = (
            os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"
        )
        self.SCHEDULER_INTERVAL_MINUTES = int(
            os.getenv("SCHEDULER_INTERVAL_MINUTES", "5")
        )
        self.SCHEDULER_START_TIME = self.parse_env_time(
            os.getenv("SCHEDULER_START_TIME", "11:00"), time(11, 0)
        )
        self.SCHEDULER_END_TIME = self.parse_env_time(
            os.getenv("SCHEDULER_END_TIME", "20:30"), time(20, 30)
        )
        self.SCHEDULER_TIME_ZONE = os.getenv("SCHEDULER_TIME_ZONE", "Asia/Tehran")

        # Telegram Bot
        self.ADMIN_CHAT_IDS = [
            x.strip() for x in os.getenv("ADMIN_CHAT_IDS", "").split(",") if x.strip()
        ]
        self.TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
        self.TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
        self.TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")

        # Database
        self.DB_FOLDER: Path = Path("db")
        self.DB_FOLDER.mkdir(exist_ok=True)
        self.DB_FILE: Path = self.DB_FOLDER / "gold_prices.json"


"""
# Usage
CONFIG = EnvConfig()

# Access values
print(CONFIG.SCHEDULER_ENABLED)
print(CONFIG.SCHEDULER_START_TIME)

# Reload at runtime if .env changes
CONFIG.reload()
"""
