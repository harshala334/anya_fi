"""Agent for handling impulse buying interventions."""

from typing import Dict, Any, Optional
from groq import Groq
from sqlalchemy.orm import Session

from app.config import settings
from app.messaging.telegram_notifier import send_telegram_text
from app.agents.tools import AgentTools

class ImpulseAgent:
    """
    Agent that intervenes when a user visits a shopping site.
    """

    def __init__(self, db: Session):
        self.db = db
        if settings.groq_api_key:
            self.client = Groq(api_key=settings.groq_api_key)
        else:
            self.client = None
            print("⚠️  GROQ_API_KEY not configured - ImpulseAgent will use fallback responses")

    async def evaluate_and_intervene(self, user_id: str, url: str, merchant: str, product_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate the visit and decide whether to intervene.
        
        Args:
            user_id: Telegram User ID
            url: The URL visited
            merchant: Merchant name (e.g. Amazon)
            product_details: Optional details like price, name
            
        Returns:
            Result dictionary
        """
        print(f"🕵️ ImpulseAgent evaluating: User={user_id}, Merchant={merchant}")
        
        # 1. Get User Context (Goals, Budget)
        tools = AgentTools(self.db, user_id)
        active_goals = tools.get_active_goals()
        budget_status = tools.check_budget_status()
        
        # 2. Generate Nudge using LLM
        nudge = self._generate_nudge(merchant, product_details, active_goals, budget_status)
        
        # 3. Send Message via Telegram
        try:
            # We need to ensure the user exists in our DB and has a chat ID.
            # The tools init handles get_or_create_user, so we assume they are valid if they are using the extension.
            
            await send_telegram_text(text=nudge, chat_id=user_id)
            status = "sent"
        except Exception as e:
            print(f"❌ Failed to send Telegram intervention: {e}")
            status = "failed"
            
        return {
            "status": status,
            "nudge": nudge,
            "context_used": {
                "goals_count": len(active_goals),
                "budget_verdict": budget_status.get("verdict")
            }
        }

    def _generate_nudge(self, merchant: str, product: Optional[Dict], goals: list, budget: Dict) -> str:
        """Generate a persuasive nudge."""
        
        # Fallback if no LLM
        if not self.client:
            return f"👀 I see you're about to checkout on {merchant}. Remember your goals!"

        # Construct Prompt
        is_cart = product.get("is_cart", False) if product else False
        is_checkout = product.get("is_checkout", False) if product else False
        price = product.get("price", 0) if product else 0
        items = product.get("items", []) if product else []
        
        context_str = "User is looking at a product."
        if is_checkout:
            context_str = "URGENT: User is at the CHECKOUT page. They are about to pay."
        elif is_cart:
            context_str = "User is viewing their SHOPPING CART."
            
        price_str = f"The total cart value is ₹{price}." if price > 0 else "Total amount is unknown."
        
        items_str = ""
        if items:
            # Take top 3 items
            top_items = ", ".join(items[:3])
            if len(items) > 3:
                top_items += f" and {len(items)-3} more"
            items_str = f"The cart contains: {top_items}."
        
        goals_text = ""
        if goals:
            g = goals[0] # Focus on primary goal
            goals_text = f"They are saving for '{g['title']}' (Target: ₹{g['target_amount']})."
        else:
            goals_text = "They haven't set a specific saving goal yet, but want to save money."
            
        budget_text = ""
        if budget.get("verdict") != "NO_GOAL":
            budget_text = f"Their budget status is {budget['verdict']} ({budget['label']}). Remaining budget: ₹{budget['remaining']}."
        
        system_prompt = (
            "You are Anya, a financial best friend. "
            "The user is about to make a purchase online. "
            "Your job is to intervene at this critical moment. "
            "If they are at checkout, be more firm but still kind. "
            "Ask them to pause and think. "
            "Keep it short (under 50 words)."
        )
        
        user_prompt = (
            f"{context_str} on {merchant}. "
            f"{price_str} "
            f"{items_str} "
            f"{goals_text} "
            f"{budget_text} "
            "Write a short, punchy message to send to them right now."
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return f"👀 I see you're on {merchant}. Just a gentle reminder to stay on track with your goals! ✨"
