import pandas as pd
import os
from dbManager import get_db_engine
from utils import log


# Load environment variables from .env
EXPORT_PATH = os.getenv("EXPORT_PATH")

def export_to_excel():
    """Fetches all card data from PostgreSQL and exports it to an Excel file."""
    query = "SELECT * FROM card_inventory.cards ORDER BY updated_at DESC;"

    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

        # Ensure the path is valid and remove unwanted quotes
        clean_export_path = EXPORT_PATH.strip().replace('"', '')

        # Ensure openpyxl is installed
        df.to_excel(clean_export_path, index=False, engine="openpyxl")
        log(f"Data successfully exported to {clean_export_path}")

    except Exception as e:
        log(f"Error exporting data: {e}")
