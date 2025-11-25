from typing import Optional
from telegram.ext import Application

from modules.logger import logging
from .handlers import GeneralHandlers


class TelegramBot:
    def __init__(self, token: str, proxy: Optional[str] = None):
        # 1. Setup Logger
        self.logger = logging.getLogger("TelegramBot")

        # 2. Load Configs
        self.token = token
        self.proxy = proxy

        # 3. Build Application
        builder = self.build()
        self.app = builder.build()
        self.bot = self.app.bot

        # 4. Initialize Logic Classes
        # Inject the logger into handlers so they use the same system
        self.general_handlers = GeneralHandlers(self.logger)

    def run(self):
        """
        Registers handlers and starts the polling loop.
        """
        try:
            self.logger.info("Initializing Bot Architecture...")

            # Register the handlers from our modular classes
            self.general_handlers.register(self.app)

            self.logger.info("Bot is starting polling...")
            self.app.run_polling()

        except Exception as e:
            self.logger.error(f"Error running Telegram Bot: {e}")
            raise e

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

    async def send_channel_message(self, channel_id: str, text: str):
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
            await bot.send_message(chat_id=channel_id, text=text)

            self.logger.info(f"Successfully sent message to channel: {channel_id}")

        except Exception as e:
            self.logger.error(f"Error sending message to channel {channel_id}: {e}")
            raise e
