import asyncio
import jdatetime
from zoneinfo import ZoneInfo
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.logger import logging
from modules.services.price_service import PriceService
from modules.configs import (
    SCHEDULER_MINUTES,
    SCHEDULER_TIME_ZONE,
    SCHEDULER_END_TIME,
    SCHEDULER_START_TIME,
)


class PriceScheduler:
    """
    Scheduler service to fetch prices and send to Telegram channel.
    Runs every x minutes between start and end times of given timezone for a single day.
    """

    MINUTES = SCHEDULER_MINUTES  # every x minutes
    TIME_ZONE = ZoneInfo(SCHEDULER_TIME_ZONE)
    # Define working hours
    END_TIME = SCHEDULER_END_TIME
    START_TIME = SCHEDULER_START_TIME

    def __init__(self, telegram_bot, channel_id: str):
        self.logger = logging.getLogger("PriceScheduler")
        self.price_service = PriceService()
        self.telegram_bot = telegram_bot
        self.channel_id = channel_id
        self.scheduler = AsyncIOScheduler(timezone=self.TIME_ZONE)

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

                    # Send to channel
                    await self.telegram_bot.send_channel_message(
                        channel_id=self.channel_id, text=message
                    )

                    self.logger.info(f"Price update sent to channel: {self.channel_id}")
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
                    minute=f"*/{self.MINUTES}", timezone=self.TIME_ZONE
                ),
                id="price_fetch_job",
                name=f"Fetch and send price every {self.MINUTES} minutes",
                replace_existing=True,
            )

            self.logger.info(
                f"Scheduler started. Will fetch prices every {self.MINUTES} minutes (between {self.START_TIME} and {self.END_TIME} time) {self.TIME_ZONE}"
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
