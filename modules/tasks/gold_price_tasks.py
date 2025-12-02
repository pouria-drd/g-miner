import asyncio
from datetime import datetime
from celery import shared_task

from modules.bots import TelegramBot
from modules.services import PriceService
from modules.configs import get_settings, get_logger


@shared_task(bind=True, max_retries=3)
def fetch_and_send(self):
    logger = get_logger("CeleryGoldPriceTask")
    settings = get_settings()

    SCHEDULER_TIME_ZONE = settings["SCHEDULER_TIME_ZONE"]
    now = datetime.now(SCHEDULER_TIME_ZONE)
    current_time = now.time()

    SCHEDULER_START_TIME = settings["SCHEDULER_START_TIME"]
    SCHEDULER_END_TIME = settings["SCHEDULER_END_TIME"]

    # Check if within working hours
    if not (SCHEDULER_START_TIME <= current_time <= SCHEDULER_END_TIME):
        logger.debug(f"Outside working hours: {current_time}")
        return "Skipped (outside working hours)"

    try:
        price_service = PriceService()
        telegram = TelegramBot(
            token=settings["TELEGRAM_TOKEN"],
            proxy=settings["TELEGRAM_PROXY_URL"],
            allowed_ids=[settings["ADMIN_CHAT_IDS"]],
        )

        prices = price_service.fetch_data()

        if prices and prices.get("estimate_price_toman"):
            latest = price_service.get_latest_price()

            if latest:
                # Previous entry
                try:
                    all_entries = price_service.repo.get_all()
                    prev = all_entries[-2] if len(all_entries) >= 2 else None
                except:
                    prev = None

                message = price_service.format_message(latest, previous=prev)

                channel_id = settings["TELEGRAM_CHANNEL_ID"]
                if not channel_id:
                    raise ValueError("TELEGRAM_CHANNEL_ID not set")

                asyncio.run(telegram.send_channel_message(channel_id, message))

                logger.info(f"Price update sent to channel {channel_id}")
            else:
                logger.warning("No latest price found")
        else:
            logger.warning("Invalid price data")

    except Exception as e:
        logger.error(f"Task error: {e}")
        raise self.retry(exc=e, countdown=5)

    return "OK"
