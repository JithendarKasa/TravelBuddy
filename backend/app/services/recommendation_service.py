import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, neo4j_model):
        self.neo4j_model = neo4j_model

    def process_hotel_data(self, hotel: Dict[str, Any]) -> Dict[str, Any]:
        """Process and clean hotel data"""
        try:
            # Convert rating to float with 1 decimal place
            if hotel.get('rating'):
                hotel['rating'] = round(float(hotel['rating']), 1)
            
            # Process tags
            if hotel.get('tags'):
                if isinstance(hotel['tags'], str):
                    hotel['tags'] = [tag.strip() for tag in hotel['tags'].replace("'", "").split(',')]
                hotel['tags'] = list(filter(None, hotel['tags']))  # Remove empty tags
            
            # Ensure reviews are strings
            if hotel.get('positive_review') is None:
                hotel['positive_review'] = "No positive review available"
            if hotel.get('negative_review') is None:
                hotel['negative_review'] = "No negative review available"

            return hotel
        except Exception as e:
            logger.error(f"Error processing hotel data: {str(e)}")
            return hotel

    def get_location_recommendations(self, city: str, limit: int = 10) -> Dict[str, Any]:
        """Get hotel recommendations for a specific location"""
        try:
            logger.info(f"Getting recommendations for city: {city}")
            hotels = self.neo4j_model.get_location_based_recommendations(city, limit)
            
            processed_hotels = [self.process_hotel_data(hotel) for hotel in hotels]
            
            return {
                "status": "success",
                "recommended_hotels": processed_hotels,
                "count": len(processed_hotels),
                "location": city
            }
        except Exception as e:
            logger.error(f"Error getting location recommendations: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "recommended_hotels": []
            }

    def get_similar_hotels(self, hotel_name: str, limit: int = 5) -> Dict[str, Any]:
        """Get similar hotels based on reviewer patterns"""
        try:
            logger.info(f"Finding similar hotels to: {hotel_name}")
            similar_hotels = self.neo4j_model.get_similar_hotels_by_reviewers(hotel_name, limit)
            
            processed_hotels = [self.process_hotel_data(hotel) for hotel in similar_hotels]
            
            return {
                "status": "success",
                "similar_hotels": processed_hotels,
                "count": len(processed_hotels),
                "reference_hotel": hotel_name
            }
        except Exception as e:
            logger.error(f"Error getting similar hotels: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "similar_hotels": []
            }

    def get_travel_type_recommendations(self, travel_type: str, limit: int = 10) -> Dict[str, Any]:
        """Get recommendations based on travel type"""
        try:
            logger.info(f"Getting recommendations for travel type: {travel_type}")
            hotels = self.neo4j_model.get_recommendations_by_type(travel_type, limit)
            
            processed_hotels = [self.process_hotel_data(hotel) for hotel in hotels]
            
            return {
                "status": "success",
                "recommended_hotels": processed_hotels,
                "count": len(processed_hotels),
                "travel_type": travel_type
            }
        except Exception as e:
            logger.error(f"Error getting travel type recommendations: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "recommended_hotels": []
            }

    def get_personalized_recommendations(self, 
                                      preferences: Dict[str, Any], 
                                      limit: int = 10) -> Dict[str, Any]:
        """Get personalized recommendations based on user preferences"""
        try:
            logger.info(f"Getting personalized recommendations with preferences: {preferences}")
            
            # Get basic recommendations based on travel type
            travel_type = preferences.get('travel_type', 'Leisure trip')
            base_recommendations = self.neo4j_model.get_recommendations_by_type(travel_type, limit * 2)
            
            # Process and filter recommendations
            processed_hotels = []
            for hotel in base_recommendations:
                hotel = self.process_hotel_data(hotel)
                
                # Apply preference filters
                if preferences.get('min_rating') and hotel.get('rating', 0) < preferences['min_rating']:
                    continue
                    
                if preferences.get('required_tags'):
                    hotel_tags = set(hotel.get('tags', []))
                    required_tags = set(preferences['required_tags'])
                    if not required_tags.issubset(hotel_tags):
                        continue
                
                processed_hotels.append(hotel)
                if len(processed_hotels) >= limit:
                    break
            
            return {
                "status": "success",
                "recommended_hotels": processed_hotels,
                "count": len(processed_hotels),
                "preferences_applied": preferences
            }
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "recommended_hotels": []
            }