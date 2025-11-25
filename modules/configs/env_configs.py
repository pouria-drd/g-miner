import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

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
