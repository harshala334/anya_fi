"""WhatsApp Business API integration."""

import httpx
from typing import Dict, Any, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """Client for WhatsApp Business Cloud API."""
    
    def __init__(self):
        """Initialize WhatsApp client."""
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        
        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp credentials not configured")
    
    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp.
        
        Args:
            to: Recipient phone number (with country code, no +)
            text: Message text
            
        Returns:
            API response dictionary
        """
        if not self.access_token or not self.phone_number_id:
            logger.error("WhatsApp not configured")
            return {"error": "WhatsApp not configured"}
        
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(f"WhatsApp message sent to {to}")
                return data
        except httpx.HTTPError as e:
            logger.error(f"WhatsApp API error: {e}")
            return {"error": str(e)}
    
    async def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: list[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Send an interactive message with buttons.
        
        Args:
            to: Recipient phone number
            body_text: Message body
            buttons: List of button dicts with 'id' and 'title'
                     Example: [{"id": "btn_1", "title": "Yes"}, {"id": "btn_2", "title": "No"}]
            
        Returns:
            API response dictionary
        """
        if not self.access_token or not self.phone_number_id:
            logger.error("WhatsApp not configured")
            return {"error": "WhatsApp not configured"}
        
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Format buttons for WhatsApp API
        formatted_buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"][:20]  # Max 20 chars
                }
            }
            for btn in buttons[:3]  # Max 3 buttons
        ]
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "action": {
                    "buttons": formatted_buttons
                }
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(f"WhatsApp interactive message sent to {to}")
                return data
        except httpx.HTTPError as e:
            logger.error(f"WhatsApp API error: {e}")
            return {"error": str(e)}
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark a message as read.
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            API response dictionary
        """
        if not self.access_token or not self.phone_number_id:
            return {"error": "WhatsApp not configured"}
        
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"WhatsApp API error: {e}")
            return {"error": str(e)}


# Global WhatsApp client instance
_whatsapp_client: Optional[WhatsAppClient] = None


def get_whatsapp_client() -> WhatsAppClient:
    """Get or create the global WhatsApp client instance."""
    global _whatsapp_client
    if _whatsapp_client is None:
        _whatsapp_client = WhatsAppClient()
    return _whatsapp_client
