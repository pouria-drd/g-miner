import re
import time
from typing import Dict
from modules.configs import get_logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, WebDriverException


class ZarbahaScraper:
    """
    High-level scraper for extracting gold price from the Zarbaha website.

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

    TIME_OUT: int = 20
    # usecase: Maximum wait time (in seconds) for stabilizing a dynamically-updated number.
    # The website frequently updates prices with JavaScript, so waiting ensures accuracy.

    INTERVAL: float = 0.75
    # usecase: Delay between each check while waiting for the number to stabilize.
    # Balanced between speed and CPU usage.

    BUY_PRICE_RATE: int = 50_000
    # usecase: Business rule (site-specific): buy price = estimate - BUY_PRICE_RATE.

    SELL_PRICE_RATE: int = 130_000
    # usecase: Business rule (site-specific): sell price = estimate + SELL_PRICE_RATE.

    URL: str = "https://zarbaha-co.ir/"
    # usecase: Target website for scraping. Change here if website address changes.

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper, create logger, configure Chrome, and open the site.

        Args:
            headless (bool): Run Chrome in headless mode. Useful for servers and background tasks.
        """
        self.logger = get_logger("ZarbahaScraper")

        self.headless = headless

        # Prepare Selenium options
        options = self._configure_options()

        # Initialize the Chrome WebDriver
        self._init_driver(options)

        # Navigate to the target site immediately
        self._open_website(self.URL)

    # ----------------- Public Method ----------------- #
    def scrape(self) -> Dict[str, int | None]:
        """
        Extract and compute:
            - sell_price_toman
            - buy_price_toman
            - estimate_price_toman

        Returns:
            dict: Contains integer values OR None if extraction failed.

        Error handling:
            - If the raw estimate fails to extract or clean, returns None for all values.
        """
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
            "sell_price_toman": estimate_price + self.SELL_PRICE_RATE,
            "buy_price_toman": estimate_price - self.BUY_PRICE_RATE,
            "estimate_price_toman": estimate_price,
        }

    # ----------------- Cleanup ----------------- #
    def close(self):
        """
        Properly closes and quits the WebDriver instance.

        Avoids zombie browser processes.
        """
        if hasattr(self, "driver") and self.driver:
            self.driver.quit()
            # self.driver = None
            self.logger.info("WebDriver closed")

    # ----------------- Driver Setup ----------------- #
    def _configure_options(self) -> webdriver.ChromeOptions:
        """
        Configure Chrome options for Selenium WebDriver.

        Returns:
            ChromeOptions: Browser configuration object.
        """
        options = webdriver.ChromeOptions()

        # Enables headless mode when running on servers or background tasks
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        # Sandbox settings required for Docker/Linux environments
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--window-size=1920,1080")
        options.add_argument("--blink-settings=imagesEnabled=false")

        return options

    def _init_driver(self, options: webdriver.ChromeOptions):
        """
        Initialize Chrome WebDriver using WebDriverManager.

        Args:
            options: ChromeOptions object.

        Raises:
            WebDriverException: If ChromeDriver fails to start.
        """
        try:
            # Prefer ChromeDriverManager to ensure version compatibility
            service = Service(ChromeDriverManager().install())
            # If you must use hardcoded path, uncomment below and comment above:
            # service = Service("/usr/local/bin/chromedriver")

            self.driver = webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            self.logger.error(f"Failed to start Chrome WebDriver: {e}")
            raise

    def _open_website(self, url: str):
        """
        Navigate the browser to the target website.

        Args:
            url (str): Target URL.

        Raises:
            WebDriverException: If navigation fails.
        """
        try:
            self.driver.get(url)
        except WebDriverException as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            self.close()
            raise

    # ----------------- Price Extraction ----------------- #
    def _wait_for_stable_text(self, element) -> str:
        """
        Wait until the visible text inside an element stops changing.

        Args:
            element (WebElement): Selenium element containing a price.

        Returns:
            str: The stabilized text content.
        """
        last_text = element.text
        elapsed = 0

        while elapsed < self.TIME_OUT:
            time.sleep(self.INTERVAL)
            elapsed += self.INTERVAL

            current_text = element.text

            # If the price stops changing and is not 0, return it
            if current_text == last_text and current_text != "0":
                return current_text

            last_text = current_text

        # Return last-seen value after timeout
        return last_text

    def _fetch_price_element(self, class_name: str):
        """
        Fetch a DOM element by its class name.

        Args:
            class_name (str): HTML class identifier.

        Returns:
            WebElement | None: Returns None if element is not found.
        """
        try:
            return self.driver.find_element(By.CLASS_NAME, class_name)
        except (NoSuchElementException, WebDriverException) as e:
            self.logger.error(f"Error fetching element '{class_name}': {e}")
            return None

    def _get_price(self, class_name: str) -> str:
        """
        Get the displayed price text from a page element.

        Args:
            class_name (str): Class of the element containing the price.

        Returns:
            str: Raw text content. Returns "N/A" if not found.
        """
        elem = self._fetch_price_element(class_name)

        if elem:
            return self._wait_for_stable_text(elem)

        return "N/A"

    # ----------------- Data Cleaning Helpers ----------------- #
    def _clean_price_string(self, value: str) -> int | None:
        """
        Convert a raw string (e.g., "12,345") into an integer (12345).

        Steps:
            - Remove commas, spaces, and non-digit characters.
            - Convert to int.
            - Log errors and return None on failure.

        Args:
            value (str): Raw text extracted from the DOM.

        Returns:
            int | None: Cleaned number or None if invalid.
        """
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

        Args:
            raw_prices (dict): Keys map to raw unprocessed price strings.

        Returns:
            dict: Same keys but cleaned numeric values.
        """
        cleaned = {}
        for key, value in raw_prices.items():
            cleaned[key] = self._clean_price_string(value)
        return cleaned
