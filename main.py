from modules.logger import logging
from modules.bots import TelegramBot
from modules.configs import TELEGRAM_TOKEN, TELEGRAM_PROXY_URL

logger = logging.getLogger("g-miner")


def main():
    logger.info("Starting g-miner...")

    try:
        # Check if the environment variables are set
        if not TELEGRAM_TOKEN:
            logger.error("TELEGRAM_TOKEN is not set in the environment variables.")
            return

        # Initialize the Telegram Bot
        telegram_bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_PROXY_URL)
        telegram_bot.run()

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
