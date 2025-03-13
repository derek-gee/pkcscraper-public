import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import logging
from datetime import datetime
from dotenv import load_dotenv  # type: ignore
from urllib.parse import urlparse
import time
import random
import re  # Added for better price extraction

# Load environment variables from .env
load_dotenv()

# Get Environment Variables
FILE_PATH = os.getenv("FILE_PATH")

# Configure logging
logging.basicConfig(filename="scraper_ui.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def log(message):
    print(message)
    logging.info(message)

# Validate URL function
def is_valid_pricecharting_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc.endswith("pricecharting.com") and parsed_url.scheme in ["http", "https"]

# Function to scrape card details
def get_card_details(url):
    if not is_valid_pricecharting_url(url):
        log("Invalid URL entered.")
        return None, None, None

    headers = {'User-Agent': 'Mozilla/5.0'}  # Helps prevent being blocked
    retries = 3

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                time.sleep(random.uniform(5, 10))  # Avoid rate-limiting
                continue
            if response.status_code != 200:
                return None, None, None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract card title and set
            title_element = soup.find("h1", id="product_name")
            card_title = title_element.contents[0].strip() if title_element and title_element.contents else "Title not found"
            set_element = title_element.find("a") if title_element else None
            card_set = set_element.text.strip() if set_element else "Set not found"

            # Extract price from multiple potential locations
            price_element = soup.find("span", class_="price js-price")  # First method
            if not price_element:
                # Try looking inside <td id="used_price">
                used_price_element = soup.find("td", id="used_price")
                if used_price_element:
                    price_element = used_price_element.find("span", class_="price js-price")

            # Extract and clean the price
            price_text = price_element.text.strip() if price_element else ""
            price_match = re.search(r"(\d+\.\d{2})", price_text)
            ungraded_price = float(price_match.group(1)) if price_match else None

            return card_title, card_set, ungraded_price

        except requests.RequestException as e:
            log(f"Request error: {e}")
            time.sleep(random.uniform(1, 3))

    return None, None, ungraded_price

# Function to sanitize Excel input
def sanitize_excel_input(value):
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value

# Function to add data to Excel
def add_to_excel(url):
    card_title, card_set, ungraded_price = get_card_details(url)

    # Ensure ungraded_price has a default value
    if ungraded_price is None:
        ungraded_price = "Price not found"

    if not card_title or card_title == "Title not found":
        messagebox.showerror("Error", "Failed to retrieve card details. Check the URL.")
        return

    # Define column names explicitly
    columns = ["Card Title", "Set", "Ungraded Price", "Link"]

    # Load existing Excel file or create a new DataFrame
    if os.path.exists(FILE_PATH):
        df = pd.read_excel(FILE_PATH)

        # Ensure the DataFrame has the correct columns
        missing_cols = [col for col in columns if col not in df.columns]
        for col in missing_cols:
            df[col] = None  # Add missing columns if necessary

        # Ensure "Link" column exists
        if "Link" in df.columns:
            # Check if URL already exists
            if url in df["Link"].astype(str).values:
                messagebox.showwarning("Duplicate Entry", "This card has already been added.")
                return
        else:
            df["Link"] = pd.Series(dtype=str)
    else:
        # Create an empty DataFrame with defined columns and types
        df = pd.DataFrame(columns=columns)

    # Prepare the new entry as a DataFrame
    new_entry_df = pd.DataFrame([{
        "Card Title": sanitize_excel_input(card_title),
        "Set": sanitize_excel_input(card_set),
        "Ungraded Price": ungraded_price,  # Ensuring price is always stored correctly
        "Link": url
    }], columns=columns)  # Ensure same column order

    # Fix FutureWarning by excluding all-NA DataFrames
    if df.empty or df.isna().all().all():
        df = new_entry_df.copy()  # Direct assignment if empty or all-NA
    else:
        # Manually append new row(s) instead of using concat
        for _, row in new_entry_df.iterrows():
            df.loc[len(df)] = row.values  # Append row manually


    # Save updated Excel file
    df.to_excel(FILE_PATH, index=False)

    messagebox.showinfo("Scraping Complete", f"Card: {card_title}\nSet: {card_set}\nUngraded Price: ${ungraded_price if isinstance(ungraded_price, float) else 'N/A'}")
    log(f"Added: {card_title}, {card_set}, ${ungraded_price if isinstance(ungraded_price, float) else 'N/A'}")

# UI Setup
def create_ui():
    root = tk.Tk()
    root.title("TCG Scraper UI")
    root.geometry("400x200")

    tk.Label(root, text="Enter PriceCharting URL:").pack(pady=10)
    url_entry = tk.Entry(root, width=50)
    url_entry.pack()

    def on_submit():
        url = url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return
        add_to_excel(url)

    submit_btn = tk.Button(root, text="Scrape & Add", command=on_submit)
    submit_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_ui()
