from pydantic import BaseModel


class SetGoalRequest(BaseModel):
    user_id: str = "u1"
    month_saving_goal: int           # e.g. 10000
    month_nonessential_budget: int   # e.g. 15000


class AddTransactionRequest(BaseModel):
    user_id: str = "u1"
    amount: float                    # e.g. 2499
    merchant: str                    # e.g. "Myntra"
    category: str = "shopping"       # default "shopping"
