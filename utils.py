import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename="scraper.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def log(message):
    """Logs messages with timestamps and prints to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_with_timestamp = f"[{timestamp}] {message}"
    print(message_with_timestamp)
    logging.info(message_with_timestamp)
