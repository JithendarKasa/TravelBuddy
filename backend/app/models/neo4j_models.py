from neo4j.exceptions import ServiceUnavailable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jHotelModel:
    def __init__(self, driver):
        self.driver = driver

    def get_location_based_recommendations(self, city, limit=10):
        """Get hotel recommendations based on location"""
        try:
            with self.driver.session() as session:
                logger.info(f"Searching for hotels in {city}")
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
                             nationality: r.reviewer_nationality,
                             tags: r.tags
                         })[0] as recent_review
                    WHERE review_count >= 5
                    WITH *, 
                         split(recent_review.tags, ',') as tag_list
                    RETURN 
                        hotel_name as name,
                        address as location,
                        avg_score as rating,
                        review_count as total_reviews,
                        recent_review.positive as positive_review,
                        recent_review.negative as negative_review,
                        tag_list as tags,
                        recent_review.nationality as reviewer_nationality
                    ORDER BY avg_score DESC, review_count DESC
                    LIMIT $limit
                """, city=city, limit=limit)
                
                hotels = [dict(record) for record in result]
                logger.info(f"Found {len(hotels)} hotels for {city}")
                return hotels
                
        except ServiceUnavailable as e:
            logger.error(f"Neo4j Database connection error: {str(e)}")
            raise Exception("Database connection error")
        except Exception as e:
            logger.error(f"Error in get_location_based_recommendations: {str(e)}")
            raise

    def get_similar_hotels_by_reviewers(self, hotel_name, limit=5):
        """Find hotels with similar reviewer patterns"""
        try:
            with self.driver.session() as session:
                logger.info(f"Finding similar hotels to {hotel_name}")
                result = session.run("""
                    MATCH (r1:Review {hotel_name: $hotel_name})
                    MATCH (r2:Review)
                    WHERE r1.hotel_name <> r2.hotel_name 
                    AND r1.reviewer_nationality = r2.reviewer_nationality
                    WITH r2.hotel_name as similar_hotel,
                         r2.hotel_address as address,
                         avg(toFloat(r2.reviewer_score)) as avg_score,
                         count(DISTINCT r2.reviewer_nationality) as shared_nationalities,
                         collect({
                             positive: r2.positive_review,
                             negative: r2.negative_review,
                             score: r2.reviewer_score,
                             tags: r2.tags
                         })[0] as recent_review
                    WHERE avg_score >= 7.0
                    RETURN 
                        similar_hotel as name,
                        address as location,
                        avg_score as rating,
                        shared_nationalities,
                        recent_review.positive as positive_review,
                        recent_review.negative as negative_review,
                        recent_review.tags as tags
                    ORDER BY shared_nationalities DESC, avg_score DESC
                    LIMIT $limit
                """, hotel_name=hotel_name, limit=limit)
                
                similar_hotels = [dict(record) for record in result]
                logger.info(f"Found {len(similar_hotels)} similar hotels")
                return similar_hotels
                
        except Exception as e:
            logger.error(f"Error finding similar hotels: {str(e)}")
            raise

    def get_recommendations_by_type(self, travel_type, limit=10):
        """Get hotel recommendations based on travel type"""
        try:
            with self.driver.session() as session:
                logger.info(f"Finding hotels for travel type: {travel_type}")
                result = session.run("""
                    MATCH (r:Review)
                    WHERE r.tags CONTAINS $travel_type
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
                    AND avg_score >= 7.0
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
                """, travel_type=travel_type, limit=limit)
                
                hotels = [dict(record) for record in result]
                logger.info(f"Found {len(hotels)} hotels for type {travel_type}")
                return hotels
                
        except Exception as e:
            logger.error(f"Error getting recommendations by type: {str(e)}")
            raise

    def test_connection(self):
        """Test the Neo4j connection"""
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()["count"]
                return {"status": "success", "node_count": count}
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {"status": "error", "message": str(e)}