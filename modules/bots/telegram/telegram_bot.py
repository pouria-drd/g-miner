import asyncio
from typing import Optional
from telegram.ext import Application

from .handlers import GeneralHandlers
from modules.configs import get_logger


class TelegramBot:
    def __init__(
        self, token: str, proxy: Optional[str] = None, admin_ids: Optional[set] = None
    ):
        # 1. Setup Logger
        self.logger = get_logger("TelegramBot")

        # 2. Load Configs
        self.token = token
        self.proxy = proxy
        self.admin_ids = admin_ids or set()

        # 3. Build Application
        builder = self.build()
        self.app = builder.build()
        self.bot = self.app.bot

        # 4. Initialize Logic Classes
        # Inject the logger into handlers so they use the same system
        self.general_handlers = GeneralHandlers(self.logger)

    async def run(self):
        """
        Registers handlers and starts the polling loop.
        """
        try:
            self.logger.info("Initializing Bot Architecture...")

            # Register the handlers from our modular classes
            self.general_handlers.register(self.app)

            self.logger.info("Bot is starting polling...")

            # Initialize and start polling
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()  # type: ignore

            try:
                await asyncio.Event().wait()
            finally:
                await self.app.updater.stop()  # type: ignore
                await self.app.stop()
                await self.app.shutdown()

        except Exception as e:
            self.logger.error(f"Error running Telegram Bot: {e}")
            raise e

    async def stop(self):
        """Stop the bot safely."""
        if not self.app:
            return

        try:
            if self.app.running:
                self.logger.info("Stopping Telegram bot...")
                await self.app.stop()
                await self.app.shutdown()

        except asyncio.CancelledError:
            self.logger.info("Telegram bot stop cancelled due to task cancellation.")
        except Exception as e:
            self.logger.error(f"Error stopping Telegram Bot: {e}")

    def build(self):
        """
        Builds the application.
        """
        try:
            builder = Application.builder().token(self.token)

            # Configure proxy if TELEGRAM_PROXY_URL is set
            if self.proxy:
                builder.proxy(self.proxy)
                builder.get_updates_proxy(self.proxy)
                self.logger.info("Using proxy for Telegram bot.")

            # Set timeouts
            builder.get_updates_connect_timeout(10)
            builder.get_updates_read_timeout(10)
            builder.get_updates_write_timeout(10)
            builder.get_updates_pool_timeout(10)

            return builder

        except Exception as e:
            self.logger.error(f"Error building Telegram Bot: {e}")
            raise e

    async def notify_admins(self, text: str, parse_mode: str = "HTML"):
        """
        Sends a message to all admin chats.

        Args:
            text (str): The message content to send.
        """
        try:
            # 1. Access the Bot object from the Application
            bot = self.app.bot

            # 2. Call the send_message method
            for chat_id in self.admin_ids:
                chat = await bot.get_chat(chat_id)
                if chat:
                    await chat.send_message(text=text, parse_mode=parse_mode)

            self.logger.info(f"Successfully notified admins")

        except Exception as e:
            self.logger.error(f"Error notifying admins: {e}")

    async def send_channel_message(
        self, channel_id: str, text: str, parse_mode: str = "HTML"
    ):
        """
        Sends a message to a specific Telegram channel.

        Args:
            channel_id (str): The ID of the channel (e.g., @channelusername or -100123456789).
            text (str): The message content to send.
        """
        try:
            # 1. Access the Bot object from the Application
            bot = self.app.bot

            # 2. Call the send_message method
            await bot.send_message(chat_id=channel_id, text=text, parse_mode=parse_mode)

            self.logger.info(f"Successfully sent message to channel: {channel_id}")

        except Exception as e:
            self.logger.error(f"Error sending message to channel {channel_id}: {e}")
