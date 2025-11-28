import os
import httpx
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_text(text: str):
    """
    Send a text message to your Telegram chat using the Bot API.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram config missing, skipping send.")
        print("TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)
        print("TELEGRAM_CHAT_ID:", TELEGRAM_CHAT_ID)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
        print("Telegram API response:", data)
        return data
