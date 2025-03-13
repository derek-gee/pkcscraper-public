import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from utils import log
import pandas as pd
import sys

def get_card_details(url, processed_count=None, total_cards=None):
    """Fetches card details from PriceCharting and returns card title, set, and price."""
    parsed_url = urlparse(url)
    if not (parsed_url.netloc.endswith("pricecharting.com") and parsed_url.scheme in ["http", "https"]):
        log(f"Invalid URL: {url}")
        return None, None, None

    headers = {'User-Agent': 'Mozilla/5.0'}
    retries = 3

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                log(f"Rate limited. Retrying ({attempt+1}/{retries})...")
                time.sleep(random.uniform(5, 10))
                continue
            if response.status_code != 200:
                return None, None, None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract price
            price_element = soup.find("span", class_="price js-price")
            price = price_element.text.strip() if price_element else None

            # Extract card title and set
            title_element = soup.find("h1", id="product_name")
            card_title = title_element.contents[0].strip() if title_element and title_element.contents else None
            set_element = title_element.find("a") if title_element else None
            card_set = set_element.text.strip() if set_element else None

            if processed_count is not None and total_cards is not None:
                sys.stdout.write(f"\r[Progress] {(processed_count+1)/total_cards*100:.2f}% ({processed_count+1}/{total_cards})")
                sys.stdout.flush()

            return card_title, card_set, price

        except requests.RequestException as e:
            log(f"Request error: {e}")
            time.sleep(random.uniform(1, 3))

    return None, None, None

def fetch_card_data(link, index):
    """Fetch card details for a given link and ensure the price is numeric."""
    if pd.notna(link):
        card_title, card_set, price = get_card_details(link)

        try:
            cleaned_price = float(price.replace("$", "").replace(",", "")) if price else None
        except ValueError:
            cleaned_price = None

        return index, card_title or "Title not found", card_set or "Set not found", cleaned_price

    return index, "Title not found", "Set not found", None
