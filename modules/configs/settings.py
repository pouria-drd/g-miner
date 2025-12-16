import os
from pathlib import Path
from datetime import time
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from modules.utils import parse_env_time


def get_settings() -> dict:
    """Read environment variables and return a dictionary of settings."""
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    load_dotenv(override=True)

    PROJECT_NAME = os.getenv("PROJECT_NAME", "GMiner")

    # Scheduler Settings
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"
    SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "5"))
    SCHEDULER_START_TIME = parse_env_time(
        os.getenv("SCHEDULER_START_TIME", "11:00"), time(11, 0)
    )
    SCHEDULER_END_TIME = parse_env_time(
        os.getenv("SCHEDULER_END_TIME", "20:30"), time(20, 30)
    )
    SCHEDULER_TIME_ZONE = ZoneInfo(os.getenv("SCHEDULER_TIME_ZONE", "Asia/Tehran"))

    # Telegram Settings
    ADMIN_CHAT_IDS = set(
        x.strip() for x in os.getenv("ADMIN_CHAT_IDS", "").split(",") if x.strip()
    )
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
    TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")

    # Zarbaha Scraper Settings
    ZARBAHA_TIMEOUT = int(os.getenv("ZARBAHA_TIMEOUT", "20"))
    ZARBAHA_INTERVAL = float(os.getenv("ZARBAHA_INTERVAL", "1"))
    ZARBAHA_BUY_PRICE_RATE = int(os.getenv("ZARBAHA_BUY_PRICE_RATE", "50000"))
    ZARBAHA_SELL_PRICE_RATE = int(os.getenv("ZARBAHA_SELL_PRICE_RATE", "130000"))

    # Celery Settings
    BROKER_URL = os.getenv("BROKER_URL", "redis://localhost:6379/0")
    RESULT_BACKEND = os.getenv("RESULT_BACKEND", "redis://localhost:6379/1")

    # Database Settings
    GOLD_DB_FOLDER = BASE_DIR / "db"
    GOLD_DB_FOLDER.mkdir(exist_ok=True)
    GOLD_DB_FILE: Path = GOLD_DB_FOLDER / "gold_prices.json"

    return {
        "PROJECT_NAME": PROJECT_NAME,
        "BASE_DIR": BASE_DIR,
        # Scheduler Settings
        "SCHEDULER_ENABLED": SCHEDULER_ENABLED,
        "SCHEDULER_INTERVAL_MINUTES": SCHEDULER_INTERVAL_MINUTES,
        "SCHEDULER_START_TIME": SCHEDULER_START_TIME,
        "SCHEDULER_END_TIME": SCHEDULER_END_TIME,
        "SCHEDULER_TIME_ZONE": SCHEDULER_TIME_ZONE,
        # Telegram Settings
        "ADMIN_CHAT_IDS": ADMIN_CHAT_IDS,
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHANNEL_ID": TELEGRAM_CHANNEL_ID,
        "TELEGRAM_PROXY_URL": TELEGRAM_PROXY_URL,
        # Zarbaha Scraper Settings
        "ZARBAHA_TIMEOUT": ZARBAHA_TIMEOUT,
        "ZARBAHA_INTERVAL": ZARBAHA_INTERVAL,
        "ZARBAHA_BUY_PRICE_RATE": ZARBAHA_BUY_PRICE_RATE,
        "ZARBAHA_SELL_PRICE_RATE": ZARBAHA_SELL_PRICE_RATE,
        # Celery Settings
        "BROKER_URL": BROKER_URL,
        "RESULT_BACKEND": RESULT_BACKEND,
        # Database Settings
        "GOLD_DB_FOLDER": GOLD_DB_FOLDER,
        "GOLD_DB_FILE": GOLD_DB_FILE,
    }
