import sys
import asyncio
from typing import Optional

from modules.bots import TelegramBot
from modules.schedulers import PriceScheduler
from modules.configs import get_settings, get_logger


class GMinerApp:
    """Main GMiner application with bot, scheduler, reload, and restart support."""

    def __init__(self):
        self.logger = get_logger("GMiner")
        self.settings = get_settings()

        self.bot_task: Optional[asyncio.Task] = None

        self.telegram_bot: Optional[TelegramBot] = None

        self.scheduler: Optional[PriceScheduler] = None

    def initialize_bot(self):
        """Initialize Telegram bot instance."""
        self.logger.info("Initializing Telegram Bot...")

        if not self.settings["TELEGRAM_TOKEN"]:
            self.logger.error("TELEGRAM_TOKEN is not set in .env file.")
            raise ValueError("TELEGRAM_TOKEN is not set in .env file.")

        self.telegram_bot = TelegramBot(
            token=self.settings["TELEGRAM_TOKEN"],
            proxy=self.settings["TELEGRAM_PROXY_URL"],
            allowed_ids=self.settings["ADMIN_CHAT_IDS"],
        )

        self.logger.info("Telegram Bot initialized.")

    def initialize_scheduler(self):
        """Initialize PriceScheduler instance."""
        if not self.telegram_bot:
            raise RuntimeError("Bot must be initialized before scheduler.")

        self.logger.info("Initializing Price Scheduler...")

        if not self.settings["TELEGRAM_CHANNEL_ID"]:
            self.logger.error("TELEGRAM_CHANNEL_ID is not set in .env file.")
            raise ValueError("TELEGRAM_CHANNEL_ID is not set in .env file.")

        self.scheduler = PriceScheduler(telegram_bot=self.telegram_bot)

        self.logger.info("Price Scheduler initialized.")

    async def run(self):
        """Run bot polling and scheduler concurrently."""
        if not self.telegram_bot or not self.scheduler:
            raise RuntimeError("Bot and scheduler must be initialized before running.")

        try:
            self.logger.info("Starting scheduler...")
            self.scheduler.start()

            self.logger.info("Starting Telegram bot polling...")
            self.bot_task = asyncio.create_task(self.telegram_bot.run())

            await self.bot_task

        except asyncio.CancelledError:
            self.logger.warning("Bot and scheduler tasks cancelled.")
            await self.stop()
            raise

        except Exception as e:
            self.logger.error(f"Error running GMiner: {e}", exc_info=True)
            await self.stop()
            raise

    async def stop(self):
        """Stop bot and scheduler safely."""
        # 1. Stop scheduler first
        if self.scheduler:
            self.logger.info("Stopping scheduler...")
            try:
                self.scheduler.stop()
            except Exception as e:
                self.logger.error(f"Error stopping scheduler: {e}")
            self.scheduler = None

        # 2. Cancel bot task first to stop polling gracefully
        if self.bot_task and not self.bot_task.done():
            self.logger.info("Cancelling bot task...")
            self.bot_task.cancel()
            try:
                await self.bot_task
            except asyncio.CancelledError:
                self.logger.info("Bot task cancelled successfully.")
            except Exception as e:
                self.logger.error(f"Error while stopping bot task: {e}")
            self.bot_task = None

        # 3. Stop Telegram bot instance safely
        if self.telegram_bot:
            self.logger.info("Stopping Telegram bot instance...")
            try:
                await self.telegram_bot.stop()
            except asyncio.CancelledError:
                self.logger.info("Telegram bot stop cancelled.")
            except Exception as e:
                self.logger.error(f"Error stopping Telegram bot: {e}")
            self.telegram_bot = None

    def reload_config(self):
        """Reload environment config at runtime."""
        self.logger.info("Reloading configuration...")
        self.settings = get_settings()
        self.logger.info("Configuration reloaded.")

    async def restart(self):
        """Restart bot and scheduler completely."""
        self.logger.info("Restarting GMiner...")
        await self.stop()
        self.initialize_bot()
        self.initialize_scheduler()
        await self.run()

    def start(self):
        """Entry point to run the application."""
        self.logger.info("Starting GMiner application...")
        try:
            self.initialize_bot()
            self.initialize_scheduler()
            asyncio.run(self.run())

        except KeyboardInterrupt:
            self.logger.warning("Application stopped by user (KeyboardInterrupt).")
            asyncio.run(self.stop())

        except Exception as e:
            self.logger.error(f"Fatal error in GMiner: {e}", exc_info=True)
            sys.exit(1)
