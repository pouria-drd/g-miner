import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")

TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
# Replace with your channel's @username (e.g., @MyAwesomeChannel)
# If the channel is private, use the numerical ID format:
# CHANNEL_ID = -100123456789
