# from neo4j import GraphDatabase
# import logging
# from collections import Counter

# class DestinationGraphManager:
#     def __init__(self, uri, user, password, database):
#         self.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
#         self.logger = logging.getLogger(__name__)

#     def create_hotel_destination_graph(self, hotel_data):
#         """
#         Creates nodes and relationships from hotel review data
#         hotel_data: List of dictionaries containing hotel information and reviews
#         """
#         def create_graph_tx(tx, data):
#             # Create indexes for faster lookups
#             tx.run("CREATE INDEX IF NOT EXISTS FOR (h:Hotel) ON (h.name)")
#             tx.run("CREATE INDEX IF NOT EXISTS FOR (c:City) ON (c.name)")
#             tx.run("CREATE INDEX IF NOT EXISTS FOR (t:Tag) ON (t.name)")
            
#             for hotel in data:
#                 # Extract city from hotel address
#                 city = hotel['location'].split(',')[-2].strip()
                
#                 # Create hotel and city nodes
#                 tx.run("""
#                     MERGE (h:Hotel {name: $hotel_name})
#                     SET h.rating = $rating,
#                         h.reviewCount = $review_count,
#                         h.address = $address
#                     MERGE (c:City {name: $city})
#                     MERGE (h)-[:LOCATED_IN]->(c)
#                 """, hotel_name=hotel['name'],
#                      rating=hotel['averageReviewScore'],
#                      review_count=hotel['reviewCount'],
#                      address=hotel['location'],
#                      city=city)
                
#                 # Create tags and relationships
#                 for tag in hotel['tags']:
#                     tx.run("""
#                         MERGE (t:Tag {name: $tag})
#                         MERGE (h:Hotel {name: $hotel_name})
#                         MERGE (h)-[:HAS_TAG]->(t)
#                     """, tag=tag, hotel_name=hotel['name'])

#         with self.driver.session() as session:
#             session.execute_write(create_graph_tx, hotel_data)

#     def find_related_destinations(self, city, tag_type=None, limit=5):
#         """
#         Find destinations similar to the given city based on shared hotel characteristics
#         """
#         query = """
#         MATCH (c1:City {name: $city})<-[:LOCATED_IN]-(h1:Hotel)-[:HAS_TAG]->(t:Tag)
#         MATCH (h2:Hotel)-[:HAS_TAG]->(t)
#         WHERE h2 <> h1
#         MATCH (h2)-[:LOCATED_IN]->(c2:City)
#         WHERE c2 <> c1
#         """
        
#         if tag_type:
#             query += "AND t.name CONTAINS $tag_type "
            
#         query += """
#         WITH c2, count(DISTINCT t) as shared_tags, avg(h2.rating) as avg_rating
#         RETURN c2.name as city,
#                shared_tags,
#                avg_rating
#         ORDER BY shared_tags DESC, avg_rating DESC
#         LIMIT $limit
#         """
        
#         with self.driver.session() as session:
#             result = session.run(query, city=city, tag_type=tag_type, limit=limit)
#             return [dict(record) for record in result]

#     def find_connected_hotels(self, city, tags=None, min_rating=4.0, limit=10):
#         """
#         Find hotels in a city and nearby cities that match specific tags and rating criteria
#         """
#         query = """
#         MATCH (c:City {name: $city})<-[:LOCATED_IN]-(h1:Hotel)
#         MATCH (h1)-[:HAS_TAG]->(t:Tag)
#         WHERE h1.rating >= $min_rating
#         """
        
#         if tags:
#             query += "AND t.name IN $tags "
            
#         query += """
#         WITH h1, collect(t.name) as tags
#         MATCH (h1)-[:LOCATED_IN]->(c1:City)
#         OPTIONAL MATCH (c1)<-[:LOCATED_IN]-(h2:Hotel)
#         WHERE h2 <> h1 AND h2.rating >= $min_rating
#         WITH h1, h2, tags, c1,
#              CASE WHEN h2 IS NOT NULL 
#                   THEN [(h2)-[:HAS_TAG]->(t) | t.name] 
#                   ELSE [] 
#              END as h2_tags
#         WHERE h2 IS NULL OR size([t IN h2_tags WHERE t IN $tags]) > 0
#         RETURN DISTINCT 
#             h1.name as hotel_name,
#             h1.rating as rating,
#             c1.name as city,
#             tags as hotel_tags,
#             collect(DISTINCT {
#                 name: h2.name,
#                 rating: h2.rating,
#                 tags: h2_tags
#             }) as nearby_hotels
#         ORDER BY h1.rating DESC
#         LIMIT $limit
#         """
        
#         with self.driver.session() as session:
#             result = session.run(query, 
#                                city=city, 
#                                tags=tags if tags else [], 
#                                min_rating=min_rating, 
#                                limit=limit)
#             return [dict(record) for record in result]

