class Neo4jHotelModel:
    def __init__(self, driver):
        self.driver = driver

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
                         pos: r.positive_review,
                         neg: r.negative_review,
                         score: r.reviewer_score,
                         tags: r.tags
                     })[0] as recent_review
                RETURN 
                    hotel_name as name,
                    address as location,
                    avg_score as rating,
                    review_count as total_reviews,
                    recent_review.pos as positive_review,
                    recent_review.neg as negative_review,
                    recent_review.tags as tags
                ORDER BY avg_score DESC
                LIMIT $limit
            """, city=city, limit=limit)
            
            hotels = []
            for record in result:
                hotel = dict(record)
                print(f"Processing hotel: {hotel['name']}")
                hotels.append(hotel)
            
            return hotels

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
                         pos: r.positive_review,
                         neg: r.negative_review,
                         tags: r.tags,
                         score: r.reviewer_score
                     })[0] as recent_review
                RETURN 
                    hotel_name as name,
                    address as location,
                    avg_score as rating,
                    review_count as total_reviews,
                    recent_review.pos as positive_review,
                    recent_review.neg as negative_review,
                    recent_review.tags as tags
                ORDER BY avg_score DESC, review_count DESC
                LIMIT $limit
            """, tag=tag, limit=limit)
            
            hotels = []
            for record in result:
                hotel = dict(record)
                print(f"Found hotel with tag: {hotel['name']}")
                hotels.append(hotel)
            
            return hotels