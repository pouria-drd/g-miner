# ⛏️ g-miner: Gold Price Scraper Telegram Bot

**g-miner** is a Python-based Telegram bot that automatically scrapes the latest gold price data from a target website, stores it locally, and broadcasts updates to a specified Telegram channel according to a configurable schedule.

---

## 🌟 Features

- **Gold Price Scraping:** Extracts live gold price data reliably from [zarbaha-co.ir](https://zarbaha-co.ir/) using Selenium and BeautifulSoup.
- **Flexible Scheduling:** Configure scraping frequency, start/end times, and timezone via environment variables.
- **Data Persistence:** Stores historical price records in a local JSON file using a Repository pattern.
- **Telegram Integration:** Sends real-time, formatted gold price updates directly to a Telegram channel.
- **Modular Architecture:** Clear separation of concerns with Scraper, Repository, Service, and Bot layers for maintainability.

---

## ⚙️ Technology Stack

- **Language:** Python 3.9+  
- **Bot Framework:** `python-telegram-bot`  
- **Web Scraping:** Selenium, webdriver-manager, BeautifulSoup4  
- **Data Storage:** JSON file  
- **Scheduling:** APScheduler  
- **Target Website:** [https://zarbaha-co.ir/](https://zarbaha-co.ir/)  

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.9+ installed  
- Telegram Bot Token (via BotFather)  
- Telegram Channel ID to post updates  
- Chrome browser (for Selenium)

### 1. Clone the Repository

```bash
git clone https://github.com/pouria-drd/g-miner
cd g-miner
```

### 2. Install Dependencies

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

> Make sure `requirements.txt` includes: `python-telegram-bot`, `selenium`, `webdriver-manager`, `beautifulsoup4`, `python-dotenv`, `apscheduler`.

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```ini
# -------------------------
# Telegram Configuration
# -------------------------
TELEGRAM_CHANNEL_ID="@my_channel"
ADMIN_CHAT_IDS="your_account_id(189855...),another_account_id(123456...)"
TELEGRAM_TOKEN="your_bot_token_from_botfather"
TELEGRAM_PROXY_URL="socks5://username:password@domain:port"

# -------------------------
# Scheduler Configuration
# -------------------------
SCHEDULER_ENABLED="True"
SCHEDULER_END_TIME="20:30"
SCHEDULER_START_TIME="11:00"
SCHEDULER_INTERVAL_MINUTES="5"
SCHEDULER_TIME_ZONE="Asia/Tehran"

# -------------------------
# Zarbaha Scraper Configuration
# -------------------------
ZARBAHA_TIMEOUT="20"
ZARBAHA_INTERVAL="1"
ZARBAHA_BUY_PRICE_RATE="50000"
ZARBAHA_SELL_PRICE_RATE="130000"

# -------------------------
# Celery Configuration
# -------------------------
BROKER_URL="redis://localhost:6379/0"
RESULT_BACKEND="redis://localhost:6379/1"
```

Replace the values with your own configurations.
```

### 4. Run the Bot

```bash
python main.py
```

The bot will automatically start scraping and sending gold price updates according to the schedule.

---

## 🧩 Architecture Overview

- **Scraper (`zarbaha_scraper.py`)** – Controls the browser and extracts raw gold price data.  
- **Repository (`db_repository.py`)** – Reads/writes structured data to `db/prices.json`.  
- **Service (`price_service.py`)** – Orchestrates scraping, validation, and data persistence.  
- **Bot Entrypoint (`telegram_bot.py`)** – Sets up Telegram communication, scheduling, and posting updates.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit pull requests.  

GitHub: [https://github.com/pouria-drd/g-miner](https://github.com/pouria-drd/g-miner)
