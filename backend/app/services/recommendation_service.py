class RecommendationService:
    def __init__(self, neo4j_model):
        self.neo4j_model = neo4j_model
    
    def get_hotel_recommendations(self, hotel_name):
        try:
            similar_hotels = self.neo4j_model.get_similar_hotels(hotel_name)
            return similar_hotels
        except Exception as e:
            print(f"Error in recommendation service: {str(e)}")
            raise e

    def get_location_recommendations(self, city):
        try:
            location_hotels = self.neo4j_model.get_location_based_recommendations(city)
            return location_hotels
        except Exception as e:
            print(f"Error in recommendation service: {str(e)}")
            raise e