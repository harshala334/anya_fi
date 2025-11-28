"""Mock Real Estate Service for retrieving property data."""

from typing import Dict, Any, Optional
import random

class RealEstateService:
    """
    Mock service to simulate fetching real estate data.
    """
    
    def __init__(self):
        self.prices = {
            "mumbai": {"1bhk": 1.2, "2bhk": 2.1, "3bhk": 3.5},
            "bangalore": {"1bhk": 0.6, "2bhk": 1.1, "3bhk": 1.8},
            "delhi": {"1bhk": 0.5, "2bhk": 1.0, "3bhk": 1.6},
            "pune": {"1bhk": 0.45, "2bhk": 0.85, "3bhk": 1.4},
            "hyderabad": {"1bhk": 0.5, "2bhk": 0.9, "3bhk": 1.5},
        }
        
        self.areas = {
            "mumbai": ["Andheri West", "Bandra", "Powai", "Chembur"],
            "bangalore": ["Indiranagar", "Koramangala", "Whitefield", "HSR Layout"],
            "delhi": ["Saket", "Dwarka", "Vasant Kunj", "Lajpat Nagar"],
            "pune": ["Koregaon Park", "Viman Nagar", "Baner"],
            "hyderabad": ["Jubilee Hills", "Gachibowli", "Madhapur"]
        }

    def get_property_details(self, location: str, property_type: str) -> Dict[str, Any]:
        """
        Get details for a property.
        
        Args:
            location: City name (e.g., "Mumbai")
            property_type: Type (e.g., "2BHK")
            
        Returns:
            Dictionary with price, area, and description.
        """
        city = location.lower().strip()
        ptype = property_type.lower().strip()
        
        # Defaults
        if city not in self.prices:
            city = "bangalore"
        if ptype not in self.prices[city]:
            ptype = "2bhk"
            
        price_cr = self.prices[city][ptype]
        # Add some random variation
        price_cr = round(price_cr * random.uniform(0.9, 1.1), 2)
        
        area_name = random.choice(self.areas.get(city, ["City Center"]))
        
        return {
            "city": city.title(),
            "area": area_name,
            "type": ptype.upper(),
            "price_cr": price_cr,
            "price_formatted": f"₹{price_cr} Cr",
            "description": f"A beautiful {ptype.upper()} in {area_name}, {city.title()}."
        }
