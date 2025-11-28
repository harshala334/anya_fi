"""Redis-based session management for conversation context."""

import json
import redis
from typing import Optional, Dict, Any
from datetime import datetime

from app.config import settings


class SessionManager:
    """Manage conversation sessions using Redis."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            print("✅ Connected to Redis")
        except redis.ConnectionError:
            print("⚠️  Redis not available, using in-memory fallback")
            self.redis_client = None
            self._memory_store: Dict[str, Any] = {}
    
    def _get_key(self, user_id: str) -> str:
        """Generate Redis key for user session."""
        return f"session:{user_id}"
    
    def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Session data dictionary or None if not found
        """
        key = self._get_key(user_id)
        
        if self.redis_client:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        else:
            # Fallback to in-memory
            return self._memory_store.get(key)
        
        return None
    
    def set_session(
        self, 
        user_id: str, 
        context: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """
        Store session data for a user.
        
        Args:
            user_id: Telegram user ID
            context: Session context data
            ttl: Time to live in seconds (default from settings)
        """
        key = self._get_key(user_id)
        ttl = ttl or settings.redis_session_ttl
        
        # Add timestamp
        context['last_activity'] = datetime.utcnow().isoformat()
        
        if self.redis_client:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(context)
            )
        else:
            # Fallback to in-memory
            self._memory_store[key] = context
    
    def update_session(
        self, 
        user_id: str, 
        updates: Dict[str, Any]
    ) -> None:
        """
        Update specific fields in a session.
        
        Args:
            user_id: Telegram user ID
            updates: Dictionary of fields to update
        """
        session = self.get_session(user_id) or {}
        session.update(updates)
        self.set_session(user_id, session)
    
    def delete_session(self, user_id: str) -> None:
        """
        Delete a user's session.
        
        Args:
            user_id: Telegram user ID
        """
        key = self._get_key(user_id)
        
        if self.redis_client:
            self.redis_client.delete(key)
        else:
            self._memory_store.pop(key, None)
    
    def get_conversation_state(self, user_id: str) -> Optional[str]:
        """
        Get the current conversation state for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Current state string or None
        """
        session = self.get_session(user_id)
        return session.get('state') if session else None
    
    def set_conversation_state(self, user_id: str, state: str) -> None:
        """
        Set the conversation state for a user.
        
        Args:
            user_id: Telegram user ID
            state: State identifier (e.g., 'awaiting_goal_amount')
        """
        self.update_session(user_id, {'state': state})
    
    def add_to_history(
        self, 
        user_id: str, 
        role: str, 
        message: str
    ) -> None:
        """
        Add a message to conversation history.
        
        Args:
            user_id: Telegram user ID
            role: 'user' or 'assistant'
            message: Message content
        """
        session = self.get_session(user_id) or {}
        history = session.get('history', [])
        
        history.append({
            'role': role,
            'content': message,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Keep only last 20 messages to avoid memory bloat
        if len(history) > 20:
            history = history[-20:]
        
        session['history'] = history
        self.set_session(user_id, session)
    
    def get_history(self, user_id: str, limit: int = 10) -> list:
        """
        Get conversation history for a user.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        session = self.get_session(user_id)
        if not session:
            return []
        
        history = session.get('history', [])
        return history[-limit:] if history else []


# Global session manager instance
session_manager = SessionManager()
