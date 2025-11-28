"""Image Generation Service wrapper."""

from typing import Optional
from groq import Groq
from app.config import settings
import os

class ImageService:
    """
    Wrapper for Image Generation APIs.
    Uses Pollinations.ai (Free, No Key) for this MVP.
    """
    
    def __init__(self):
        pass
        
    def generate_image(self, prompt: str) -> str:
        """
        Generate an image from a prompt using Pollinations.ai.
        
        Args:
            prompt: Image description
            
        Returns:
            URL of the generated image
        """
        print(f"🎨 Generating image for: {prompt}")
        
        try:
            # Encode prompt for URL
            import urllib.parse
            import random
            
            encoded_prompt = urllib.parse.quote(prompt)
            seed = random.randint(1, 10000)
            
            # Construct Pollinations.ai URL
            # We use 'flux' model for better realism
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
            
            return image_url
            
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            # Reliable fallback
            return "https://images.unsplash.com/photo-1600596542815-2a4d9f0152ba?q=80&w=1000&auto=format&fit=crop"
