from neo4j import GraphDatabase
import logging
from collections import Counter

class DestinationGraphManager:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
        self.logger = logging.getLogger(__name__)

    def create_hotel_destination_graph(self, hotel_data):
        """
        Creates nodes and relationships from hotel review data
        hotel_data: List of dictionaries containing hotel information and reviews
        """
        def create_graph_tx(tx, data):
            # Create indexes for faster lookups
            tx.run("CREATE INDEX IF NOT EXISTS FOR (h:Hotel) ON (h.name)")
            tx.run("CREATE INDEX IF NOT EXISTS FOR (c:City) ON (c.name)")
            tx.run("CREATE INDEX IF NOT EXISTS FOR (t:Tag) ON (t.name)")
            
            for hotel in data:
                # Extract city from hotel address
                city = hotel['location'].split(',')[-2].strip()
                
                # Create hotel and city nodes
                tx.run("""
                    MERGE (h:Hotel {name: $hotel_name})
                    SET h.rating = $rating,
                        h.reviewCount = $review_count,
                        h.address = $address
                    MERGE (c:City {name: $city})
                    MERGE (h)-[:LOCATED_IN]->(c)
                """, hotel_name=hotel['name'],
                     rating=hotel['averageReviewScore'],
                     review_count=hotel['reviewCount'],
                     address=hotel['location'],
                     city=city)
                
                # Create tags and relationships
                for tag in hotel['tags']:
                    tx.run("""
                        MERGE (t:Tag {name: $tag})
                        MERGE (h:Hotel {name: $hotel_name})
                        MERGE (h)-[:HAS_TAG]->(t)
                    """, tag=tag, hotel_name=hotel['name'])

        with self.driver.session() as session:
            session.execute_write(create_graph_tx, hotel_data)

    def find_related_destinations(self, city, tag_type=None, limit=5):
        """
        Find destinations similar to the given city based on shared hotel characteristics
        """
        query = """
        MATCH (c1:City {name: $city})<-[:LOCATED_IN]-(h1:Hotel)-[:HAS_TAG]->(t:Tag)
        MATCH (h2:Hotel)-[:HAS_TAG]->(t)
        WHERE h2 <> h1
        MATCH (h2)-[:LOCATED_IN]->(c2:City)
        WHERE c2 <> c1
        """
        
        if tag_type:
            query += "AND t.name CONTAINS $tag_type "
            
        query += """
        WITH c2, count(DISTINCT t) as shared_tags, avg(h2.rating) as avg_rating
        RETURN c2.name as city,
               shared_tags,
               avg_rating
        ORDER BY shared_tags DESC, avg_rating DESC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, city=city, tag_type=tag_type, limit=limit)
            return [dict(record) for record in result]

    def find_connected_hotels(self, city, tags=None, min_rating=4.0, limit=10):
        """
        Find hotels in a city and nearby cities that match specific tags and rating criteria
        """
        query = """
        MATCH (c:City {name: $city})<-[:LOCATED_IN]-(h1:Hotel)
        MATCH (h1)-[:HAS_TAG]->(t:Tag)
        WHERE h1.rating >= $min_rating
        """
        
        if tags:
            query += "AND t.name IN $tags "
            
        query += """
        WITH h1, collect(t.name) as tags
        MATCH (h1)-[:LOCATED_IN]->(c1:City)
        OPTIONAL MATCH (c1)<-[:LOCATED_IN]-(h2:Hotel)
        WHERE h2 <> h1 AND h2.rating >= $min_rating
        WITH h1, h2, tags, c1,
             CASE WHEN h2 IS NOT NULL 
                  THEN [(h2)-[:HAS_TAG]->(t) | t.name] 
                  ELSE [] 
             END as h2_tags
        WHERE h2 IS NULL OR size([t IN h2_tags WHERE t IN $tags]) > 0
        RETURN DISTINCT 
            h1.name as hotel_name,
            h1.rating as rating,
            c1.name as city,
            tags as hotel_tags,
            collect(DISTINCT {
                name: h2.name,
                rating: h2.rating,
                tags: h2_tags
            }) as nearby_hotels
        ORDER BY h1.rating DESC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                               city=city, 
                               tags=tags if tags else [], 
                               min_rating=min_rating, 
                               limit=limit)
            return [dict(record) for record in result]

    def get_destination_insights(self, city):
        """
        Get insights about a destination including popular tags and hotel statistics
        """
        query = """
        MATCH (c:City {name: $city})<-[:LOCATED_IN]-(h:Hotel)-[:HAS_TAG]->(t:Tag)
        WITH c,
             count(DISTINCT h) as hotel_count,
             avg(h.rating) as avg_rating,
             collect(DISTINCT t.name) as tags,
             sum(h.reviewCount) as total_reviews
        RETURN c.name as city,
               hotel_count,
               avg_rating,
               tags,
               total_reviews
        """
        
        with self.driver.session() as session:
            result = session.run(query, city=city)
            return dict(result.single())

    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()