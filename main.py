import sys
import asyncio
from modules.logger import logging
from modules.bots import TelegramBot
from modules.configs import ADMIN_CHAT_IDS, TELEGRAM_TOKEN, TELEGRAM_PROXY_URL

from modules.utils import run_bot_with_scheduler
from modules.configs import check_required_configs

logger = logging.getLogger("g-miner")


def main():
    """
    The main entry point for the g-miner application.
    """
    logger.info("Initializing g-miner application...")

    try:
        # Validate critical configurations before proceeding
        if not check_required_configs():
            # Exit cleanly if validation fails
            sys.exit(1)

        logger.info("Configurations successfully loaded and validated.")

        # Initialize the Telegram Bot
        telegram_bot = TelegramBot(
            token=TELEGRAM_TOKEN,  # type: ignore
            proxy=TELEGRAM_PROXY_URL,
            allowed_ids=ADMIN_CHAT_IDS,
        )

        logger.info("Bot architecture initialized.")
        logger.info("Starting bot with price scheduler...")

        # Run the bot and scheduler together
        asyncio.run(run_bot_with_scheduler(telegram_bot))

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.warning("Application stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logger.error(
            f"A critical error occurred during bot execution: {e}", exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
