# TCG Price Scraper

## 🎉 Overview

Welcome to the **TCG Price Scraper!** 🎉 This nifty tool is your trading card collection's new best friend, designed to keep you in the loop about your collection's value without lifting a finger. Say goodbye to manual price checks and hello to automation! 🚀

## ✨ Features

Our TCG Price Scraper is packed with features designed to make tracking card prices effortless and fun! Here’s what you get:

### 🔍 **Automated Price Tracking**
- No more manually checking multiple sites—our scraper fetches the latest card prices automatically.
- Supports bulk lookups so you can monitor an entire collection at once.
- Configurable price update intervals to fit your needs.

### 💰 **Multi-Source Price Comparisons** *(Coming Soon!)*
- Future updates will support price fetching from multiple sources, giving you a full market overview.

### 🖥️ **User-Friendly Interface**
- Simple and intuitive setup, even if you’re not a tech wizard.
- Organized price tracking for your entire collection, making it easy to view changes over time.

### 📢 **Discord Notifications**
- Get real-time alerts sent directly to your Discord server.
- Customizable triggers—get notified when a card reaches a certain price, increases in value, or drops below your set threshold.
- Supports multiple Discord channels for better organization.

### 📊 **Historical Price Data & Trends** *(In Development!)*
- Track how card prices change over time and make better buying/selling decisions.
- Graphical representation of price fluctuations.

### ⚙️ **Configurable & Extensible**
- Easily adjust settings like frequency of price updates, notification preferences, and scraping sources.
- Built with scalability in mind—easily add new TCGs, price sources, or notification methods.

---

## 🚀 Getting Started

Ready to dive in? Follow these simple steps:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/derek-gee/pkcscraper-public.git
   ```

2. **Install Dependencies**:

   Navigate to the project directory and install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Settings**:

   Customize the `config.yaml` file to suit your preferences, including Discord integration and scraping intervals.

4. **Run the Scraper**:

   ```bash
   python main.py
   ```

---

## 📂 File Structure

Here's a quick overview of the project structure:

```
/pkcscraper-public
├── .gitignore                # Specifies files and directories to be ignored by Git
├── .pre-commit-config.yaml   # Configuration for pre-commit hooks
├── PATCH_NOTES.md            # Notes on patches and updates
├── README.md                 # Project overview and instructions
├── VERSION                   # Current version of the project
├── dataFetcher.py            # Fetches price data from PriceCharting
├── dataSanitizer.py          # Cleans and validates fetched data
├── dataStorage.py            # Manages data storage operations
├── dbManager.py              # Handles database interactions
├── discordNotifier.py        # Sends notifications to Discord
├── excelBackupCleaner.py     # Cleans up old Excel backups
├── excelExport.py            # Exports data to Excel files
├── main.py                   # Entry point to run the scraper
├── scraperUI.py              # Graphical User Interface for the scraper
└── utils.py                  # Helper functions and utilities
```

---

## 🛠️ Technologies Used

This project is built using the following technologies:

- **Python** 🐍 - Core programming language for the scraper.
- **BeautifulSoup** 🏗️ - Web scraping library for extracting data from websites.
- **Requests** 🌐 - Handles HTTP requests to fetch price data.
- **PostgreSQL** 🗄️ - Stores and manages price history data.
- **Pandas** 📊 - Processes and analyzes scraped data.
- **Excel (via Pandas & OpenPyXL)** 📄 - Exports price data into spreadsheets for easy analysis.
- **Discord Webhooks** 🔔 - Sends real-time notifications directly to your Discord server.

---

## 🤝 Contributing

We love contributions! If you have ideas, suggestions, or improvements, feel free to fork the repository and submit a pull request. Let's make **TCG Price Scraper** even better together! 💪

I maintain the list of ongoing enhancements that I plan on doing on this Trello board:
https://trello.com/b/2D6wjQyh/https-githubcom-derek-gee

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Happy collecting! May your cards always be in mint condition. 🃏✨
