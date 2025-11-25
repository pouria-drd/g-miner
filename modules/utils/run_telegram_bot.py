import asyncio
from modules.logger import logging
from modules.bots import TelegramBot


logger = logging.getLogger(__name__)


async def run_telegram_bot(telegram_bot: TelegramBot):
    """
    Wrapper to run the Telegram bot's polling in async context.

    Args:
        telegram_bot: Initialized TelegramBot instance
    """
    try:
        # Register handlers
        telegram_bot.general_handlers.register(telegram_bot.app)

        logger.info("Bot is starting polling...")

        # Initialize and start polling
        await telegram_bot.app.initialize()
        await telegram_bot.app.start()
        await telegram_bot.app.updater.start_polling()  # type: ignore

        # Keep running until stopped
        try:
            await asyncio.Event().wait()
        finally:
            await telegram_bot.app.updater.stop()  # type: ignore
            await telegram_bot.app.stop()
            await telegram_bot.app.shutdown()

    except Exception as e:
        logger.error(f"Error in Telegram bot polling: {e}", exc_info=True)
        raise
