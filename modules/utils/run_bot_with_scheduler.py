import asyncio
from modules.bots import TelegramBot
from modules.services import PriceScheduler
from modules.configs import TELEGRAM_CHANNEL_ID


async def run_bot_with_scheduler(telegram_bot: TelegramBot):
    """
    Runs both the Telegram bot and price scheduler concurrently.

    Args:
        telegram_bot: Initialized TelegramBot instance
    """
    try:
        # Initialize the price scheduler
        scheduler = PriceScheduler(
            telegram_bot=telegram_bot, channel_id=TELEGRAM_CHANNEL_ID  # type: ignore
        )

        logger.info("Starting price scheduler...")
        scheduler.start()

        # Run the bot's polling in a separate task
        logger.info("Starting Telegram bot polling...")

        # Create a task for the bot polling
        # Note: We need to run the bot's polling loop in the async context
        bot_task = asyncio.create_task(telegram_bot.run())  # type: ignore

        # Wait for the bot task (it will run indefinitely until interrupted)
        await bot_task

    except asyncio.CancelledError:
        logger.info("Bot and scheduler tasks cancelled")
        scheduler.stop()
        raise
    except Exception as e:
        logger.error(f"Error in run_bot_with_scheduler: {e}", exc_info=True)
        scheduler.stop()
        raise
