"""WhatsApp bot with MCP agent integration."""

import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
import hmac
import hashlib

from app.config import settings
from app.db.database import get_db_context
from app.agents.mcp import MCPAgent
from app.messaging.whatsapp_client import get_whatsapp_client
from app.messaging.session_manager import session_manager

logger = logging.getLogger(__name__)


class WhatsAppBot:
    """WhatsApp bot with conversational interface."""
    
    def __init__(self):
        """Initialize WhatsApp bot."""
        self.client = get_whatsapp_client()
        self.verify_token = settings.whatsapp_verify_token
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook subscription.
        
        Args:
            mode: Verification mode
            token: Verification token
            challenge: Challenge string
            
        Returns:
            Challenge string if verified, None otherwise
        """
        if mode == "subscribe" and token == self.verify_token:
            logger.info("✅ WhatsApp webhook verified")
            return challenge
        else:
            logger.warning("⚠️  WhatsApp webhook verification failed")
            return None
    
    async def handle_webhook(self, body: Dict[str, Any]) -> Dict[str, str]:
        """
        Handle incoming WhatsApp webhook.
        
        Args:
            body: Webhook payload
            
        Returns:
            Response dictionary
        """
        try:
            # Extract message data
            entry = body.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            
            # Check if it's a message
            messages = value.get("messages")
            if not messages:
                return {"status": "no_messages"}
            
            message = messages[0]
            from_number = message.get("from")
            message_type = message.get("type")
            message_id = message.get("id")
            
            # Mark as read
            await self.client.mark_as_read(message_id)
            
            # Handle different message types
            if message_type == "text":
                text = message.get("text", {}).get("body", "")
                await self._handle_text_message(from_number, text)
            
            elif message_type == "interactive":
                # Handle button responses
                button_reply = message.get("interactive", {}).get("button_reply", {})
                button_id = button_reply.get("id")
                await self._handle_button_response(from_number, button_id)
            
            else:
                # Unsupported message type
                await self.client.send_text_message(
                    from_number,
                    "Sorry, I can only process text messages right now. 📝"
                )
            
            return {"status": "ok"}
        
        except Exception as e:
            logger.error(f"Error handling WhatsApp webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_text_message(self, from_number: str, text: str):
        """
        Handle text message using MCP agent.
        
        Args:
            from_number: Sender's phone number
            text: Message text
        """
        logger.info(f"WhatsApp message from {from_number}: {text}")
        
        # Check for commands
        if text.startswith("/"):
            await self._handle_command(from_number, text)
            return
        
        # Process through MCP agent
        with get_db_context() as db:
            # Use phone number as user_id for WhatsApp
            user_id = f"wa_{from_number}"
            agent = MCPAgent(db, user_id)
            response = agent.process_message(text)
        
        logger.info(f"Bot response: {response}")
        
        # Send response
        await self.client.send_text_message(from_number, response)
    
    async def _handle_command(self, from_number: str, command: str):
        """
        Handle command messages.
        
        Args:
            from_number: Sender's phone number
            command: Command string
        """
        cmd = command.lower().strip()
        
        if cmd == "/start":
            response = (
                "Hey! 👋 I'm Anya, your financial co-pilot.\n\n"
                "I'm here to help you:\n"
                "💰 Set and track savings goals\n"
                "📊 Monitor your spending\n"
                "🎯 Make smarter financial decisions\n\n"
                "Just chat with me naturally! You can say things like:\n"
                "• \"I want to save for a laptop\"\n"
                "• \"How am I doing this month?\"\n"
                "• \"Show me my spending\"\n\n"
                "Let's start - what are you saving for? 🎯"
            )
        
        elif cmd == "/help":
            response = (
                "🤖 *Anya Commands*\n\n"
                "/start - Get started\n"
                "/help - Show this help\n"
                "/stats - Check your budget status\n"
                "/goals - View your active goals\n\n"
                "💬 *Or just chat with me!*\n"
                "I understand natural language, so feel free to ask questions or share your goals."
            )
        
        elif cmd == "/stats":
            await self._send_stats(from_number)
            return
        
        elif cmd == "/goals":
            await self._send_goals(from_number)
            return
        
        else:
            response = "Unknown command. Try /help to see available commands."
        
        await self.client.send_text_message(from_number, response)
    
    async def _send_stats(self, from_number: str):
        """Send budget statistics."""
        with get_db_context() as db:
            user_id = f"wa_{from_number}"
            agent = MCPAgent(db, user_id)
            budget_status = agent.tools.check_budget_status()
            
            # Get active goals for progress info
            goals = agent.tools.get_active_goals()
            
            if budget_status["verdict"] == "NO_GOAL":
                response = (
                    "You haven't set a goal yet! 🎯\n\n"
                    "Tell me what you're saving for and I'll help you track it."
                )
            else:
                verdict_emoji = {
                    "GREEN": "🟢",
                    "ORANGE": "🟠",
                    "RED": "🔴"
                }
                emoji = verdict_emoji.get(budget_status["verdict"], "⚪")
                
                # Build response with goal progress
                response = f"{emoji} *Budget Status*\n\n"
                
                # Add goal progress if available
                if goals:
                    goal = goals[0]  # Show first active goal
                    progress_bar = self._create_progress_bar(goal['progress_percentage'])
                    response += (
                        f"*Goal Progress:*\n"
                        f"{goal['title']}\n"
                        f"{progress_bar} {goal['progress_percentage']:.0f}%\n"
                        f"₹{goal['current_amount']:,.0f} / ₹{goal['target_amount']:,.0f}\n\n"
                    )
                
                response += (
                    f"*This Month:*\n"
                    f"Spent: ₹{budget_status['total_spent']:,.0f}\n"
                    f"Budget: ₹{budget_status['budget']:,.0f}\n"
                    f"Remaining: ₹{budget_status['remaining']:,.0f}\n\n"
                    f"Status: {budget_status['label'].title()}"
                )
        
        await self.client.send_text_message(from_number, response)
    
    async def _send_goals(self, from_number: str):
        """Send active goals."""
        with get_db_context() as db:
            user_id = f"wa_{from_number}"
            agent = MCPAgent(db, user_id)
            goals = agent.tools.get_active_goals()
            
            if not goals:
                response = (
                    "You don't have any active goals yet! 🎯\n\n"
                    "Let's set one - what are you saving for?"
                )
            else:
                response = "🎯 *Your Active Goals*\n\n"
                for goal in goals:
                    progress = goal['progress_percentage']
                    progress_bar = self._create_progress_bar(progress)
                    
                    response += (
                        f"*{goal['title']}*\n"
                        f"{progress_bar} {progress:.0f}%\n"
                        f"₹{goal['current_amount']:,.0f} / ₹{goal['target_amount']:,.0f}\n"
                    )
                    
                    if goal['deadline']:
                        response += f"Deadline: {goal['deadline'][:10]}\n"
                    
                    response += "\n"
        
        await self.client.send_text_message(from_number, response)
    
    async def _handle_button_response(self, from_number: str, button_id: str):
        """
        Handle interactive button responses.
        
        Args:
            from_number: Sender's phone number
            button_id: Button ID that was clicked
        """
        # Process button response through agent
        # For now, treat it as a text message
        await self._handle_text_message(from_number, f"Button: {button_id}")
    
    def _create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create a visual progress bar."""
        filled = int((percentage / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar


# Global bot instance
_whatsapp_bot: Optional[WhatsAppBot] = None


def get_whatsapp_bot() -> WhatsAppBot:
    """Get or create the global WhatsApp bot instance."""
    global _whatsapp_bot
    if _whatsapp_bot is None:
        _whatsapp_bot = WhatsAppBot()
    return _whatsapp_bot
