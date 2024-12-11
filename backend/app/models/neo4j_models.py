from neo4j import GraphDatabase
from datetime import datetime

class HotelRecommendationModel:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_location_based_recommendations(self, city, limit=10):
        with self.driver.session() as session:
            print(f"Searching for hotels in {city}")
            result = session.run("""
                MATCH (r:Review)
                WHERE toLower(r.hotel_address) CONTAINS toLower($city)
                WITH r.hotel_name as hotel_name, 
                     r.hotel_address as address,
                     avg(toFloat(r.reviewer_score)) as avg_score,
                     count(r) as review_count,
                     collect({
                         positive: r.positive_review,
                         negative: r.negative_review,
                         score: r.reviewer_score,
                         tags: r.tags
                     })[0] as recent_review
                WHERE review_count >= 5  // Filter out hotels with too few reviews
                RETURN 
                    hotel_name as name,
                    address as location,
                    avg_score as rating,
                    review_count as total_reviews,
                    recent_review.positive as positive_review,
                    recent_review.negative as negative_review,
                    recent_review.tags as tags
                ORDER BY avg_score DESC, review_count DESC
                LIMIT $limit
            """, city=city, limit=limit)
            return [dict(record) for record in result]

    def search_by_tags(self, tag, limit=10):
        with self.driver.session() as session:
            print(f"Searching by tag: {tag}")
            result = session.run("""
                MATCH (r:Review)
                WHERE r.tags CONTAINS $tag
                WITH r.hotel_name as hotel_name, 
                     r.hotel_address as address,
                     avg(toFloat(r.reviewer_score)) as avg_score,
                     count(r) as review_count,
                     collect({
                         positive: r.positive_review,
                         negative: r.negative_review,
                         score: r.reviewer_score,
                         tags: r.tags
                     })[0] as recent_review
                WHERE review_count >= 5
                RETURN 
                    hotel_name as name,
                    address as location,
                    avg_score as rating,
                    review_count as total_reviews,
                    recent_review.positive as positive_review,
                    recent_review.negative as negative_review,
                    recent_review.tags as tags
                ORDER BY avg_score DESC, review_count DESC
                LIMIT $limit
            """, tag=tag, limit=limit)
            return [dict(record) for record in result]

    def get_personalized_recommendations(self, preferences):
        with self.driver.session() as session:
            trip_type = preferences.get('trip_type')
            nationality = preferences.get('nationality')
            min_score = float(preferences.get('min_score', 7.0))
            
            query = """
                MATCH (r:Review)
                WHERE r.tags CONTAINS $trip_type
                AND toFloat(r.reviewer_score) >= $min_score
            """
            
            if nationality:
                query += " AND r.reviewer_nationality = $nationality"
                
            query += """
                WITH r.hotel_name as hotel_name, 
                     r.hotel_address as address,
                     avg(toFloat(r.reviewer_score)) as avg_score,
                     count(r) as review_count,
                     collect({
                         positive: r.positive_review,
                         negative: r.negative_review,
                         score: r.reviewer_score,
                         tags: r.tags
                     })[0] as recent_review
                WHERE review_count >= 5
                RETURN 
                    hotel_name as name,
                    address as location,
                    avg_score as rating,
                    review_count as total_reviews,
                    recent_review.positive as positive_review,
                    recent_review.negative as negative_review,
                    recent_review.tags as tags
                ORDER BY avg_score DESC, review_count DESC
                LIMIT 10
            """
            
            result = session.run(query, {
                'trip_type': trip_type,
                'nationality': nationality,
                'min_score': min_score
            })
            return [dict(record) for record in result]

    def find_similar_hotels(self, hotel_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r1:Review)
                WHERE r1.hotel_name = $hotel_name
                MATCH (r2:Review)
                WHERE r2.hotel_name <> $hotel_name
                AND r2.tags = r1.tags
                WITH r2.hotel_name as hotel_name, 
                     r2.hotel_address as address,
                     avg(toFloat(r2.reviewer_score)) as avg_score,
                     count(r2) as review_count,
                     collect({
                         positive: r2.positive_review,
                         negative: r2.negative_review,
                         score: r2.reviewer_score,
                         tags: r2.tags
                     })[0] as recent_review
                WHERE review_count >= 5
                RETURN 
                    hotel_name as name,
                    address as location,
                    avg_score as rating,
                    review_count as total_reviews,
                    recent_review.positive as positive_review,
                    recent_review.negative as negative_review,
                    recent_review.tags as tags
                ORDER BY avg_score DESC, review_count DESC
                LIMIT 5
            """, hotel_name=hotel_name)
            return [dict(record) for record in result]

    def test_connection(self):
        """Test the Neo4j connection"""
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (r:Review) RETURN count(r) as count")
                count = result.single()["count"]
                return {"status": "success", "review_count": count}
        except Exception as e:
            return {"status": "error", "message": str(e)}