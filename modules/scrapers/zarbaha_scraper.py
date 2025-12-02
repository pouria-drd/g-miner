import re
import time
from typing import Dict
from modules.configs import get_settings, get_logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, WebDriverException


class ZarbahaScraper:
    """
    Scraper for extracting gold price from the Zarbaha website.

    This class is responsible only for:
        - Controlling Selenium WebDriver
        - Extracting raw prices from HTML elements
        - Stabilizing price values rendered by JavaScript on the page
        - Converting raw text into cleaned numeric prices

    Example usage:
        scraper = ZarbahaScraper(headless=True)
        try:
            prices = scraper.scrape_prices()
            print(prices)
        finally:
            scraper.close()
    """

    # usecase: Target website for scraping. Change here if website address changes.
    URL: str = "https://zarbaha-co.ir/"

    # Class-level driver for reuse across all instances
    _shared_driver = None
    _driver_lock = None  # For thread safety

    def __init__(self, headless: bool = True):

        self.logger = get_logger("ZarbahaScraper")

        self.settings = get_settings()

        self.headless = headless

        # usecase: Maximum wait time (in seconds) for stabilizing a dynamically-updated number.
        # The website frequently updates prices with JavaScript, so waiting ensures accuracy.
        self.timeout = int(self.settings["ZARBAHA_TIMEOUT"])

        # usecase: Delay between each check while waiting for the number to stabilize.
        # Balanced between speed and CPU usage.
        self.interval = float(self.settings["ZARBAHA_INTERVAL"])

        # usecase: Business rule (site-specific): buy price = estimate - BUY_PRICE_RATE.
        self.buy_price_rate = int(self.settings["ZARBAHA_BUY_PRICE_RATE"])

        # usecase: Business rule (site-specific): sell price = estimate + SELL_PRICE_RATE.
        self.sell_price_rate = int(self.settings["ZARBAHA_SELL_PRICE_RATE"])

        # Use shared driver instead of creating new one
        if ZarbahaScraper._shared_driver is None:
            options = self._configure_options()
            self._init_driver(options)
        else:
            self.driver = ZarbahaScraper._shared_driver

    def scrape(self) -> Dict[str, int | None]:
        """Extract and compute prices."""
        try:
            # Refresh page to get latest data
            self.driver.refresh()

            # Fetch raw text from the estimate element
            raw_estimate = self._get_price("_g_m")

            # raw_sell_price_toman = self._get_price("_g_g")
            # raw_buy_price_toman = self._get_price("_g_k")

            # Clean and convert the raw text into an integer or fail gracefully
            estimate_price = self._clean_price_string(raw_estimate)

            if estimate_price is None:
                # Return None for all prices on failure
                return {
                    "sell_price_toman": None,
                    "buy_price_toman": None,
                    "estimate_price_toman": None,
                }

            # Compute buy/sell prices using the business rules (fixed offsets)
            return {
                "sell_price_toman": estimate_price + self.sell_price_rate,
                "buy_price_toman": estimate_price - self.buy_price_rate,
                "estimate_price_toman": estimate_price,
            }

        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            return {
                "sell_price_toman": None,
                "buy_price_toman": None,
                "estimate_price_toman": None,
            }

    def close(self):
        """
        DON'T close shared driver - it's reused.
        Call cleanup() on app shutdown instead.
        """
        self.logger.info("Scraper instance released (driver kept alive)")

    # def close(self):
    #     """
    #     Properly closes and quits the WebDriver instance.

    #     Avoids zombie browser processes.
    #     """
    #     if hasattr(self, "driver") and self.driver:
    #         self.driver.quit()
    #         # self.driver = None
    #         self.logger.info("WebDriver closed")

    def cleanup(self):
        """Call this ONCE on application shutdown to close shared driver."""
        if self._shared_driver:
            try:
                self._shared_driver.quit()
                self._shared_driver = None
                self.logger.info("Shared driver closed")
            except Exception as e:
                self.logger.error(f"Error closing shared driver: {e}")

    def _configure_options(self) -> webdriver.ChromeOptions:
        """Configure Chrome for minimal resource usage."""
        options = webdriver.ChromeOptions()

        # Enables headless mode when running on servers or background tasks
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        # Memory optimizations
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-features=VizDisplayCompositor")

        # Reduce memory usage
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")

        # Performance
        options.add_argument("--window-size=1280,720")  # Smaller than 1920x1080
        options.add_argument("--blink-settings=imagesEnabled=false")
        # options.add_argument("--disable-javascript")  # Enable if site works without JS

        # Memory limits
        options.add_argument("--max-old-space-size=512")  # Limit V8 heap

        # Sandbox settings required for Docker/Linux environments
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        return options

    def _init_driver(self, options: webdriver.ChromeOptions):
        """Initialize shared Chrome WebDriver."""
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            ZarbahaScraper._shared_driver = self.driver

            # Navigate to site once
            self._open_website(self.URL)

        except WebDriverException as e:
            self.logger.error(f"Failed to start Chrome WebDriver: {e}")
            raise

    def _open_website(self, url: str):
        """Navigate to target website."""
        try:
            self.driver.get(url)
        except WebDriverException as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            raise

    def _wait_for_stable_text(self, element) -> str:
        """Wait for element text to stabilize."""
        last_text = element.text
        elapsed = 0

        while elapsed < self.timeout:
            time.sleep(self.interval)
            elapsed += self.interval

            current_text = element.text

            # If the price stops changing and is not 0, return it
            if current_text == last_text and current_text != "0":
                return current_text

            last_text = current_text

        # Return last-seen value after timeout
        return last_text

    def _fetch_price_element(self, class_name: str):
        """Fetch DOM element by class name."""
        try:
            return self.driver.find_element(By.CLASS_NAME, class_name)
        except (NoSuchElementException, WebDriverException) as e:
            self.logger.error(f"Error fetching element '{class_name}': {e}")
            return None

    def _get_price(self, class_name: str) -> str:
        """Get price text from page element."""
        elem = self._fetch_price_element(class_name)

        if elem:
            return self._wait_for_stable_text(elem)

        return "N/A"

    # ----------------- Data Cleaning Helpers ----------------- #
    def _clean_price_string(self, value: str) -> int | None:
        """Convert raw string to integer."""
        if not value or value == "N/A":
            return None

        try:
            # Remove all characters except digits
            number = re.sub(r"[^\d]", "", value)
            return int(number)
        except Exception as e:
            self.logger.error(f"Error cleaning price '{value}': {e}")
            return None

    def _format_prices(self, raw_prices: dict) -> dict:
        """
        Convert a dictionary of raw prices into cleaned integer values.
        """
        cleaned = {}
        for key, value in raw_prices.items():
            cleaned[key] = self._clean_price_string(value)
        return cleaned
