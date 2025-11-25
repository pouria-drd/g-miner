import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ZarbahaScraper:
    """Scraper for https://zarbaha-co.ir/ prices.

    Example usage:
        scraper = ZarbahaScraper(headless=True)
        try:
            prices = scraper.scrape_prices()
            print(prices)
        finally:
            scraper.close()
    """

    def __init__(self, headless: bool = True, timeout: int = 10, interval: float = 0.5):

        self.timeout = timeout
        self.interval = interval
        self.headless = headless

        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        self.driver.get("https://zarbaha-co.ir/")

    def _wait_for_stable_text(self, element) -> str:
        """Wait until element text stops changing and is non-zero."""
        last_text = element.text
        elapsed = 0
        while elapsed < self.timeout:
            time.sleep(self.interval)
            elapsed += self.interval
            current_text = element.text
            if current_text == last_text and current_text != "0":
                return current_text
            last_text = current_text
        return last_text  # fallback

    def _get_price(self, class_name: str) -> str:
        """Get price from element class name."""
        elem = self.driver.find_element(By.CLASS_NAME, class_name)
        return self._wait_for_stable_text(elem)

    def scrape_prices(self) -> dict:
        """Scrape sell, buy, and estimate prices and return as dictionary."""
        prices = {
            "sell_price": self._get_price("_g_g"),
            "buy_price": self._get_price("_g_k"),
            "estimate_price": self._get_price("_g_m"),
        }
        return prices

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()


# Example usage
# if __name__ == "__main__":
#     scraper = ZarbahaScraper(headless=True)
#     try:
#         prices = scraper.scrape_prices()
#         print(prices)
#     finally:
#         scraper.close()
