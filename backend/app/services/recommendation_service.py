class RecommendationService:
    def __init__(self, neo4j_model):
        self.neo4j_model = neo4j_model
    
    def get_recommendations(self, params):
        """Get hotel recommendations based on various parameters"""
        try:
            results = {}
            
            # Get location-based recommendations
            if 'city' in params:
                results['city_recommendations'] = self.neo4j_model.get_location_based_recommendations(
                    params['city']
                )

            # Get similar hotels if a hotel is specified
            if 'hotel_name' in params:
                results['similar_hotels'] = self.neo4j_model.get_similar_hotels_by_reviewers(
                    params['hotel_name']
                )

            # Get personalized recommendations if nationality is provided
            if 'nationality' in params:
                results['personalized'] = self.neo4j_model.get_personalized_recommendations(
                    params['nationality'],
                    params.get('preferences', [])
                )

            return {
                'status': 'success',
                'recommendations': results
            }
            
        except Exception as e:
            print(f"Error in recommendation service: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }