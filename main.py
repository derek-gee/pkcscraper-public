import os
import sys
import time
import shutil
import pytz
import schedule
import pandas as pd  # type: ignore
from datetime import datetime
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importing modules from the project
import dbManager
from dataFetcher import fetch_card_data
from utils import log
from excelExport import export_to_excel
from excelBackupCleaner import cleanup_old_backups
from dataStorage import store_data_in_db
from discordNotifier import send_discord_message

# Define Pacific Time Zone
PACIFIC_TZ = pytz.timezone("America/Los_Angeles")

# Fetch the environment variable for file path
FILE_PATH = os.getenv("FILE_PATH")

# Initialize the PostgreSQL database
dbManager.initialize_db()

def get_file_path():
    """Retrieve the file path from environment variables."""
    file_path = os.getenv("FILE_PATH")
    if not file_path:
        log("Error: FILE_PATH is not set in environment variables.")
        sys.exit(1)
    return file_path

def backup_excel(file_path):
    """Creates a backup of the existing Excel file before modifying."""
    backup_path = file_path.replace(".xlsx", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    shutil.copy(file_path, backup_path)
    log(f"Backup created: {backup_path}")
    return backup_path

def load_excel(file_path):
    """Loads the Excel file and validates required columns."""
    if not os.path.exists(file_path):
        log("Error: Excel file not found.")
        return None

    log(f"Loading Excel file: {file_path}")
    df = pd.read_excel(file_path)

    required_columns = ["Card Title", "Set", "Link", "Ungraded Price"]
    if not all(col in df.columns for col in required_columns):
        log("Error: Missing required columns in Excel file.")
        return None

    return df

def update_excel(file_path):
    """
    Reads the Excel file, fetches pricing data in parallel, updates the database, and exports to a new Excel file.
    Returns total price and number of cards updated.
    """
    df = load_excel(file_path)
    if df is None:
        return None, None

    # Create a backup before modifying
    backup_excel(file_path)
    cleanup_old_backups(file_path)  # Cleanup old backups

    # Extract links
    links = df["Link"].dropna().tolist()
    total_cards = len(links)
    processed_count = 0
    lock = Lock()

    start_time = time.time()

    # Fetch card data using multithreading
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {executor.submit(fetch_card_data, link, idx): idx for idx, link in enumerate(links)}

        for future in as_completed(future_to_index):
            try:
                index, card_title, card_set, price = future.result()

                # Update the Excel DataFrame
                df.at[index, "Card Title"] = card_title
                df.at[index, "Set"] = card_set
                df.at[index, "Ungraded Price"] = float(price) if price is not None else None

                # Store Data in PostgreSQL
                store_data_in_db(card_title, card_set, price, links[index], processed_count, total_cards)

                # Update progress
                with lock:
                    processed_count += 1
                    progress = (processed_count / total_cards) * 100
                    sys.stdout.write(f"\r[Progress] {progress:.2f}% ({processed_count}/{total_cards})")
                    sys.stdout.flush()
            except Exception as e:
                log(f"Error processing card data: {e}")

    elapsed_time = time.time() - start_time
    log(f"\nScraping completed in {elapsed_time:.2f} seconds.")

    # Clean price formatting
    df["Ungraded Price"] = df["Ungraded Price"].astype(str).str.replace("$", "").str.replace(",", "")
    df["Ungraded Price"] = pd.to_numeric(df["Ungraded Price"], errors='coerce')

    total_price = df["Ungraded Price"].sum()
    total_cards = df["Ungraded Price"].count()

    # Save updated file
    df.to_excel(file_path, index=False)
    log(f"Excel file updated: {file_path}")

    # Export database data to Excel
    export_to_excel()

    return total_price, total_cards

def run_script():
    """Runs the update_excel process and sends a Discord notification."""
    log("Scheduled script execution started")
    file_path = get_file_path()
    total_price, total_cards = update_excel(file_path)

    if total_price is not None and total_cards is not None:
        send_discord_message(total_price, total_cards)

def display_next_run():
    """Continuously updates the next scheduled run time in the console."""
    while True:
        now = datetime.now(pytz.utc).astimezone(PACIFIC_TZ)
        next_run = schedule.next_run()

        if next_run:
            next_run_pacific = next_run.astimezone(PACIFIC_TZ)
            sys.stdout.write(f"\rNext run at: {next_run_pacific.strftime('%Y-%m-%d %H:%M:%S %Z')}   ")
            sys.stdout.flush()

        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Schedule the script to run at 7:00 AM Pacific Time daily
schedule.every().day.at("07:00").do(run_script)

if __name__ == "__main__":
    file_path = get_file_path()
    total_price, total_cards = update_excel(file_path)

    if total_price is not None and total_cards is not None:
        send_discord_message(total_price, total_cards)

    # Start monitoring the next run time
    display_next_run()
