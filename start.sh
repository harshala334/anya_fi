#!/bin/bash

# Start the Telegram bot in the background
python run_bot.py &

# Start the FastAPI web server in the foreground
uvicorn app.main:app --host 0.0.0.0 --port $PORT
