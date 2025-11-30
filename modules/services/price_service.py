import jdatetime
from datetime import datetime
from zoneinfo import ZoneInfo

from modules.configs import Settings
from modules.configs import get_logger
from modules.repositories import PriceRepository
from modules.scrapers.zarbaha_scraper import ZarbahaScraper


class PriceService:
    """
    Service layer for business logic around gold prices.
    """

    MESAQAL_TO_GRAM = 4.331802  # هر مثقال چند گرم است؟

    def __init__(self, env_config: Settings):
        self.logger = get_logger("PriceService")
        self.env_config = env_config

        self.repo = PriceRepository(db_file=self.env_config.DB_FILE)
        self.scraper = ZarbahaScraper(headless=True)

        self.TIME_ZONE = ZoneInfo(self.env_config.SCHEDULER_TIME_ZONE)

    def fetch_data(self):
        """
        Fetch price from Zarbaha and store it in the DB.
        Returns the price dict.
        """
        try:
            prices = self.scraper.scrape()
            if prices["estimate_price_toman"] is not None:
                self.repo.create(prices)
                self.logger.info(f"Price stored: {prices}")
            else:
                self.logger.warning("Failed to fetch valid price.")
            return prices

        except Exception as e:
            self.logger.error(f"Error in fetch_and_store: {e}")
            return None

        # finally:
        #     self.scraper.close()

    def get_latest_price(self):
        """Retrieve the most recent stored price."""
        return self.repo.get_latest()

    def format_message(self, price_data: dict, previous: dict | None = None) -> str:
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
            dt = datetime.fromisoformat(ts).astimezone(self.TIME_ZONE)
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
