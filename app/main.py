from fastapi import FastAPI, BackgroundTasks, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

# New imports
from app.config import settings
from app.db.database import get_db, init_db
from app.db.models import User, Goal, Transaction, GoalStatus, TransactionCategory
from app.messaging.telegram_bot import get_bot
from app.messaging.telegram_notifier import send_telegram_text
from app.messaging.whatsapp_bot import get_whatsapp_bot

# Legacy imports for backward compatibility
from app.models import SetGoalRequest, AddTransactionRequest
from app.storage import (
    USERS,
    add_transaction as legacy_add_transaction,
    update_goal as legacy_update_goal,
    get_user as legacy_get_user,
    get_user_transactions as legacy_get_user_transactions,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("🚀 Starting Anya.fi...")
    
    # Initialize database (creates tables if they don't exist)
    try:
        init_db()
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("Continuing with in-memory storage...")
    
    # Start Telegram bot in polling mode (for development)
    # In production, use webhooks instead
    if settings.telegram_bot_token:
        try:
            bot = get_bot()
            # Note: bot.run_polling() blocks, so we don't call it here
            # Instead, run it separately or use webhooks
            print("✅ Telegram bot initialized")
        except Exception as e:
            print(f"⚠️  Telegram bot initialization failed: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Anya.fi...")


app = FastAPI(
    title="Anya.fi – Financial Co-Pilot",
    description="Agentic AI for financial guidance on Telegram",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== NEW ENDPOINTS ====================

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "app": "Anya.fi",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Conversational Telegram bot",
            "Conversational WhatsApp bot",
            "MCP agent with Groq LLM",
            "PostgreSQL database",
            "Redis session management",
            "Behavioral nudging"
        ]
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "database": "connected" if settings.database_url else "not configured",
        "telegram": "configured" if settings.telegram_bot_token else "not configured",
        "whatsapp": "configured" if settings.whatsapp_access_token else "not configured",
        "groq": "configured" if settings.groq_api_key else "not configured"
    }


# ==================== WHATSAPP WEBHOOK ENDPOINTS ====================

@app.get("/webhook/whatsapp")
async def whatsapp_webhook_verify(
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge")
):
    """
    WhatsApp webhook verification endpoint.
    
    This is called by Meta when you set up the webhook.
    """
    bot = get_whatsapp_bot()
    result = bot.verify_webhook(mode, token, challenge)
    
    if result:
        return int(result)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/whatsapp")
async def whatsapp_webhook_handler(request: Request):
    """
    WhatsApp webhook message handler.
    
    Receives incoming WhatsApp messages and processes them.
    """
    body = await request.json()
    bot = get_whatsapp_bot()
    result = await bot.handle_webhook(body)
    return result


# ==================== LEGACY ENDPOINTS (Backward Compatibility) ====================

def calc_month_nonessential_spend(user_id: str) -> float:
    """
    Calculate this month's total non-essential spend (shopping, food, entertainment)
    for the given user.
    """
    txs = legacy_get_user_transactions(user_id)
    now = datetime.utcnow()
    month_start = datetime(year=now.year, month=now.month, day=1)

    total = 0.0
    for tx in txs:
        if tx["timestamp"] >= month_start and tx["category"] in ("shopping", "food", "entertainment"):
            total += float(tx["amount"])
    return total


def evaluate_purchase(user: dict, tx: dict, month_spend_nonessential_before: float):
    """
    Decide if the purchase is OK / borderline / hurting the goal.

    Returns:
      verdict: "GREEN" | "ORANGE" | "RED"
      label: short text
      remaining_after: remaining non-essential budget after this purchase
    """
    nonessential_budget = user["month_nonessential_budget"]
    remaining_before = nonessential_budget - month_spend_nonessential_before
    remaining_after = remaining_before - tx["amount"]

    # Simple rules for demo:
    # - GREEN: comfortably above 50% of saving goal left in budget after this purchase
    # - ORANGE: still positive budget, but below that comfort zone
    # - RED: negative budget -> this is hurting the saving goal
    if remaining_after >= user["month_saving_goal"] * 0.5:
        verdict = "GREEN"
        label = "probably okay for your saving goal"
    elif remaining_after >= 0:
        verdict = "ORANGE"
        label = "borderline for your saving goal"
    else:
        verdict = "RED"
        label = "hurting your saving goal this month"

    return verdict, label, remaining_after


def build_verdict_message(user: dict, tx: dict, verdict: str, label: str, remaining_after: float) -> str:
    """
    Create the text you will send on Telegram.
    """
    emoji_map = {"GREEN": "🟢", "ORANGE": "🟠", "RED": "🔴"}
    emoji = emoji_map.get(verdict, "⚪")

    month_goal = user["month_saving_goal"]
    text = (
        f"{emoji} You just spent ₹{tx['amount']} on {tx['merchant']}.\n"
        f"This month you want to save ₹{month_goal}.\n"
        f"Based on your current spending, this purchase is {label}.\n\n"
        f"Approx. non-essential budget left this month after this: ₹{max(remaining_after, 0):.0f}.\n"
        "If you want, we can adjust something else to keep you on track. 💸"
    )
    return text


@app.post("/set-goal")
def set_goal(body: SetGoalRequest):
    """
    Set the user's monthly saving goal and non-essential budget.
    This is the 'initially feed some goals' step.
    
    LEGACY ENDPOINT - Use Telegram bot for new implementations.
    """
    user = legacy_update_goal(
        user_id=body.user_id,
        saving_goal=body.month_saving_goal,
        nonessential_budget=body.month_nonessential_budget,
    )
    return {
        "message": "Goals updated",
        "user": user,
    }


@app.post("/add-transaction")
def add_tx(body: AddTransactionRequest, background_tasks: BackgroundTasks):
    """
    Simulate spending on a shopping app.
    This will:
      1) Record the transaction
      2) Calculate current month non-essential spend
      3) Evaluate if this purchase aligns with the saving goal
      4) Return a verdict + send a Telegram message
      
    LEGACY ENDPOINT - Use Telegram bot for new implementations.
    """
    user = legacy_get_user(body.user_id)
    if not user:
        return {"ok": False, "error": "User not found"}

    # 1) Save the transaction
    tx = legacy_add_transaction(
        user_id=body.user_id,
        amount=body.amount,
        merchant=body.merchant,
        category=body.category,
    )

    # 2) Calculate month non-essential spend *before* this new tx
    month_spend_total = calc_month_nonessential_spend(body.user_id)
    month_spend_before = month_spend_total - body.amount

    # 3) Evaluate this purchase
    verdict, label, remaining_after = evaluate_purchase(user, tx, month_spend_before)

    # 4) Build message text
    verdict_message = build_verdict_message(user, tx, verdict, label, remaining_after)

    # 5) Send Telegram message in the background
    background_tasks.add_task(send_telegram_text, verdict_message)

    return {
        "ok": True,
        "transaction": tx,
        "verdict": verdict,                      # "GREEN" / "ORANGE" / "RED"
        "verdict_label": label,                  # human-readable label
        "month_spend_nonessential_before": month_spend_before,
        "remaining_nonessential_budget_after": remaining_after,
        "notification_message": verdict_message,
        "notify_status": "telegram_send_triggered",
    }

