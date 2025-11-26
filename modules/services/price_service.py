from modules.logger import logging
from modules.repositories import PriceRepository
from modules.scrapers.zarbaha_scraper import ZarbahaScraper


class PriceService:
    """
    Service layer for business logic around gold prices.
    """

    def __init__(self):
        self.logger = logging.getLogger("PriceService")
        self.repo = PriceRepository()
        self.scraper = ZarbahaScraper(headless=True)

    def fetch_data(self):
        """
        Fetch price from Zarbaha and store it in the DB.
        Returns the price dict.
        """
        try:
            prices = self.scraper.scrape_prices()
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


# Example if you want Iran time instead of UTC:
# import pytz
# from datetime import datetime

# iran_tz = pytz.timezone("Asia/Tehran")

# repo = PriceRepository(timestamp_func=lambda: datetime.now(iran_tz).isoformat(timespec="seconds"))
