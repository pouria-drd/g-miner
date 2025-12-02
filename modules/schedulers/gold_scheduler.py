import asyncio
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.bots import TelegramBot
from modules.services import GoldService
from modules.configs import get_settings, get_logger


class GoldScheduler:
    """
    Scheduler service to fetch gold prices and send to Telegram channel.
    Runs every x minutes between start and end times of given timezone for a single day.
    """

    def __init__(self, telegram_bot: TelegramBot):
        self.logger = get_logger("PriceScheduler")

        self.settings = get_settings()
        self.telegram_bot = telegram_bot

        self.SCHEDULER_TIME_ZONE = self.settings["SCHEDULER_TIME_ZONE"]

        # Lazy initialization of PriceService
        self._gold_service = None

        self.END_TIME = self.settings["SCHEDULER_END_TIME"]
        self.START_TIME = self.settings["SCHEDULER_START_TIME"]

        self.INTERVAL_MINUTES = int(self.settings["SCHEDULER_INTERVAL_MINUTES"])

        self.scheduler = AsyncIOScheduler(
            timezone=self.SCHEDULER_TIME_ZONE,
            job_defaults={
                "coalesce": True,  # Prevent job pile-up
                "max_instances": 1,  # Only one instance at a time
                "misfire_grace_time": 30,  # Skip jobs that are >30s late
            },
        )

    @property
    def gold_service(self):
        """Lazy initialize PriceService to save memory."""
        if self._gold_service is None:
            self._gold_service = GoldService()
        return self._gold_service

    async def fetch_and_send(self):
        """
        Fetch the latest price and send it to the Telegram channel.
        Only executes during working hours (11:00-20:30 Tehran time).
        """
        try:
            # Get current Tehran time
            now = datetime.now(self.SCHEDULER_TIME_ZONE)
            current_time = now.time()

            # Check working hours
            if not (self.START_TIME <= current_time <= self.END_TIME):
                self.logger.debug(
                    f"Outside working hours. Current time: {current_time}"
                )
                return

            self.logger.info(f"Fetching price at {now.strftime('%Y-%m-%d %H:%M:%S')}")

            # Get the latest stored price
            latest = self.gold_service.get_latest_price()

            if latest:
                # Try to get the previous stored price (one before latest)
                try:
                    # repository stores entries in a file; get all and pick second-last
                    all_entries = self.gold_service.repo.get_all()
                    prev = all_entries[-2] if len(all_entries) >= 2 else None
                except Exception:
                    prev = None

                # Format message with direction icon based on estimate_price_toman
                message = self.gold_service.format_message(latest, previous=prev)

                channel_id = self.settings["TELEGRAM_CHANNEL_ID"]
                if not channel_id:
                    self.logger.error("TELEGRAM_CHANNEL_ID is not set in .env file.")
                    raise ValueError("TELEGRAM_CHANNEL_ID is not set in .env file.")
                # Send to channel
                await self.telegram_bot.send_channel_message(
                    channel_id=channel_id, text=message
                )

                self.logger.info(f"Price update sent to channel: {channel_id}")
            else:
                self.logger.warning("No latest price found in database")

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
                    minute=f"*/{self.INTERVAL_MINUTES}",
                    timezone=self.SCHEDULER_TIME_ZONE,
                ),
                id="price_fetch_job",
                name=f"Fetch and send price every {self.INTERVAL_MINUTES} minutes",
                replace_existing=True,
            )

            self.logger.info(
                f"Scheduler started. Will fetch gold prices every {self.INTERVAL_MINUTES} minutes "
                f"(between {self.START_TIME} and {self.END_TIME}) {self.SCHEDULER_TIME_ZONE}"
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
