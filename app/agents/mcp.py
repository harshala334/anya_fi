"""MCP (Model-Context-Protocol) Agent - Observe → Reason → Act."""

from typing import Dict, Any, Optional, List
from groq import Groq
from sqlalchemy.orm import Session

from app.config import settings
from app.agents.prompts import (
    FINANCIAL_ADVISOR_SYSTEM_PROMPT,
    GOAL_SETTING_PROMPT,
    SPENDING_ANALYSIS_PROMPT,
    BEHAVIORAL_NUDGE_PROMPT
)
from app.agents.tools import AgentTools
from app.messaging.session_manager import session_manager


class MCPAgent:
    """
    MCP Agent orchestrates the Observe → Reason → Act cycle.
    
    - Observe: Gather context (user message, goals, spending, history)
    - Reason: Use LLM to understand intent and plan response
    - Act: Execute tools and generate response
    """
    
    def __init__(self, db: Session, user_id: str):
        """
        Initialize MCP agent.
        
        Args:
            db: Database session
            user_id: Telegram user ID
        """
        self.db = db
        self.user_id = user_id
        self.tools = AgentTools(db, user_id)
        
        # Initialize Groq client
        if settings.groq_api_key:
            self.client = Groq(api_key=settings.groq_api_key)
        else:
            self.client = None
            print("⚠️  GROQ_API_KEY not configured - agent will use fallback responses")
    
    def observe(self, user_message: str) -> Dict[str, Any]:
        """
        Observe: Gather all relevant context.
        
        Args:
            user_message: User's message
            
        Returns:
            Context dictionary
        """
        # Get conversation history
        history = session_manager.get_history(self.user_id, limit=5)
        
        # Get active goals
        goals = self.tools.get_active_goals()
        
        # Get spending status
        budget_status = self.tools.check_budget_status()
        
        # Get conversation state
        state = session_manager.get_conversation_state(self.user_id)
        
        return {
            "user_message": user_message,
            "history": history,
            "goals": goals,
            "budget_status": budget_status,
            "conversation_state": state
        }
    
    def reason(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason: Use LLM to understand intent and plan response.
        
        Args:
            context: Observed context
            
        Returns:
            Reasoning result with intent and planned actions
        """
        if not self.client:
            return self._fallback_reasoning(context)
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": FINANCIAL_ADVISOR_SYSTEM_PROMPT}
        ]
        
        # Add conversation history
        for msg in context["history"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current context as system message
        context_str = self._format_context(context)
        messages.append({
            "role": "system",
            "content": f"Current context:\n{context_str}"
        })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": context["user_message"]
        })
        
        try:
            # Call Groq LLM
            response = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Detect intent from response
            intent = self._detect_intent(context["user_message"], assistant_message)
            
            return {
                "intent": intent,
                "response": assistant_message,
                "actions": []  # Actions will be determined based on intent
            }
        
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return self._fallback_reasoning(context)
    
    def act(self, reasoning: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Act: Execute actions and return final response.
        
        Args:
            reasoning: Reasoning result
            context: Observed context
            
        Returns:
            Final response message
        """
        intent = reasoning["intent"]
        response = reasoning["response"]
        user_message = context["user_message"]
        
        # Execute intent-specific actions
        if intent == "set_goal":
            # Try to extract goal parameters from the conversation
            goal_params = self._extract_goal_params(user_message, response, context)
            print(f"🔍 DEBUG: Extracted goal params: {goal_params}")
            
            if goal_params and goal_params.get("title") and goal_params.get("target_amount"):
                try:
                    print(f"💾 Creating goal: {goal_params}")
                    # Create the goal
                    goal_result = self.tools.set_saving_goal(
                        title=goal_params["title"],
                        target_amount=goal_params["target_amount"],
                        deadline_days=goal_params.get("deadline_days"),
                        month_nonessential_budget=goal_params.get("month_nonessential_budget")
                    )
                    print(f"✅ Goal created: {goal_result}")
                    # Update response to confirm goal creation
                    if "goal_id" in goal_result:
                        response += f"\n\n✅ Goal saved! I'll help you track your progress toward {goal_params['title']}."
                except Exception as e:
                    print(f"❌ Error creating goal: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"⚠️  Goal params incomplete - title: {goal_params.get('title') if goal_params else None}, amount: {goal_params.get('target_amount') if goal_params else None}")
        
        elif intent == "update_progress":
            # Extract amount from message
            progress_amount = self._extract_progress_amount(user_message)
            if progress_amount:
                try:
                    print(f"💰 Updating goal progress: {progress_amount}")
                    result = self.tools.update_goal_progress(amount=progress_amount)
                    if "error" not in result:
                        print(f"✅ Goal updated: {result}")
                        response += f"\n\n✅ Updated! You now have ₹{result['current_amount']:,.0f} saved ({result['progress_percentage']:.0f}% of your goal)."
                except Exception as e:
                    print(f"❌ Error updating progress: {e}")
        
        elif intent == "update_budget":
            # Extract budget amount from message
            budget_amount = self._extract_budget_amount(user_message)
            if budget_amount:
                try:
                    print(f"💵 Updating budget: {budget_amount}")
                    result = self.tools.update_budget(budget_amount)
                    if "error" not in result:
                        print(f"✅ Budget updated: {result}")
                        response += f"\n\n✅ Budget updated! Your monthly non-essential budget is now ₹{budget_amount:,.0f}."
                except Exception as e:
                    print(f"❌ Error updating budget: {e}")
        
        elif intent == "delete_goals":
            # Delete goals
            try:
                print(f"🗑️  Deleting goals...")
                result = self.tools.delete_goals()
                if "error" not in result:
                    print(f"✅ Deleted: {result}")
                    response += f"\n\n✅ Deleted {result['deleted']} goal(s). You can start fresh with new goals!"
            except Exception as e:
                print(f"❌ Error deleting goals: {e}")
        
        elif intent == "check_status":
            # Status is already checked in observe(), just use it
            pass
        
        elif intent == "add_transaction":
            # Extract transaction details and add it
            transaction_data = self._extract_transaction_data(user_message)
            if transaction_data:
                try:
                    print(f"💳 Adding transaction: {transaction_data}")
                    result = self.tools.add_transaction(
                        amount=transaction_data['amount'],
                        merchant=transaction_data.get('merchant', 'Unknown'),
                        category=transaction_data.get('category', 'other')
                    )
                    print(f"✅ Transaction added: {result}")
                    response += f"\n\n✅ Recorded! Spent ₹{transaction_data['amount']:,.0f} at {transaction_data.get('merchant', 'Unknown')}."
                except Exception as e:
                    print(f"❌ Error adding transaction: {e}")
        
        elif intent == "analyze_spending":
            # Spending is already analyzed in observe(), just use it
            pass
        
        # Store conversation in history
        session_manager.add_to_history(self.user_id, "user", context["user_message"])
        session_manager.add_to_history(self.user_id, "assistant", response)
        
        return response
    
    def process_message(self, user_message: str) -> str:
        """
        Main entry point: Process a user message through the MCP cycle.
        
        Args:
            user_message: User's message
            
        Returns:
            Agent's response
        """
        # Observe
        context = self.observe(user_message)
        
        # Reason
        reasoning = self.reason(context)
        
        # Act
        response = self.act(reasoning, context)
        
        return response
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for LLM."""
        parts = []
        
        # Goals
        if context["goals"]:
            goals_str = "\n".join([
                f"- {g['title']}: ₹{g['current_amount']:.0f} / ₹{g['target_amount']:.0f} ({g['progress_percentage']:.0f}%)"
                for g in context["goals"]
            ])
            parts.append(f"Active Goals:\n{goals_str}")
        else:
            parts.append("No active goals set.")
        
        # Budget status
        budget = context["budget_status"]
        if budget["verdict"] != "NO_GOAL":
            parts.append(
                f"\nBudget Status: {budget['verdict']} ({budget['label']})\n"
                f"Spent: ₹{budget['total_spent']:.0f} / ₹{budget['budget']:.0f}\n"
                f"Remaining: ₹{budget['remaining']:.0f}"
            )
        
        return "\n\n".join(parts)
    
    def _detect_intent(self, user_message: str, assistant_response: str) -> str:
        """Detect user intent from message and response."""
        user_lower = user_message.lower()
        
        # Simple keyword-based intent detection
        if any(word in user_lower for word in ["delete goal", "remove goal", "delete my goal", "clear goal"]):
            return "delete_goals"
        elif any(word in user_lower for word in ["budget is", "monthly budget", "set budget", "month budget", "my budget", "budget of"]):
            return "update_budget"
        elif any(word in user_lower for word in ["i spent", "spent", "paid", "bought", "purchase", "cost"]):
            return "add_transaction"
        elif any(word in user_lower for word in ["i saved", "i have", "already have", "update my goal", "update goal", "update progress"]):
            return "update_progress"
        elif any(word in user_lower for word in ["goal", "save", "want to buy", "planning"]):
            return "set_goal"
        elif any(word in user_lower for word in ["status", "how am i", "progress", "doing"]):
            return "check_status"
        elif any(word in user_lower for word in ["spent", "spending", "transactions"]):
            return "analyze_spending"
        else:
            return "general_chat"
    
    def _fallback_reasoning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback reasoning when Groq is not available."""
        user_message = context["user_message"].lower()
        
        # Simple rule-based responses
        if "goal" in user_message or "save" in user_message:
            response = "I'd love to help you set a goal! What are you saving for? 🎯"
            intent = "set_goal"
        
        elif "status" in user_message or "progress" in user_message:
            budget = context["budget_status"]
            if budget["verdict"] != "NO_GOAL":
                response = (
                    f"You've spent ₹{budget['total_spent']:.0f} out of ₹{budget['budget']:.0f} "
                    f"this month. You have ₹{budget['remaining']:.0f} left! 💰"
                )
            else:
                response = "You haven't set a goal yet. Want to create one? 🎯"
            intent = "check_status"
        
        else:
            response = "I'm here to help you with your financial goals! You can ask me about your spending, set goals, or check your progress. 😊"
            intent = "general_chat"
        
        return {
            "intent": intent,
            "response": response,
            "actions": []
        }
    
    def _extract_goal_params(self, user_message: str, assistant_response: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract goal parameters from user message and conversation context.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            context: Conversation context
            
        Returns:
            Dictionary with goal parameters or None
        """
        import re
        
        params = {}
        user_lower = user_message.lower()
        
        # Extract title - look for common patterns
        title_patterns = [
            r"(?:save|saving|buy|purchase|get)\s+(?:a|an|for|)\s*([a-zA-Z0-9\s]+?)(?:\s+for|\s+in|\s+by|$)",
            r"(?:want to|planning to)\s+(?:buy|get|purchase)\s+(?:a|an|)\s*([a-zA-Z0-9\s]+?)(?:\s+for|\s+in|\s+by|$)",
            r"for\s+(?:a|an|)\s*([a-zA-Z0-9\s]+?)(?:\s+for|\s+in|\s+by|$)"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, user_lower)
            if match:
                title = match.group(1).strip()
                # Clean up common words
                title = re.sub(r'\b(for|in|by|the|a|an)\b', '', title).strip()
                if title and len(title) > 2:
                    params["title"] = title.title()
                    break
        
        # Extract amount - look for numbers with optional currency symbols
        amount_patterns = [
            r'₹\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'rupees?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'(?:^|\s)([0-9,]+(?:\.[0-9]{2})?)\s*(?:rupees?|rs|₹|inr)',
            r'(?:cost|price|worth|amount|target)(?:\s+is|\s+of)?\s*₹?\s*([0-9,]+(?:\.[0-9]{2})?)',
            # Handle bare numbers in context of saving/buying
            r'(?:save|saving|buy|purchase|get|need)\s+(?:₹|rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)',
            # Handle "50000 for a laptop" pattern
            r'\b([0-9]{4,}(?:\.[0-9]{2})?)\s+(?:for|to)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, user_lower, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    # Only accept reasonable amounts (100 to 100 million)
                    if 100 <= amount <= 100000000:
                        params["target_amount"] = amount
                        break
                except ValueError:
                    continue
        
        # Extract deadline - look for time expressions
        deadline_patterns = [
            (r'in\s+(\d+)\s+months?', lambda x: int(x) * 30),
            (r'in\s+(\d+)\s+weeks?', lambda x: int(x) * 7),
            (r'in\s+(\d+)\s+days?', lambda x: int(x)),
            (r'(\d+)\s+months?', lambda x: int(x) * 30),
            (r'(\d+)\s+weeks?', lambda x: int(x) * 7),
        ]
        
        for pattern, converter in deadline_patterns:
            match = re.search(pattern, user_lower)
            if match:
                try:
                    params["deadline_days"] = converter(match.group(1))
                    break
                except (ValueError, IndexError):
                    continue
        
        # Extract budget - look for monthly budget mentions
        budget_patterns = [
            r'budget\s+(?:of|is)?\s*₹?\s*([0-9,]+)',
            r'spend\s+₹?\s*([0-9,]+)\s+(?:per|a|each)\s+month',
            r'monthly\s+budget\s+₹?\s*([0-9,]+)',
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, user_lower)
            if match:
                budget_str = match.group(1).replace(',', '')
                try:
                    params["month_nonessential_budget"] = float(budget_str)
                    break
                except ValueError:
                    continue
        
        # If we have at least a title or amount, return params
        if params.get("title") or params.get("target_amount"):
            return params
        
        return None
    
    def _extract_progress_amount(self, user_message: str) -> Optional[float]:
        """
        Extract savings amount from progress update messages.
        
        Args:
            user_message: User's message
            
        Returns:
            Amount or None
        """
        import re
        
        user_lower = user_message.lower()
        
        # Patterns to extract amount
        patterns = [
            r'(?:i\s+)?(?:already\s+)?(?:have|saved|got)\s+(?:₹|rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'(?:₹|rs\.?)\s*([0-9,]+(?:\.[0-9]{2})?)\s+(?:saved|already)',
            r'\b([0-9,]+(?:\.[0-9]{2})?)\s+(?:rupees?|rs|₹)',
            r'update.*?(?:₹|rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_lower, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    if 0 <= amount <= 100000000:  # Reasonable range
                        return amount
                except ValueError:
                    continue
        
        return None
    
    def _extract_budget_amount(self, user_message: str) -> Optional[float]:
        """
        Extract budget amount from budget update messages.
        
        Args:
            user_message: User's message
            
        Returns:
            Budget amount or None
        """
        import re
        
        user_lower = user_message.lower()
        
        # Patterns to extract budget amount
        patterns = [
            r'budget\s+is\s+(?:₹|rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'monthly\s+budget\s+(?:is\s+)?(?:₹|rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'set\s+budget\s+(?:to\s+)?(?:₹|rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'month\s+budget\s+(?:is\s+)?(?:₹|rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_lower, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    if 0 <= amount <= 100000000:  # Reasonable range
                        return amount
                except ValueError:
                    continue
        
        return None
    def _extract_transaction_data(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        Extract transaction details from message.
        
        Args:
            user_message: User's message
            
        Returns:
            Dictionary with amount, merchant, category
        """
        import re
        
        user_lower = user_message.lower()
        data = {}
        
        # Extract amount
        amount_patterns = [
            r'(?:spent|paid|cost|bought.*?for)\s+(?:₹|rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'(?:₹|rs\.?)\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'\b([0-9,]+(?:\.[0-9]{2})?)\s+(?:rupees?|rs|₹)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, user_lower, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    if 0 < amount <= 100000000:
                        data['amount'] = amount
                        break
                except ValueError:
                    continue
        
        if 'amount' not in data:
            return None
            
        # Extract merchant/description
        # Look for "at [merchant]" or "for [item]"
        merchant_match = re.search(r'(?:at|from|to)\s+([a-zA-Z0-9\s\']+?)(?:\s+for|\s+on|\s*$)', user_lower)
        if merchant_match:
            data['merchant'] = merchant_match.group(1).strip().title()
        else:
            # Fallback: try to find what was bought
            item_match = re.search(r'(?:bought|purchase|for)\s+([a-zA-Z0-9\s\']+?)(?:\s+for|\s+at|\s+cost|\s*$)', user_lower)
            if item_match:
                data['merchant'] = item_match.group(1).strip().title()
            else:
                data['merchant'] = "Unknown Merchant"
        
        # Determine category based on keywords
        merchant_lower = data['merchant'].lower()
        message_lower = user_lower
        
        if any(w in message_lower or w in merchant_lower for w in ['food', 'restaurant', 'cafe', 'dinner', 'lunch', 'breakfast', 'burger', 'pizza', 'coffee']):
            data['category'] = 'food'
        elif any(w in message_lower or w in merchant_lower for w in ['uber', 'ola', 'taxi', 'bus', 'train', 'flight', 'fuel', 'petrol']):
            data['category'] = 'transport'
        elif any(w in message_lower or w in merchant_lower for w in ['grocery', 'vegetables', 'fruits', 'milk', 'supermarket']):
            data['category'] = 'groceries'
        elif any(w in message_lower or w in merchant_lower for w in ['movie', 'netflix', 'game', 'concert', 'party']):
            data['category'] = 'entertainment'
        elif any(w in message_lower or w in merchant_lower for w in ['bill', 'electricity', 'water', 'rent', 'internet', 'wifi']):
            data['category'] = 'bills'
        elif any(w in message_lower or w in merchant_lower for w in ['clothes', 'shoes', 'dress', 'shopping', 'amazon', 'flipkart']):
            data['category'] = 'shopping'
        else:
            data['category'] = 'other'
            
        return data
