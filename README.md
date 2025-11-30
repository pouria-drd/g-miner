# ⛏️ g-miner: Gold Price Scraper Telegram Bot

**g-miner** is a Python-based Telegram bot designed to automatically scrape the latest gold price data from a specified external website, persist this information, and broadcast updates to a designated Telegram channel within specific operating hours.

---

## 🌟 Features

- **Gold Price Scraping:** Uses Selenium to reliably extract live gold price estimates from the target website ([https://zarbaha-co.ir/](https://zarbaha-co.ir/)).
- **Highly Configurable Scheduling:** Uses environment variables to precisely control the scraping frequency, start time, end time, and timezone.
- **Data Persistence:** Uses a local JSON file (following the Repository pattern) to store historical price records and retrieve the latest saved data.
- **Telegram Integration:** Sends formatted, real-time gold price updates directly to a configured Telegram channel.
- **Modular Architecture:** Structured with clear separation of concerns (Scraper, Repository, and Service layers) for maintainability.

---

## ⚙️ Core Technology

- **Language:** Python  
- **Bot Framework:** python-telegram-bot  
- **Web Scraping:** Selenium and webdriver-manager and beautifulsoup4
- **Database:** JSON file
- **Scheduling:** APScheduler
- **Target Site:** [https://zarbaha-co.ir/](https://zarbaha-co.ir/)  

---

## 🚀 Setup and Installation

### Prerequisites

- Python 3.9+  
- A Telegram Bot Token (from BotFather)  
- A Telegram Channel ID (where the prices will be posted)  
- Chrome browser installed (required for Selenium)  

### 1. Clone the Repository

```bash
git clone https://github.com/pouria-drd/g-miner
cd g-miner
```

### 2. Install Dependencies

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install all required Python packages
pip install -r requirements.txt
```

> Note: Ensure your `requirements.txt` includes: `python-telegram-bot`, `selenium`, `webdriver-manager`, `python-dotenv`, etc.

### 3. Set Up Environment Variables:

    Create a `.env` file in the project root and add the following:

    ```ini
    # ---------------------------------------------------------------
    # Scheduler Configuration
    # ---------------------------------------------------------------
    SCHEDULER_ENABLED="True"
    SCHEDULER_END_TIME="20:30"
    SCHEDULER_START_TIME="11:00"
    SCHEDULER_INTERVAL_MINUTES="5"
    SCHEDULER_TIME_ZONE="Asia/Tehran"

    # ---------------------------------------------------------------
    # Telegram Configuration
    # ---------------------------------------------------------------
    TELEGRAM_TOKEN="your-telegram-bot-token (from BotFather)"
    ADMIN_CHAT_IDS="your-admin-chat-id(s) (e.g., 78557,85875)"
    TELEGRAM_CHANNEL_ID="your-channel-id(e.g., @mychannel, or -100123456789)"
    
    TELEGRAM_PROXY_URL="your-proxy-url (optional) (e.g., socks5://....)"

    ```
### 4. Running the Bot

Start the main application script (e.g., `main.py`):

```bash
python main.py
```

The bot will run the price scraping job according to the configured schedule.

---

## 🧩 Architecture Overview

The application follows a clear separation of concerns:

- **Scraper** (e.g., `zarbaha_scraper.py`): Responsible for browser control (Selenium) and raw data extraction.  
- **Repository** (e.g., `db_repository.py`): Handles reading/writing structured data to the `db/prices.json` file.  
- **Service** (e.g., `price_service.py`): Orchestrates the workflow: calls the Scraper, validates data, and saves it via the Repository.  
- **Bot Entrypoint** (e.g., `telegram_bot.py`): Sets up the python-telegram-bot application, defines the scheduled job, and handles communication with Telegram.  

---

## 🤝 Contributing

This project is open for contributions.  

GitHub Repository: [https://github.com/pouria-drd/g-miner](https://github.com/pouria-drd/g-miner)
