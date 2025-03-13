import requests
import os
from utils import log
import openai
from sqlalchemy import text
from dbManager import get_db_connection

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def fetch_top_5_expensive_cards():
    """Retrieves the top 5 most expensive cards from the database."""
    query = text("""
        SELECT card_title, card_set, price
        FROM card_inventory.cards
        WHERE price IS NOT NULL
        ORDER BY price DESC
        LIMIT 5;
    """)

    try:
        with get_db_connection() as conn:
            result = conn.execute(query).fetchall()  # ✅ Corrected execution
        return result
    except Exception as e:
        log(f"Database error: {e}")
        return []

def generate_fun_message(total_price, total_cards):
    """Generates a fun Discord message using OpenAI."""
    prompt = f"""
        Create a short, engaging message about a collection worth ${total_price:.2f}
        with {total_cards} cards. Keep it under 250 characters and don't use quotations.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log(f"OpenAI error: {e}")
        return f"Your collection is worth ${total_price:.2f} with {total_cards} cards."

def send_discord_message(total_price, total_cards):
    """Sends a Discord embed notification with a dynamically generated description."""
    if not DISCORD_WEBHOOK_URL:
        log("Discord Webhook URL missing.")
        return

    top_cards = fetch_top_5_expensive_cards()

    # Generate a fun description dynamically
    embed_description = generate_fun_message(total_price, total_cards)

    # Format Top 5 Cards with Numbered Bullets & No Bolding
    if top_cards:
        top_cards_text = "\n".join([
            f"{idx + 1}. {card[0]} ({card[1]}) - ${card[2]:.2f}"
            for idx, card in enumerate(top_cards)
        ])
    else:
        top_cards_text = "No pricing data available."

    # Discord Embed Payload
    embed = {
        "title": "📊 Base Set Price Update",
        "description": embed_description,  # <-- Dynamic AI-generated description
        "color": 0x3498db,  # Blue color
        "fields": [
            {
                "name": "💰 Total Ungraded Value",
                "value": f"${total_price:.2f}",
                "inline": True
            },
            {
                "name": "📦 Total Cards Analyzed",
                "value": f"{total_cards}",
                "inline": True
            },
            {
                "name": "🔥 Top 5 Most Expensive Cards",
                "value": top_cards_text if top_cards_text else "No pricing data available.",
                "inline": False
            },
            {
                "name": "🔗 Source",
                "value": "[PriceCharting](https://www.pricecharting.com/)",
                "inline": False
            }
        ]
    }

    payload = {"embeds": [embed]}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

    if response.status_code == 204:
        log("Discord message sent successfully.")
    else:
        log(f"Failed to send Discord message. Response: {response.text}")
