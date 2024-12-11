class HotelRecommendationService:
    def __init__(self, neo4j_model):
        self.model = neo4j_model

    def get_personalized_recommendations(self, preferences):
        """Get personalized hotel recommendations based on user preferences"""
        trip_type = preferences.get('trip_type', 'Leisure trip')
        nationality = preferences.get('nationality')
        min_score = float(preferences.get('min_score', 7.0))

        recommendations = self.model.get_recommendations_by_preferences(
            trip_type=trip_type,
            nationality=nationality,
            min_score=min_score
        )

        # Add similarity scores and sort
        for hotel in recommendations:
            hotel['similarity_score'] = self._calculate_similarity_score(hotel, preferences)

        return sorted(recommendations, key=lambda x: x['similarity_score'], reverse=True)

    def find_similar_hotels(self, hotel_name):
        """Find similar hotels based on review patterns and trip types"""
        return self.model.find_similar_hotels(hotel_name)

    def _calculate_similarity_score(self, hotel, preferences):
        """Calculate similarity score based on preferences matching"""
        base_score = hotel['avg_score'] * 0.6  # 60% weight to rating
        review_weight = min(hotel['review_count'] / 100, 1) * 0.4  # 40% weight to review count
        return base_score + review_weight