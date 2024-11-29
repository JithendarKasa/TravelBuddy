class Neo4jHotelModel:
    def __init__(self, driver):
        self.driver = driver

    def get_location_based_recommendations(self, city, limit=5):
        with self.driver.session() as session:
            print(f"Searching for hotels in {city}")
            result = session.run("""
                MATCH (r:Review)
                WHERE r.hotel_address CONTAINS $city
                WITH r.hotel_name as hotel_name, 
                     r.hotel_address as address,
                     avg(r.reviewer_score) as avg_score,
                     count(r) as review_count,
                     collect(r.tags) as all_tags,
                     collect({
                         positive: r.positive_review,
                         negative: r.negative_review
                     }) as reviews
                RETURN 
                    hotel_name as name,
                    address as location,
                    avg_score as rating,
                    review_count as total_reviews,
                    all_tags[0] as tags,
                    reviews[0] as recent_review
                ORDER BY avg_score DESC
                LIMIT $limit
            """, city=city, limit=limit)
            
            hotels = [dict(record) for record in result]
            print(f"Found {len(hotels)} hotels")
            return hotels

    def get_similar_hotels(self, hotel_name, limit=5):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r1:Review)-[:REVIEWED_BY]->(rev:Reviewer)-[:REVIEWED]->(r2:Review)
                WHERE r1.hotel_name = $hotel_name 
                AND r2.hotel_name <> $hotel_name
                WITH r2.hotel_name as similar_hotel, 
                     r2.hotel_address as address,
                     avg(r2.reviewer_score) as avg_score,
                     count(DISTINCT rev) as shared_reviewers,
                     collect(r2.tags) as all_tags
                RETURN 
                    similar_hotel as name,
                    address as location,
                    avg_score as rating,
                    shared_reviewers,
                    all_tags[0] as tags
                ORDER BY shared_reviewers DESC, avg_score DESC
                LIMIT $limit
            """, hotel_name=hotel_name, limit=limit)
            
            return [dict(record) for record in result]

    def get_detailed_hotel_info(self, hotel_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Review)
                WHERE r.hotel_name = $hotel_name
                WITH r.hotel_name as hotel_name,
                     r.hotel_address as address,
                     avg(r.reviewer_score) as avg_score,
                     collect({
                         score: r.reviewer_score,
                         positive: r.positive_review,
                         negative: r.negative_review,
                         nationality: r.reviewer_nationality,
                         date: r.review_date
                     }) as reviews
                RETURN {
                    name: hotel_name,
                    location: address,
                    rating: avg_score,
                    reviews: reviews,
                    total_reviews: size(reviews)
                } as hotel_info
            """, hotel_name=hotel_name)
            
            return result.single()["hotel_info"]