from datetime import datetime
from typing import Dict, List

# ---- In-memory "database" ----

# One sample user for now
USERS: Dict[str, dict] = {
    "u1": {
        "id": "u1",
        "phone": "91XXXXXXXXXX",      # put your WhatsApp number here later (no +)
        "name": "Test User",
        "month_saving_goal": 10000,            # ₹ user wants to save this month
        "month_nonessential_budget": 15000,    # ₹ allowed for shopping etc.
    }
}

# Store all transactions in memory
TRANSACTIONS: List[dict] = []


def add_transaction(user_id: str, amount: float, merchant: str, category: str) -> dict:
    """Store a new transaction in memory."""
    tx = {
        "id": f"tx_{len(TRANSACTIONS) + 1}",
        "user_id": user_id,
        "amount": amount,
        "merchant": merchant,
        "category": category,
        "timestamp": datetime.utcnow(),
    }
    TRANSACTIONS.append(tx)
    return tx


def update_goal(user_id: str, saving_goal: int, nonessential_budget: int) -> dict:
    """Update the user's monthly saving goal and non-essential budget."""
    user = USERS.get(user_id)
    if not user:
        raise ValueError("User not found")
    user["month_saving_goal"] = saving_goal
    user["month_nonessential_budget"] = nonessential_budget
    return user


def get_user(user_id: str) -> dict:
    """Fetch user details."""
    return USERS.get(user_id)


def get_user_transactions(user_id: str) -> List[dict]:
    """Get all transactions for a given user."""
    return [tx for tx in TRANSACTIONS if tx["user_id"] == user_id]
