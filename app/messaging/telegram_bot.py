"""Telegram bot with conversational interface."""

import logging
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from app.config import settings
from app.db.database import get_db_context
from app.agents.mcp import MCPAgent

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot with MCP agent integration."""
    
    def __init__(self):
        """Initialize the bot."""
        if not settings.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured")
        
        self.application = Application.builder().token(settings.telegram_bot_token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("mystats", self.stats_command))
        self.application.add_handler(CommandHandler("goals", self.goals_command))
        
        # Message handler for all text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        welcome_message = (
            f"Hey {user.first_name}! 👋 I'm Anya, your financial co-pilot.\n\n"
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
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = (
            "🤖 **Anya Commands**\n\n"
            "/start - Get started\n"
            "/help - Show this help\n"
            "/mystats - Check your budget status\n"
            "/goals - View your active goals\n\n"
            "💬 **Or just chat with me!**\n"
            "I understand natural language, so feel free to ask questions or share your goals.\n\n"
            "Examples:\n"
            "• \"I want to buy a MacBook for ₹1,20,000\"\n"
            "• \"How much have I spent this month?\"\n"
            "• \"Am I on track for my goal?\""
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mystats command."""
        user_id = str(update.effective_user.id)
        
        with get_db_context() as db:
            agent = MCPAgent(db, user_id)
            
            # Get budget status
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
                response = f"{emoji} **Budget Status**\n\n"
                
                # Add goal progress if available
                if goals:
                    goal = goals[0]  # Show first active goal
                    progress_bar = self._create_progress_bar(goal['progress_percentage'])
                    response += (
                        f"**Goal Progress:**\n"
                        f"{goal['title']}\n"
                        f"{progress_bar} {goal['progress_percentage']:.0f}%\n"
                        f"₹{goal['current_amount']:,.0f} / ₹{goal['target_amount']:,.0f}\n\n"
                    )
                
                response += (
                    f"**This Month:**\n"
                    f"Spent: ₹{budget_status['total_spent']:,.0f}\n"
                    f"Budget: ₹{budget_status['budget']:,.0f}\n"
                    f"Remaining: ₹{budget_status['remaining']:,.0f}\n\n"
                    f"Status: {budget_status['label'].title()}"
                )
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def goals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /goals command."""
        user_id = str(update.effective_user.id)
        
        with get_db_context() as db:
            agent = MCPAgent(db, user_id)
            goals = agent.tools.get_active_goals()
            
            if not goals:
                response = (
                    "You don't have any active goals yet! 🎯\n\n"
                    "Let's set one - what are you saving for?"
                )
            else:
                response = "🎯 **Your Active Goals**\n\n"
                for goal in goals:
                    progress = goal['progress_percentage']
                    progress_bar = self._create_progress_bar(progress)
                    
                    response += (
                        f"**{goal['title']}**\n"
                        f"{progress_bar} {progress:.0f}%\n"
                        f"₹{goal['current_amount']:,.0f} / ₹{goal['target_amount']:,.0f}\n"
                    )
                    
                    if goal['deadline']:
                        response += f"Deadline: {goal['deadline'][:10]}\n"
                    
                    response += "\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        
        logger.info(f"User {user_id}: {user_message}")
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        # Process message through MCP agent
        with get_db_context() as db:
            agent = MCPAgent(db, user_id)
            response = agent.process_message(user_message)
        
        logger.info(f"Bot: {response}")
        
        # Send response
        await update.message.reply_text(response)
    
    def _create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create a visual progress bar."""
        filled = int((percentage / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar
    
    def run_polling(self):
        """Run the bot in polling mode (for development)."""
        logger.info("🤖 Starting Telegram bot in polling mode...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def set_webhook(self, webhook_url: str):
        """Set webhook for production deployment."""
        await self.application.bot.set_webhook(
            url=webhook_url,
            secret_token=settings.telegram_webhook_secret
        )
        logger.info(f"✅ Webhook set to: {webhook_url}")
    
    def get_webhook_handler(self):
        """Get webhook handler for FastAPI integration."""
        return self.application


# Global bot instance
_bot_instance: Optional[TelegramBot] = None


def get_bot() -> TelegramBot:
    """Get or create the global bot instance."""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TelegramBot()
    return _bot_instance
