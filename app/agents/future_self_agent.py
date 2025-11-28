"""Agent for visualizing future goals."""

from typing import Dict, Any, Optional
from app.services.real_estate_service import RealEstateService
from app.services.image_service import ImageService
from app.config import settings

class FutureSelfAgent:
    """
    Agent that helps users visualize their future goals.
    """
    
    def __init__(self):
        self.re_service = RealEstateService()
        self.image_service = ImageService()

    async def visualize_dream_home(self, location: str, property_type: str) -> Dict[str, Any]:
        """
        Generate a visualization and details for a dream home.
        
        Args:
            location: City/Area
            property_type: Type (e.g. 2BHK)
            
        Returns:
            Dictionary with text details and image URL.
        """
        # 1. Fetch Market Data
        details = self.re_service.get_property_details(location, property_type)
        
        # 2. Construct Image Prompt
        prompt = (
            f"A photorealistic image of a modern {details['type']} apartment in {details['city']}, India. "
            f"The apartment is spacious, with a balcony overlooking the city skyline. "
            f"Warm lighting, cozy interior, plants, and a view of {details['area']}. "
            "High quality, architectural photography style."
        )
        
        # 3. Generate Image
        image_url = self.image_service.generate_image(prompt)
        
        return {
            "details": details,
            "image_url": image_url,
            "message": (
                f"🏡 **Future Home Visualization**\n\n"
                f"📍 **Location**: {details['area']}, {details['city']}\n"
                f"🏠 **Type**: {details['type']}\n"
                f"💰 **Estimated Price**: {details['price_formatted']}\n\n"
                f"✨ *{details['description']}*\n\n"
                "Keep saving! You're building towards this."
            )
        }
