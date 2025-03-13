from dbManager import get_db_engine
from utils import log
from sqlalchemy import text
import sys

def store_data_in_db(card_title, card_set, price, link, processed_count=None, total_cards=None):
    """Inserts or updates card data in PostgreSQL and logs progress."""
    try:
        engine = get_db_engine()
        with engine.begin() as conn:  # ✅ Transaction handled automatically
            query = text("""
                INSERT INTO card_inventory.cards (card_title, card_set, price, link, updated_at)
                VALUES (:card_title, :card_set, :price, :link, NOW())
                ON CONFLICT (link) DO UPDATE
                SET price = EXCLUDED.price, updated_at = NOW();
            """)
            conn.execute(query, {
                "card_title": card_title,
                "card_set": card_set,
                "price": price,
                "link": link
            })

        # ✅ First, overwrite the same progress line in the terminal
        if processed_count is not None and total_cards is not None:
            progress = (processed_count + 1) / total_cards * 100
            sys.stdout.write(f"\r[Progress] {progress:.2f}% ({processed_count + 1}/{total_cards})   ")
            sys.stdout.flush()  # ✅ Force immediate update

    except Exception as e:
        log(f"Database error: {e}")
