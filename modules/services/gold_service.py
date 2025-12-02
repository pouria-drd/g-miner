import jdatetime
from datetime import datetime

from modules.repositories import GoldRepository
from modules.configs import get_settings, get_logger
from modules.scrapers.zarbaha_scraper import ZarbahaScraper


class GoldService:
    """
    Service layer for business logic around gold prices.
    """

    MESAQAL_TO_GRAM = 4.331802  # every mesqal is how many grams?

    def __init__(self):
        self.logger = get_logger("PriceService")
        self.settings = get_settings()

        self.repo = GoldRepository()
        self.scraper = ZarbahaScraper(headless=True)

        self.SCHEDULER_TIME_ZONE = self.settings["SCHEDULER_TIME_ZONE"]

    def get_latest_price(self):
        """Retrieve the most recent stored price."""
        self.fetch_data()
        return self.repo.get_latest()

    def fetch_data(self):
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
            else:
                self.logger.warning("Failed to fetch valid price.")
            return prices

        except Exception as e:
            self.logger.error(f"Error in fetch_and_store: {e}")
            return None

        # finally:
        #     self.scraper.close()

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
