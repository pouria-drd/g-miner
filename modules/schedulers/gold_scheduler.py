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
        self.logger = get_logger("GoldScheduler")

        self.settings = get_settings()
        self.telegram_bot = telegram_bot

        self.SCHEDULER_TIME_ZONE = self.settings["SCHEDULER_TIME_ZONE"]

        # Lazy initialization of GoldService
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
        """Lazy initialize GoldService to save memory."""
        if self._gold_service is None:
            self._gold_service = GoldService(telegram_bot=self.telegram_bot)
        return self._gold_service

    async def gold_price_job(self):
        """
        Fetch the latest price and send it to the Telegram channel.
        Only executes during working hours (11:00-20:30 Tehran time) and if scheduler is enabled.
        """
        try:
            # Check if scheduler is enabled
            if not self.settings["SCHEDULER_ENABLED"]:
                self.logger.info("Scheduler is disabled. Skipping price fetch.")
                return

            # Get current Tehran time
            now = datetime.now(self.SCHEDULER_TIME_ZONE)
            current_time = now.time()

            # Check working hours
            if not (self.START_TIME <= current_time <= self.END_TIME):
                self.logger.info(f"Outside working hours. Current time: {current_time}")
                return

            self.logger.info(f"Fetching price at {now.strftime('%Y-%m-%d %H:%M:%S')}")

            await self.gold_service.run()

        except Exception as e:
            self.logger.error(f"Error in fetch_and_send: {e}", exc_info=True)

    def start(self):
        """
        Start the scheduler with a job that runs every x minutes.
        """
        try:
            # Schedule job to run every x minutes
            self.scheduler.add_job(
                self.gold_price_job,
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
