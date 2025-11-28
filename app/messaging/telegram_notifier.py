import os
import httpx
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_text(text: str, chat_id: str = None):
    """
    Send a text message to your Telegram chat using the Bot API.
    """
    target_chat_id = chat_id or TELEGRAM_CHAT_ID
    
    if not TELEGRAM_BOT_TOKEN or not target_chat_id:
        print("Telegram config missing, skipping send.")
        print("TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)
        print("TELEGRAM_CHAT_ID:", target_chat_id)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
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
