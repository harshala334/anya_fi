"""Mock service for finding budget-friendly social alternatives."""

from typing import Dict, List, Any
import random

class PlacesService:
    """
    Mock service to find social alternatives.
    """
    
    def __init__(self):
        # Mock database of "Cool but Cheap" places
        self.alternatives = {
            "bangalore": {
                "drinks": [
                    {"name": "Chin Lung", "area": "Residency Road", "vibe": "Old school, cheap beer", "savings": "High"},
                    {"name": "Sathya's", "area": "Koramangala", "vibe": "Local legend, great food", "savings": "High"},
                    {"name": "Pecos", "area": "Indiranagar", "vibe": "Classic rock, popcorn", "savings": "Medium"},
                ],
                "dinner": [
                    {"name": "Nagarjuna", "area": "Indiranagar", "vibe": "Spicy Andhra meals", "savings": "Medium"},
                    {"name": "Truffles", "area": "Koramangala", "vibe": "Burgers & casual", "savings": "Medium"},
                    {"name": "Rameshwaram Cafe", "area": "Indiranagar", "vibe": "Quick, delicious dosa", "savings": "High"},
                ]
            },
            "mumbai": {
                "drinks": [
                    {"name": "Toto's Garage", "area": "Bandra", "vibe": "Neon, retro cars", "savings": "Medium"},
                    {"name": "Janata Bar", "area": "Bandra", "vibe": "No frills, local fav", "savings": "High"},
                    {"name": "Gokul", "area": "Colaba", "vibe": "Student favorite", "savings": "High"},
                ],
                "dinner": [
                    {"name": "Candies", "area": "Bandra", "vibe": "Portuguese villa, salads", "savings": "Medium"},
                    {"name": "Britannia & Co", "area": "Fort", "vibe": "Parsi heritage", "savings": "Medium"},
                    {"name": "Kyani & Co", "area": "Marine Lines", "vibe": "Irani cafe", "savings": "High"},
                ]
            }
        }

    def get_alternative(self, activity: str, location: str) -> Dict[str, Any]:
        """
        Get a recommendation based on activity and location.
        """
        city = "bangalore" # Default for MVP if not found
        
        # Simple detection
        loc_lower = location.lower()
        if "mumbai" in loc_lower or "bandra" in loc_lower or "colaba" in loc_lower:
            city = "mumbai"
        elif "delhi" in loc_lower:
            city = "delhi" # Fallback to generic if not in mock
            
        act_key = "drinks" if "drink" in activity.lower() or "bar" in activity.lower() else "dinner"
        
        # Get list for city/activity
        city_data = self.alternatives.get(city, self.alternatives["bangalore"])
        options = city_data.get(act_key, city_data["dinner"])
        
        return random.choice(options)
