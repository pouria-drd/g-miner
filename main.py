import sys
from modules.logger import logging
from modules.bots import TelegramBot
from modules.configs import (
    ADMIN_CHAT_IDS,
    TELEGRAM_TOKEN,
    TELEGRAM_PROXY_URL,
    TELEGRAM_CHANNEL_ID,
)

logger = logging.getLogger("g-miner")


def validate_configs() -> bool:
    """
    Checks for the existence of critical configuration values.
    Returns True if all required configs are present, False otherwise.
    """

    # Map required variables to their imported values
    required_configs = {
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


def main():
    """
    The main entry point for the g-miner application.
    """
    logger.info("Initializing g-miner application...")

    try:
        # Validate critical configurations before proceeding
        if not validate_configs():
            # Exit cleanly if validation fails
            sys.exit(1)

        logger.info("Configurations successfully loaded and validated.")

        # Initialize and run the Telegram Bot
        # TELEGRAM_PROXY_URL is correctly passed as an Optional parameter
        telegram_bot = TelegramBot(token=TELEGRAM_TOKEN, proxy=TELEGRAM_PROXY_URL, allowed_ids=ADMIN_CHAT_IDS)  # type: ignore

        logger.info("Bot architecture initialized. Starting polling loop...")
        telegram_bot.run()  # This is the blocking call that starts the bot

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
