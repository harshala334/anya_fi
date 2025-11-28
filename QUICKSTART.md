# 🚀 Quick Start Guide

## Prerequisites

- PostgreSQL installed
- Python 3.10+ with venv
- Telegram bot token ([Get one from @BotFather](https://t.me/botfather))
- OpenAI API key

## Setup (5 minutes)

### 1. Start PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Optional: auto-start on boot
```

### 2. Create Database

```bash
./setup_postgres.sh
```

### 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required settings:**
```bash
DATABASE_URL=postgresql://anya_user:anya_password@localhost/anya_db
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENAI_API_KEY=sk-your_openai_key_here
```

### 4. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Run Migrations

```bash
alembic upgrade head
```

### 6. Start the Bot

```bash
python run_bot.py
```

## Test It!

1. Open Telegram
2. Find your bot (search by username)
3. Send `/start`
4. Try: "I want to save ₹50,000 for a laptop"

## Troubleshooting

**Bot not responding?**
- Check `TELEGRAM_BOT_TOKEN` in `.env`
- Ensure bot is running (`python run_bot.py`)

**Database errors?**
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check `DATABASE_URL` in `.env`

**OpenAI errors?**
- Verify `OPENAI_API_KEY` in `.env`
- Bot has fallback responses if OpenAI unavailable

## Next Steps

- Read `walkthrough.md` for architecture details
- See `implementation_plan.md` for Phase 2 (Mock AA)
- Check `aa_setup_guide.md` for real AA integration

## Commands

- `/start` - Get started
- `/help` - Show help
- `/mystats` - Check budget status
- `/goals` - View active goals

Or just chat naturally! 💬
