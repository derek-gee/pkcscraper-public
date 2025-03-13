from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from utils import log
from urllib.parse import quote

# Load environment variables from .env
load_dotenv()

# Establish database information
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote(os.getenv("DB_PASSWORD")) # Encode the password

# Establishes a connection to PostgreSQL
def get_db_engine():
    """Creates and returns an SQLAlchemy database engine."""
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(db_url, future=True)

# Provides a connection object for executing SQL queries
def get_db_connection():
    """Provides a connection object for executing SQL queries."""
    engine = get_db_engine()
    return engine.connect()  # Use `.connect()` for queries

# Initialize the database
# This function creates the schema and table if they don't exist
def initialize_db():
    """Creates the cards table in the custom schema if it doesn't exist."""
    create_schema_query = "CREATE SCHEMA IF NOT EXISTS card_inventory;"

    """Creates the cards table if it doesn't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS card_inventory.cards (
        id SERIAL PRIMARY KEY,
        card_title TEXT NOT NULL,
        card_set TEXT NOT NULL,
        price NUMERIC(10,2),
        link TEXT UNIQUE NOT NULL,
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """

    engine = get_db_engine() # Use SQLAlchemy engine
    try:
        with engine.begin() as conn:  # Use `.begin()` instead of `.connect()`
            conn.execute(text(create_schema_query))
            conn.execute(text(create_table_query))
        log("Database initialized successfully in schema card_inventory.")
    except Exception as e:
        log(f"Error initializing database: {e}")
