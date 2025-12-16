import jdatetime
from datetime import datetime

from modules.bots import TelegramBot
from modules.repositories import GoldRepository
from modules.configs import get_settings, get_logger
from modules.scrapers.zarbaha_scraper import ZarbahaScraper


class GoldService:
    """
    Service layer for business logic around gold prices.
    """

    MESAQAL_TO_GRAM = 4.331802  # every mesqal is how many grams?

    def __init__(self, telegram_bot: TelegramBot):
        self.logger = get_logger("GoldService")
        self.settings = get_settings()

        self.repo = GoldRepository()
        self.telegram_bot = telegram_bot
        self.scraper = ZarbahaScraper(headless=True)

        self.SCHEDULER_TIME_ZONE = self.settings["SCHEDULER_TIME_ZONE"]

    async def run(self):
        """Run the price fetching task."""
        try:
            # Get the latest stored price
            success, latest = self.__get_latest_price()

            if not success:
                self.logger.warning("Failed to fetch valid price.")
                await self.telegram_bot.notify_admins(
                    "❌ Failed to fetch valid price! using previous price instead..."
                )

            if latest:
                # Try to get the previous stored price (one before latest)
                try:
                    # repository stores entries in a file; get all and pick second-last
                    all_entries = self.repo.get_all()
                    prev = all_entries[-2] if len(all_entries) >= 2 else None
                except Exception:
                    prev = None

                # Format message with direction icon based on estimate_price_toman
                message = self.__format_message(latest, previous=prev)

                # Send to channel
                channel_id = self.settings["TELEGRAM_CHANNEL_ID"]
                await self.telegram_bot.send_channel_message(
                    channel_id=channel_id,
                    text=message,
                )

                self.logger.info(f"Price update sent to channel: {channel_id}")

        except Exception as e:
            self.logger.error(f"Error in while fetching price: {e}", exc_info=True)

    def __get_latest_price(self):
        """Retrieve the most recent stored price."""
        success = self.__fetch_data()
        prices = self.repo.get_latest()
        return (success, prices)

    def __fetch_data(self):
        """Fetch price from Zarbaha and store it."""
        try:
            prices = self.scraper.scrape()
            # Extract price data
            estimate_price = prices.get("estimate_price_toman")
            # check validity
            if estimate_price is not None and estimate_price > 0:
                # Create new entry in repository
                self.repo.create(prices)
                self.logger.info(f"Price stored: {prices}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error in fetching price: {e}")
            return False

        # finally:
        #     self.scraper.close()

    def __format_message(self, price_data: dict, previous: dict | None = None) -> str:
        """Format the price data into an HTML message for Telegram.

        Shows an icon at the top: green (up) if estimate rose since previous entry,
        red (down) if fell, yellow when unchanged or unknown.
        """
        ts = price_data.get("timestamp")
        buy_mesqal = price_data.get("buy_price_toman")
        sell_mesqal = price_data.get("sell_price_toman")
        estimate_mesqal = price_data.get("estimate_price_toman")

        # Convert timestamp to Persian datetime
        if ts:
            dt = datetime.fromisoformat(ts).astimezone(self.SCHEDULER_TIME_ZONE)
            persian_dt = jdatetime.datetime.fromgregorian(datetime=dt)
            formatted_ts = persian_dt.strftime("%Y/%m/%d - %H:%M:%S")
        else:
            formatted_ts = "N/A"

        def format_price(p):
            return f"{p:,} تومان" if p is not None else "N/A"

        def calc_per_gram(price_mesqal):
            if price_mesqal is None:
                return None
            per_gram = price_mesqal / self.MESAQAL_TO_GRAM
            return round(per_gram)

        buy_per_gram = calc_per_gram(buy_mesqal)
        sell_per_gram = calc_per_gram(sell_mesqal)

        # Determine direction icon
        direction_icon = "🟡"
        try:
            if (
                previous
                and previous.get("estimate_price_toman") is not None
                and estimate_mesqal is not None
            ):
                prev_est = previous.get("estimate_price_toman")
                if estimate_mesqal > prev_est:
                    direction_icon = "🟢"
                elif estimate_mesqal < prev_est:
                    direction_icon = "🔴"
                else:
                    direction_icon = "⚪"
            else:
                # if we don't have previous or current estimate, keep neutral
                direction_icon = "⚪"
        except Exception:
            direction_icon = "⚪"

        message = (
            f"{direction_icon} <b>گزارش لحظه‌ای قیمت طلا</b>\n\n"
            f"💵 <b>خرید</b>\n"
            f"• 🪙 <b>مظنه:</b> {format_price(buy_mesqal)}\n"
            f"• ⚖️ <b>قیمت هر گرم:</b> {format_price(buy_per_gram)}\n\n"
            f"💰 <b>فروش</b>\n"
            f"• 🪙 <b>مظنه:</b> {format_price(sell_mesqal)}\n"
            f"• ⚖️ <b>قیمت هر گرم:</b> {format_price(sell_per_gram)}\n\n"
            f"⏱️ <b>تاریخ و زمان:</b> {formatted_ts}"
        )

        return message.strip()


# Example if you want Iran time instead of UTC:
# import pytz
# from datetime import datetime

# iran_tz = pytz.timezone("Asia/Tehran")

# repo = PriceRepository(timestamp_func=lambda: datetime.now(iran_tz).isoformat(timespec="seconds"))
