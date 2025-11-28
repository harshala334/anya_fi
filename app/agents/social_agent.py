"""Agent for social spending optimization."""

from typing import Dict, Any
from app.services.places_service import PlacesService
from groq import Groq
from app.config import settings

class SocialAgent:
    """
    Agent that helps users navigate social spending pressure.
    """
    
    def __init__(self):
        self.places_service = PlacesService()
        self.groq_client = Groq(api_key=settings.groq_api_key)

    async def suggest_social_hack(self, activity: str, location: str) -> Dict[str, Any]:
        """
        Suggest a cheaper alternative and a social script.
        """
        # 1. Find Alternative
        place = self.places_service.get_alternative(activity, location)
        
        # 2. Generate Social Script using LLM
        prompt = (
            f"You are a socially intelligent financial assistant. "
            f"The user wants to go for '{activity}' in '{location}' but needs to save money. "
            f"Suggest they go to '{place['name']}' in '{place['area']}' instead. "
            f"It has a vibe of: '{place['vibe']}'. "
            f"Write a short, persuasive, casual WhatsApp message (max 2 sentences) they can send to their friends "
            f"to convince them to switch plans, without sounding broke. Make it sound like a 'better plan'."
        )
        
        try:
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a witty, helpful social assistant."},
                    {"role": "user", "content": prompt}
                ],
                model=settings.groq_model,
                temperature=0.7,
                max_tokens=100,
            )
            script = completion.choices[0].message.content.strip().replace('"', '')
        except Exception as e:
            print(f"LLM Error: {e}")
            script = f"Guys, how about {place['name']} instead? Heard the vibe is {place['vibe']}!"

        return {
            "place": place,
            "script": script,
            "message": (
                f"💡 **Social Currency Hack**\n\n"
                f"Instead of blowing cash, why not try **{place['name']}**?\n"
                f"📍 {place['area']} | ✨ {place['vibe']}\n\n"
                f"**Copy-Paste to Friends:**\n"
                f"`{script}`"
            )
        }