#     def get_destination_insights(self, city):
#         """
#         Get insights about a destination including popular tags and hotel statistics
#         """
#         query = """
#         MATCH (c:City {name: $city})<-[:LOCATED_IN]-(h:Hotel)-[:HAS_TAG]->(t:Tag)
#         WITH c,
#              count(DISTINCT h) as hotel_count,
#              avg(h.rating) as avg_rating,
#              collect(DISTINCT t.name) as tags,
#              sum(h.reviewCount) as total_reviews
#         RETURN c.name as city,
#                hotel_count,
#                avg_rating,
#                tags,
#                total_reviews
#         """
        
#         with self.driver.session() as session:
#             result = session.run(query, city=city)
#             return dict(result.single())

#     def close(self):
#         """Close the Neo4j driver connection"""
#         self.driver.close()

from neo4j import GraphDatabase
import logging
from collections import Counter

class DestinationGraphManager:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
        self.logger = logging.getLogger(__name__)
        self.ensure_connection()

    def ensure_connection(self):
        """Establish or verify connection to Neo4j"""
        try:
            if self.driver is None:
                self.driver = GraphDatabase.driver(
                    self._uri, 
                    auth=(self._user, self._password),
                    database=self._database
                )
            # Test the connection
            with self.driver.session() as session:
                session.run("RETURN 1")
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {str(e)}")
            # Try to reconnect
            if self.driver:
                self.driver.close()
            self.driver = GraphDatabase.driver(
                self._uri, 
                auth=(self._user, self._password),
                database=self._database
            )

    def initialize_database(self):
        """Initialize Neo4j database with required schema"""
        with self.driver.session() as session:
            try:
                # Create constraints
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (h:Hotel) REQUIRE h.name IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:City) REQUIRE c.name IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE")
                
                self.logger.info("Database schema initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing database: {str(e)}")
                raise

    def extract_city(self, address):
        """Extract city name from hotel address"""
        try:
            # Split by spaces and commas
            parts = address.split(' ')
            # For addresses like "202 rue de Rivoli 1st arr 75001 Paris France"
            # Look for major cities in the address
            major_cities = ['Paris', 'London', 'Rome', 'Barcelona', 'Vienna', 'Amsterdam']
            for part in parts:
                if part in major_cities:
                    return part
                    
            # If no major city found, try splitting by comma
            comma_parts = address.split(',')
            if len(comma_parts) >= 2:
                for part in comma_parts:
                    clean_part = part.strip()
                    if clean_part in major_cities:
                        return clean_part
            
            return None
        except Exception as e:
            self.logger.error(f"Error extracting city: {str(e)}")
            return None

    # def create_hotel_destination_graph(self, hotel_data):
    #     """Creates nodes and relationships from hotel review data"""
    #     def create_graph_tx(tx, data):
    #         for hotel in data:
    #             try:
    #                 # Extract city from hotel address
    #                 city = self.extract_city(hotel['location'])
    #                 if not city:
    #                     continue

    #                 # Create hotel node
    #                 tx.run("""
    #                     MERGE (h:Hotel {name: $hotel_name})
    #                     SET h.rating = $rating,
    #                         h.reviewCount = $review_count,
    #                         h.address = $address
    #                 """, 
    #                 hotel_name=hotel['name'],
    #                 rating=float(hotel['averageReviewScore']),
    #                 review_count=int(hotel['reviewCount']),
    #                 address=hotel['location'])

    #                 # Create city node and relationship
    #                 tx.run("""
    #                     MERGE (c:City {name: $city})
    #                     WITH c
    #                     MATCH (h:Hotel {name: $hotel_name})
    #                     MERGE (h)-[:LOCATED_IN]->(c)
    #                 """, 
    #                 city=city,
    #                 hotel_name=hotel['name'])

    #                 # Create tags and relationships
    #                 for tag in hotel['tags']:
    #                     if tag.strip():
    #                         tx.run("""
    #                             MERGE (t:Tag {name: $tag})
    #                             WITH t
    #                             MATCH (h:Hotel {name: $hotel_name})
    #                             MERGE (h)-[:HAS_TAG]->(t)
    #                         """, 
    #                         tag=tag.strip(),
    #                         hotel_name=hotel['name'])

    #             except Exception as e:
    #                 self.logger.error(f"Error processing hotel {hotel.get('name', 'unknown')}: {str(e)}")
    #                 continue

    #     with self.driver.session() as session:
    #         try:
    #             session.execute_write(create_graph_tx, hotel_data)
    #             self.logger.info(f"Successfully created graph for {len(hotel_data)} hotels")
    #         except Exception as e:
    #             self.logger.error(f"Error creating graph: {str(e)}")
    #             raise

    def create_hotel_destination_graph(self, hotel_data):
        """Creates nodes and relationships from hotel review data"""
        def create_graph_tx(tx, data):
            for hotel in data:
                try:
                    # Extract city from hotel address
                    city = self.extract_city(hotel['location'])
                    if not city:
                        continue

                    # Create hotel node with defaulted properties if missing
                    tx.run("""
                        MERGE (h:Hotel {name: $hotel_name})
                        SET h.rating = $rating,
                            h.reviewCount = $review_count,
                            h.address = $address
                    """, 
                    hotel_name=hotel['name'],
                    rating=float(hotel.get('averageReviewScore', 0.0)),
                    review_count=int(hotel.get('reviewCount', 0)),
                    address=hotel['location'])

                    # Create city and relationships
                    tx.run("""
                        MERGE (c:City {name: $city})
                        WITH c
                        MATCH (h:Hotel {name: $hotel_name})
                        MERGE (h)-[:LOCATED_IN]->(c)
                    """, 
                    city=city,
                    hotel_name=hotel['name'])

                    # Create tags
                    if 'tags' in hotel and hotel['tags']:
                        for tag in hotel['tags']:
                            if tag and tag.strip():
                                tx.run("""
                                    MERGE (t:Tag {name: $tag})
                                    WITH t
                                    MATCH (h:Hotel {name: $hotel_name})
                                    MERGE (h)-[:HAS_TAG]->(t)
                                """, 
                                tag=tag.strip(),
                                hotel_name=hotel['name'])

                except Exception as e:
                    self.logger.error(f"Error processing hotel {hotel.get('name', 'unknown')}: {str(e)}")
                    continue

        with self.driver.session() as session:
            try:
                session.execute_write(create_graph_tx, hotel_data)
                self.logger.info(f"Successfully created graph for {len(hotel_data)} hotels")
            except Exception as e:
                self.logger.error(f"Error creating graph: {str(e)}")
                raise

    def find_related_destinations(self, city, tag_type=None, limit=5):
        """Find destinations similar to the given city"""
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
            try:
                result = session.run(query, city=city, tag_type=tag_type, limit=limit)
                return [dict(record) for record in result]
            except Exception as e:
                self.logger.error(f"Error finding related destinations: {str(e)}")
                return []

    def get_destination_insights(self, city):
        """Get insights about a destination"""
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
            try:
                result = session.run(query, city=city)
                record = result.single()
                if record:
                    return dict(record)
                return None
            except Exception as e:
                self.logger.error(f"Error getting destination insights: {str(e)}")
                return None

    # def find_connected_hotels(self, city, tags=None, min_rating=4.0, limit=10):
        """Find hotels in a city and nearby cities"""
        query = """
        MATCH (c:City {name: $city})<-[:LOCATED_IN]-(h1:Hotel)
        WHERE h1.rating >= $min_rating
        """
        
        if tags and tags[0]:
            query += """
            MATCH (h1)-[:HAS_TAG]->(t:Tag)
            WHERE t.name IN $tags
            """
            
        query += """
        WITH h1
        MATCH (h1)-[:LOCATED_IN]->(c1:City)
        OPTIONAL MATCH (c1)<-[:LOCATED_IN]-(h2:Hotel)
        WHERE h2 <> h1 AND h2.rating >= $min_rating
        WITH h1, h2, c1,
             CASE WHEN h2 IS NOT NULL 
                  THEN [(h2)-[:HAS_TAG]->(t) | t.name] 
                  ELSE [] 
             END as h2_tags
        RETURN DISTINCT 
            h1.name as hotel_name,
            h1.rating as rating,
            c1.name as city,
            [(h1)-[:HAS_TAG]->(t) | t.name] as hotel_tags,
            collect(DISTINCT {
                name: h2.name,
                rating: h2.rating,
                tags: h2_tags
            }) as nearby_hotels
        ORDER BY h1.rating DESC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(query, 
                                   city=city, 
                                   tags=tags if tags else [], 
                                   min_rating=min_rating, 
                                   limit=limit)
                return [dict(record) for record in result]
            except Exception as e:
                self.logger.error(f"Error finding connected hotels: {str(e)}")
                return []

    def find_connected_hotels(self, city, tags=None, min_rating=4.0, limit=10):
        """Find hotels in a city and nearby cities"""
        query = """
        MATCH (c:City {name: $city})<-[:LOCATED_IN]-(h1:Hotel)
        WHERE h1.rating >= $min_rating
        """
        
        if tags and tags[0]:
            query += """
            MATCH (h1)-[:HAS_TAG]->(t:Tag)
            WHERE t.name IN $tags
            """
            
        query += """
        WITH h1
        MATCH (h1)-[:LOCATED_IN]->(c1:City)
        OPTIONAL MATCH (c1)<-[:LOCATED_IN]-(h2:Hotel)
        WHERE h2 <> h1 AND h2.rating >= $min_rating
        WITH h1, h2, c1,
            CASE WHEN h2 IS NOT NULL 
                THEN [(h2)-[:HAS_TAG]->(t) | t.name] 
                ELSE [] 
            END as h2_tags
        RETURN DISTINCT 
            h1.name as hotel_name,
            h1.rating as rating,
            c1.name as city,
            [(h1)-[:HAS_TAG]->(t) | t.name] as hotel_tags,
            collect(DISTINCT {
                name: h2.name,
                rating: h2.rating,
                tags: h2_tags
            }) as nearby_hotels
        ORDER BY h1.rating DESC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(query, 
                                city=city, 
                                tags=tags if tags else [], 
                                min_rating=min_rating, 
                                limit=limit)
                return [dict(record) for record in result]
            except Exception as e:
                self.logger.error(f"Error finding connected hotels: {str(e)}")
                return []
            
    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()