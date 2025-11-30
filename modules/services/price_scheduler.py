import asyncio
from zoneinfo import ZoneInfo
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.bots import TelegramBot
from modules.configs import Settings
from modules.configs import get_logger
from modules.services import PriceService


class PriceScheduler:
    """
    Scheduler service to fetch prices and send to Telegram channel.
    Runs every x minutes between start and end times of given timezone for a single day.
    """

    def __init__(self, env_config: Settings, telegram_bot: TelegramBot):
        self.logger = get_logger("PriceScheduler")

        self.env_config = env_config
        self.telegram_bot = telegram_bot

        self.TIME_ZONE = ZoneInfo(self.env_config.SCHEDULER_TIME_ZONE)

        self.price_service = PriceService(self.env_config)

        self.scheduler = AsyncIOScheduler(timezone=self.TIME_ZONE)

        self.END_TIME = self.env_config.SCHEDULER_END_TIME
        self.START_TIME = self.env_config.SCHEDULER_START_TIME
        self.INTERVAL_MINUTES = self.env_config.SCHEDULER_INTERVAL_MINUTES

    async def fetch_and_send(self):
        """
        Fetch the latest price and send it to the Telegram channel.
        Only executes during working hours (11:00-20:30 Tehran time).
        """
        try:
            # Get current Tehran time
            now = datetime.now(self.TIME_ZONE)
            current_time = now.time()

            # Check if within working hours
            if not (self.START_TIME <= current_time <= self.END_TIME):
                self.logger.debug(
                    f"Outside working hours. Current time: {current_time}"
                )
                return

            self.logger.info(f"Fetching price at {now.strftime('%Y-%m-%d %H:%M:%S')}")

            # Fetch data (runs synchronously)
            prices = await asyncio.to_thread(self.price_service.fetch_data)

            if prices and prices.get("estimate_price_toman"):
                # Get the latest stored price
                latest = await asyncio.to_thread(self.price_service.get_latest_price)

                if latest:
                    # Try to get the previous stored price (one before latest)
                    try:
                        # repository stores entries in a file; get all and pick second-last
                        all_entries = await asyncio.to_thread(
                            self.price_service.repo.get_all
                        )
                        prev = all_entries[-2] if len(all_entries) >= 2 else None
                    except Exception:
                        prev = None

                    # Format message with direction icon based on estimate_price_toman
                    message = self.price_service.format_message(latest, previous=prev)

                    channel_id = self.env_config.TELEGRAM_CHANNEL_ID
                    if not channel_id:
                        self.logger.error(
                            "TELEGRAM_CHANNEL_ID is not set in .env file."
                        )
                        raise ValueError("TELEGRAM_CHANNEL_ID is not set in .env file.")
                    # Send to channel
                    await self.telegram_bot.send_channel_message(
                        channel_id=channel_id, text=message
                    )

                    self.logger.info(f"Price update sent to channel: {channel_id}")
                else:
                    self.logger.warning("No latest price found in database")
            else:
                self.logger.warning("Failed to fetch valid price data")

        except Exception as e:
            self.logger.error(f"Error in fetch_and_send: {e}", exc_info=True)

    def start(self):
        """
        Start the scheduler with a job that runs every x minutes.
        """
        try:
            # Schedule job to run every x minutes
            self.scheduler.add_job(
                self.fetch_and_send,
                trigger=CronTrigger(
                    minute=f"*/{self.INTERVAL_MINUTES}", timezone=self.TIME_ZONE
                ),
                id="price_fetch_job",
                name=f"Fetch and send price every {self.INTERVAL_MINUTES} minutes",
                replace_existing=True,
            )

            self.logger.info(
                f"Scheduler started. Will fetch prices every {self.INTERVAL_MINUTES} minutes (between {self.START_TIME} and {self.END_TIME} time) {self.TIME_ZONE}"
            )
            self.scheduler.start()

        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
            raise

    def stop(self):
        """
        Stop the scheduler gracefully.
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                self.logger.info("Scheduler stopped")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
