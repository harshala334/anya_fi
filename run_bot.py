#!/usr/bin/env python3
"""Run the Telegram bot in polling mode (for development)."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.messaging.telegram_bot import get_bot

if __name__ == "__main__":
    print("🤖 Starting Anya.fi Telegram Bot...")
    print("Press Ctrl+C to stop\n")
    
    try:
        bot = get_bot()
        bot.run_polling()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
