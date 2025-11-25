import os
from pathlib import Path
from datetime import time
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv(filename=".env", usecwd=True)
print(env_path)
load_dotenv(dotenv_path=env_path, override=True)


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


# ==== Scheduler Configs ====
SCHEDULER_MINUTES = int(os.getenv("SCHEDULER_MINUTES", "5"))
SCHEDULER_START_TIME = parse_env_time(
    os.getenv("SCHEDULER_START_TIME", "11:00"), time(11, 0)
)
SCHEDULER_END_TIME = parse_env_time(
    os.getenv("SCHEDULER_END_TIME", "20:30"), time(20, 30)
)
SCHEDULER_TIME_ZONE = os.getenv("SCHEDULER_TIME_ZONE", "Asia/Tehran")

# ==== Telegram Bot Configs ====
raw_ids = os.getenv("ADMIN_CHAT_IDs", "")
ADMIN_CHAT_IDS = [str(x.strip()) for x in raw_ids.split(",") if x.strip()]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")

TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
# Replace with your channel's @username (e.g., @MyAwesomeChannel)
# If the channel is private, use the numerical ID format:
# CHANNEL_ID = -100123456789

# ==== Database Configs ====
DB_FOLDER = Path("db")
DB_FOLDER.mkdir(exist_ok=True)
DB_FILE = DB_FOLDER / "prices.json"
