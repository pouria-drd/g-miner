from modules.logger import logging

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, WebDriverException


class ZarbahaScraper:
    """
    Scraper for zarbaha prices.

    Attributes:
        headless (bool): Whether to run Chrome in headless mode.
        timeout (int): Maximum time to wait for stable element text.
        interval (float): Polling interval when waiting for text stability.
        driver (webdriver.Chrome): Selenium WebDriver instance.
        logger (logging.Logger): Logger instance for the scraper.

    Example usage:
        scraper = ZarbahaScraper(headless=True)
        try:
            prices = scraper.scrape_prices()
            print(prices)
        finally:
            scraper.close()
    """

    def __init__(
        self,
        url: str = "https://zarbaha-co.ir/",
        headless: bool = True,
        timeout: int = 10,
        interval: float = 0.5,
    ):
        """
        Initialize the scraper with Chrome WebDriver.

        Args:
            headless (bool): Run browser in headless mode if True.
            timeout (int): Maximum seconds to wait for element text to stabilize.
            interval (float): Seconds between checks for text stability.
        """
        self.logger = logging.getLogger("ZarbahaScraper")
        self.logger.info("Initializing ZarbahaScraper...")

        # Load configurations
        self.url = url
        self.timeout = timeout
        self.interval = interval
        self.headless = headless

        # Build and initialize driver
        options = self._configure_options()
        self._init_driver(options)
        self._open_website(self.url)

    # ----------------- Driver Setup ----------------- #
    def _configure_options(self) -> webdriver.ChromeOptions:
        """Configure Chrome options for the WebDriver."""
        self.logger.info("Configuring Chrome options...")
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return options

    def _init_driver(self, options: webdriver.ChromeOptions):
        """Initialize the Selenium WebDriver with error handling."""
        self.logger.info("Initializing Chrome WebDriver...")
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
            self.logger.info("Chrome WebDriver started successfully.")
        except WebDriverException as e:
            self.logger.error(f"Failed to start Chrome WebDriver: {e}")
            raise

    def _open_website(self, url: str):
        """Open the target website with error handling."""
        self.logger.info(f"Navigating to {url}...")
        try:
            self.driver.get(url)
            self.logger.info(f"Successfully navigated to {url}")
        except WebDriverException as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            if self.driver:
                self.driver.quit()
            raise

    # ----------------- Price Extraction ----------------- #
    def _wait_for_stable_text(self, element) -> str:
        """
        Wait until an element's text stops changing and is non-zero.

        Args:
            element (WebElement): Selenium element to monitor.

        Returns:
            str: The stabilized text of the element.
        """
        last_text = element.text
        elapsed = 0
        while elapsed < self.timeout:
            time.sleep(self.interval)
            elapsed += self.interval
            current_text = element.text
            if current_text == last_text and current_text != "0":
                self.logger.debug(f"Stable text found: {current_text}")
                return current_text
            last_text = current_text
        self.logger.warning(
            f"Text did not stabilize in {self.timeout}s. Using last text: {last_text}"
        )
        return last_text

    def _fetch_price_element(self, class_name: str):
        """
        Retrieve a Selenium element by class name with exception handling.

        Args:
            class_name (str): CSS class name of the element.

        Returns:
            WebElement or None: Found element or None if not found.
        """
        try:
            elem = self.driver.find_element(By.CLASS_NAME, class_name)
            return elem
        except NoSuchElementException:
            self.logger.error(f"Price element not found: {class_name}")
            return None
        except WebDriverException as e:
            self.logger.error(
                f"Selenium error while fetching element {class_name}: {e}"
            )
            return None

    def _get_price(self, class_name: str) -> str:
        """
        Retrieve a price string from an element class name.

        Args:
            class_name (str): CSS class of the price element.

        Returns:
            str: Extracted price or "N/A" if not found.
        """
        self.logger.info(f"Fetching price for class: {class_name}")
        elem = self._fetch_price_element(class_name)
        if elem:
            return self._wait_for_stable_text(elem)
        return "N/A"

    # ----------------- Public Method ----------------- #
    def scrape_prices(self) -> dict:
        """
        Scrape sell, buy, and estimate prices from the website.

        Returns:
            dict: Dictionary containing 'sell_price', 'buy_price', and 'estimate_price'.
        """
        self.logger.info("Starting price scraping...")
        prices = {
            "sell_price": self._get_price("_g_g"),
            "buy_price": self._get_price("_g_k"),
            "estimate_price": self._get_price("_g_m"),
        }
        self.logger.info(f"Scraping completed. Prices: {prices}")
        return prices

    # ----------------- Cleanup ----------------- #
    def close(self):
        """Close the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed.")
