#!/bin/bash

# Start the Telegram bot in the background
echo "🤖 Launching run_bot.py..."
python run_bot.py &
BOT_PID=$!
echo "✅ Bot process started with PID: $BOT_PID"

# Start the FastAPI web server in the foreground
uvicorn app.main:app --host 0.0.0.0 --port $PORT
