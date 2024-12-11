from pymongo import MongoClient
from neo4j import GraphDatabase
import logging
from datetime import datetime


class TravelBuddyQueries:
    def __init__(self):
        # MongoDB connection
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo_client['TravelBuddy']

        # Neo4j connection
        self.neo4j_driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "moderndbproject"),
            database="travelbuddy"
        )

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    # def search_hotels_by_features(self, features, limit=10):
    #     """
    #     Search hotels based on features mentioned in reviews or tags
    #     """
    #     try:
    #         # Create regex patterns for each feature
    #         feature_patterns = [f".*{feature}.*" for feature in features]

    #         pipeline = [
    #             {
    #                 "$match": {
    #                     "$and": [
    #                         {"Tags": {"$regex": pattern, "$options": "i"}} for pattern in feature_patterns
    #                     ]
    #                 }
    #             },
    #             # Group by hotel to get unique hotels
    #             {
    #                 "$group": {
    #                     "_id": "$Hotel_Name",
    #                     "Hotel_Address": {"$first": "$Hotel_Address"},
    #                     "Average_Score": {"$first": "$Average_Score"},
    #                     "review_count": {"$sum": 1},
    #                     "avg_reviewer_score": {"$avg": "$Reviewer_Score"},
    #                     "sample_tags": {"$first": "$Tags"}
    #                 }
    #             },
    #             {
    #                 "$project": {
    #                     "Hotel_Name": "$_id",
    #                     "Hotel_Address": 1,
    #                     "Average_Score": 1,
    #                     "review_count": 1,
    #                     "avg_reviewer_score": 1,
    #                     "Tags": "$sample_tags",
    #                     "_id": 0
    #                 }
    #             },
    #             {"$sort": {"Average_Score": -1}},
    #             {"$limit": limit}
    #         ]

    #         results = list(self.db.HotelReviews.aggregate(pipeline))
    #         return results
    #     except Exception as e:
    #         self.logger.error(f"Error in search_hotels_by_features: {str(e)}")
    #         raise

    # def search_hotels_by_features(self, features, limit=10):
        # """
        # Search hotels based on features mentioned in reviews or tags
        # """
        # try:
        #     # If no features provided, return top-rated hotels
        #     if not features:
        #         pipeline = [
        #             {
        #                 "$project": {
        #                     "Hotel_Name": 1,
        #                     "Hotel_Address": 1,
        #                     "Average_Score": 1,
        #                     "review_count": 1,
        #                     "avg_reviewer_score": "$Reviewer_Score",
        #                     "Tags": 1
        #                 }
        #             },
        #             {
        #                 "$group": {
        #                     "_id": "$Hotel_Name",
        #                     "Hotel_Address": {"$first": "$Hotel_Address"},
        #                     "Average_Score": {"$first": "$Average_Score"},
        #                     "review_count": {"$sum": 1},
        #                     "avg_reviewer_score": {"$avg": "$avg_reviewer_score"},
        #                     "sample_tags": {"$first": "$Tags"}
        #                 }
        #             },
        #             {
        #                 "$project": {
        #                     "Hotel_Name": "$_id",
        #                     "Hotel_Address": 1,
        #                     "Average_Score": 1,
        #                     "review_count": 1,
        #                     "avg_reviewer_score": 1,
        #                     "Tags": "$sample_tags",
        #                     "_id": 0
        #                 }
        #             },
        #             {"$sort": {"Average_Score": -1}},
        #             {"$limit": limit}
        #         ]
        #     else:
        #         # Create regex patterns for each feature
        #         feature_patterns = [f".*{feature}.*" for feature in features]
                
        #         pipeline = [
        #             {
        #                 "$match": {
        #                     "$and": [
        #                         {"Tags": {"$regex": pattern, "$options": "i"}} for pattern in feature_patterns
        #                     ]
        #                 }
        #             },
        #             {
        #                 "$group": {
        #                     "_id": "$Hotel_Name",
        #                     "Hotel_Address": {"$first": "$Hotel_Address"},
        #                     "Average_Score": {"$first": "$Average_Score"},
        #                     "review_count": {"$sum": 1},
        #                     "avg_reviewer_score": {"$avg": "$Reviewer_Score"},
        #                     "sample_tags": {"$first": "$Tags"}
        #                 }
        #             },
        #             {
        #                 "$project": {
        #                     "Hotel_Name": "$_id",
        #                     "Hotel_Address": 1,
        #                     "Average_Score": 1,
        #                     "review_count": 1,
        #                     "avg_reviewer_score": 1,
        #                     "Tags": "$sample_tags",
        #                     "_id": 0
        #                 }
        #             },
        #             {"$sort": {"Average_Score": -1}},
        #             {"$limit": limit}
        #         ]

        #     results = list(self.db.HotelReviews.aggregate(pipeline))
        #     return results
        # except Exception as e:
        #     self.logger.error(f"Error in search_hotels_by_features: {str(e)}")
        #     raise

    # def get_hotel_sentiment_analysis(self, hotel_name):
        # """
        # Analyze sentiment patterns for a specific hotel
        # """
        # try:
        #     pipeline = [
        #         {
        #             "$match": {"Hotel_Name": hotel_name}
        #         },
        #         {
        #             "$lookup": {
        #                 "from": "reviews",
        #                 "localField": "_id",
        #                 "foreignField": "hotel_id",
        #                 "as": "reviews"
        #             }
        #         },
        #         {
        #             "$project": {
        #                 "Hotel_Name": 1,
        #                 "Average_Score": 1,
        #                 "total_reviews": {"$size": "$reviews"},
        #                 "positive_reviews": {
        #                     "$size": {
        #                         "$filter": {
        #                             "input": "$reviews",
        #                             "as": "review",
        #                             "cond": {"$gt": ["$$review.Reviewer_Score", 7]}
        #                         }
        #                     }
        #                 },
        #                 "negative_reviews": {
        #                     "$size": {
        #                         "$filter": {
        #                             "input": "$reviews",
        #                             "as": "review",
        #                             "cond": {"$lt": ["$$review.Reviewer_Score", 5]}
        #                         }
        #                     }
        #                 },
        #                 "review_distribution": {
        #                     "$map": {
        #                         "input": {"$range": [0, 10]},
        #                         "as": "score",
        #                         "in": {
        #                             "score": "$$score",
        #                             "count": {
        #                                 "$size": {
        #                                     "$filter": {
        #                                         "input": "$reviews",
        #                                         "as": "review",
        #                                         "cond": {"$eq": [{"$floor": "$$review.Reviewer_Score"}, "$$score"]}
        #                                     }
        #                                 }
        #                             }
        #                         }
        #                     }
        #                 }
        #             }
        #         }
        #     ]
        #     result = list(self.db.hotels.aggregate(pipeline))
        #     if not result:
        #         raise ValueError(f"No hotel found with name: {hotel_name}")
        #     return result[0]
        # except Exception as e:
        #     self.logger.error(f"Error in get_hotel_sentiment_analysis: {str(e)}")
        #     raise

    # def find_similar_hotels_neo4j(self, hotel_name, limit=5):
        # """
        # Find similar hotels based on common reviewers and tags using Neo4j
        # """
        # try:
        #     with self.neo4j_driver.session(database="travelbuddy") as session:
        #         result = session.run("""
        #             MATCH (h:Hotel {name: $hotel_name})
        #             MATCH (h)-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(other:Hotel)
        #             WHERE h <> other
        #             WITH other, count(DISTINCT t) as common_tags
        #             MATCH (other)<-[:ABOUT]-(r:Review)
        #             WITH other, common_tags, avg(r.score) as avg_score
        #             RETURN other.name as hotel_name,
        #                    common_tags,
        #                    avg_score,
        #                    other.address as address
        #             ORDER BY common_tags DESC, avg_score DESC
        #             LIMIT $limit
        #         """, hotel_name=hotel_name, limit=limit)
        #         return [dict(record) for record in result]
        # except Exception as e:
        #     self.logger.error(f"Error in find_similar_hotels_neo4j: {str(e)}")
        #     raise

    # def analyze_traveler_patterns(self, nationality, limit=10):
        # """
        # Analyze travel patterns for specific nationalities using Neo4j
        # """
        # try:
        #     with self.neo4j_driver.session(database="travelbuddy") as session:
        #         result = session.run("""
        #             MATCH (r:Reviewer {nationality: $nationality})-[:WROTE]->(review:Review)-[:ABOUT]->(h:Hotel)
        #             WITH h.name as hotel_name, 
        #                  count(DISTINCT r) as visitor_count,
        #                  avg(review.score) as avg_rating
        #             WHERE visitor_count > 5
        #             RETURN hotel_name, 
        #                    visitor_count,
        #                    avg_rating,
        #                    h.address as address
        #             ORDER BY visitor_count DESC
        #             LIMIT $limit
        #         """, nationality=nationality, limit=limit)
        #         return [dict(record) for record in result]
        # except Exception as e:
        #     self.logger.error(f"Error in analyze_traveler_patterns: {str(e)}")
        #     raise

    # def get_location_insights(self, hotel_name):
        # """
        # Get insights about a location combining MongoDB and Neo4j data
        # """
        # try:
        #     # Get hotel details from MongoDB
        #     hotel = self.db.hotels.find_one({"Hotel_Name": hotel_name})
        #     if not hotel:
        #         raise ValueError(f"No hotel found with name: {hotel_name}")

        #     # Get related insights from Neo4j
        #     with self.neo4j_driver.session(database="travelbuddy") as session:
        #         result = session.run("""
        #             MATCH (h:Hotel {name: $hotel_name})
        #             OPTIONAL MATCH (h)<-[:ABOUT]-(r:Review)<-[:WROTE]-(reviewer:Reviewer)
        #             WITH h, reviewer
        #             OPTIONAL MATCH (reviewer)-[:WROTE]->(other:Review)-[:ABOUT]->(next:Hotel)
        #             WHERE h <> next
        #             WITH next, count(DISTINCT reviewer) as common_visitors
        #             WHERE common_visitors > 2
        #             RETURN next.name as next_destination,
        #                    common_visitors,
        #                    next.address as address
        #             ORDER BY common_visitors DESC
        #             LIMIT 5
        #         """, hotel_name=hotel_name)
        #         next_destinations = [dict(record) for record in result]

        #     return {
        #         "hotel_details": hotel,
        #         "next_destinations": next_destinations,
        #     }
        # except Exception as e:
        #     self.logger.error(f"Error in get_location_insights: {str(e)}")
        #     raise

    # def verify_mongodb_data(self):
        # """Verify data in MongoDB"""
        # try:
        #     # Get a sample hotel from HotelReviews collection
        #     sample_hotel = self.db.HotelReviews.find_one()
        #     if sample_hotel:
        #         print("\nSample hotel structure:")
        #         for key in sample_hotel:
        #             print(f"{key}: {sample_hotel[key]}")

        #     # Count total hotels
        #     total_hotels = self.db.HotelReviews.count_documents({})
        #     print(f"\nTotal number of hotels: {total_hotels}")

        #     # Get some sample hotel names
        #     sample_names = list(self.db.HotelReviews.find({}, {"Hotel_Name": 1}).limit(5))
        #     print("\nSample hotel names:")
        #     for hotel in sample_names:
        #         print(hotel.get('Hotel_Name', 'No name found'))

        # except Exception as e:
        #     self.logger.error(f"Error verifying MongoDB data: {str(e)}")
        #     raise

    # def analyze_hotel_data(self):
        # """Analyze hotel data structure and content"""
        # try:
        #     # Get total count of documents
        #     total_docs = self.db.HotelReviews.count_documents({})
        #     print(f"\nTotal number of reviews: {total_docs}")

        #     # Get one sample document and print its structure
        #     sample = self.db.HotelReviews.find_one()
        #     if sample:
        #         print("\nSample document structure:")
        #         for key in sample:
        #             print(f"{key}: {type(sample[key])} = {sample[key]}")

        #     # Check Tags field specifically
        #     tags_sample = self.db.HotelReviews.find({"Tags": {"$exists": True}}).limit(1).next()
        #     print("\nTags field example:")
        #     print(f"Type: {type(tags_sample['Tags'])}")
        #     print(f"Value: {tags_sample['Tags']}")

        #     # Get some distinct tag values
        #     print("\nSome distinct tag combinations:")
        #     distinct_tags = list(self.db.HotelReviews.distinct("Tags"))[:5]
        #     for tags in distinct_tags:
        #         print(tags)

        # except Exception as e:
        #     self.logger.error(f"Error analyzing data: {str(e)}")
        #     raise

    def search_hotels(self, search_text='', features=None, limit=10):
        """
        Combined search for both text and features
        """
        try:
            # Start building the match conditions
            match_conditions = []
            
            # Add text search conditions if search text is provided
            if search_text:
                text_keywords = search_text.lower().split()
                text_conditions = []
                for keyword in text_keywords:
                    text_conditions.append({
                        "$or": [
                            {"Positive_Review": {"$regex": keyword, "$options": "i"}},
                            {"Negative_Review": {"$regex": keyword, "$options": "i"}},
                            {"Tags": {"$regex": keyword, "$options": "i"}}
                        ]
                    })
                if text_conditions:
                    match_conditions.append({"$and": text_conditions})

            # Add feature search conditions if features are provided
            if features and features[0]:  # Check if features list is not empty and first element is not empty
                feature_conditions = []
                for feature in features:
                    if feature.strip():  # Only add non-empty features
                        feature_conditions.append({
                            "Tags": {"$regex": feature.strip(), "$options": "i"}
                        })
                if feature_conditions:
                    match_conditions.append({"$or": feature_conditions})

            # Build the final match query
            match_query = {"$and": match_conditions} if match_conditions else {}

            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": "$Hotel_Name",
                        "Hotel_Address": {"$first": "$Hotel_Address"},
                        "Average_Score": {"$first": "$Average_Score"},
                        "positive_reviews": {
                            "$push": {
                                "$cond": [
                                    {"$ne": ["$Positive_Review", "No Positive"]},
                                    "$Positive_Review",
                                    None
                                ]
                            }
                        },
                        "negative_reviews": {
                            "$push": {
                                "$cond": [
                                    {"$ne": ["$Negative_Review", "No Negative"]},
                                    "$Negative_Review",
                                    None
                                ]
                            }
                        },
                        "review_count": {"$sum": 1},
                        "avg_reviewer_score": {"$avg": "$Reviewer_Score"},
                        "all_tags": {"$push": "$Tags"}
                    }
                },
                {
                    "$project": {
                        "name": "$_id",
                        "location": "$Hotel_Address",
                        "averageReviewScore": "$Average_Score",
                        "reviewCount": "$review_count",
                        "highlights": {
                            "$filter": {
                                "input": "$positive_reviews",
                                "as": "review",
                                "cond": {"$ne": ["$$review", None]}
                            }
                        },
                        "considerations": {
                            "$filter": {
                                "input": "$negative_reviews",
                                "as": "review",
                                "cond": {"$ne": ["$$review", None]}
                            }
                        },
                        "tags": "$all_tags",
                        "_id": 0
                    }
                },
                {
                    "$project": {
                        "name": 1,
                        "location": 1,
                        "averageReviewScore": 1,
                        "reviewCount": 1,
                        "highlights": {"$slice": ["$highlights", 3]},
                        "considerations": {"$slice": ["$considerations", 3]},
                        "tags": {
                            "$reduce": {
                                "input": "$tags",
                                "initialValue": [],
                                "in": {
                                    "$concatArrays": [
                                        "$$value",
                                        {"$split": ["$$this", ","]}
                                    ]
                                }
                            }
                        }
                    }
                },
                {"$sort": {"averageReviewScore": -1}},
                {"$limit": limit}
            ]

            results = list(self.db.HotelReviews.aggregate(pipeline))

            # Clean up the results
            for hotel in results:
                # Clean up and deduplicate tags
                hotel['tags'] = list(set([
                    tag.strip()
                    for tags in hotel['tags']
                    for tag in (tags.split(',') if tags else [])
                    if tag.strip()
                ]))

            return results

        except Exception as e:
            self.logger.error(f"Error in search_hotels: {str(e)}")
            raise

    def close(self):
        """Close database connections"""
        self.mongo_client.close()
        self.neo4j_driver.close()

# Example usage


# def test_hotel_search():
    # """Test searching hotels by features"""
    # queries = TravelBuddyQueries()
    # try:
    #     # Test with features we know exist
    #     features = ['Leisure trip', 'Couple']
    #     print(f"\nSearching for features: {features}")

    #     hotels = queries.search_hotels_by_features(features, limit=5)
    #     print(f"\nFound {len(hotels)} unique hotels:")

    #     for hotel in hotels:
    #         print(f"\nHotel Name: {hotel['Hotel_Name']}")
    #         print(f"Address: {hotel['Hotel_Address']}")
    #         print(f"Average Score: {hotel['Average_Score']}")
    #         print(f"Number of matching reviews: {hotel['review_count']}")
    #         print(f"Average reviewer score: {hotel['avg_reviewer_score']:.2f}")
    #         print(f"Sample Tags: {hotel['Tags']}")

    # except Exception as e:
    #     print(f"Error in hotel search: {e}")
    # finally:
    #     queries.close()


# def test_mongodb_verification():
    # """Test MongoDB data verification"""
    # queries = TravelBuddyQueries()
    # try:
    #     queries.verify_mongodb_data()
    # except Exception as e:
    #     print(f"Error verifying MongoDB data: {e}")
    # finally:
    #     queries.close()

# def test_data_analysis():
        # """Test data analysis"""
        # queries = TravelBuddyQueries()
        # try:
        #     queries.analyze_hotel_data()
        # except Exception as e:
        #     print(f"Error in data analysis: {e}")
        # finally:
        #     queries.close()



# if __name__ == "__main__":
    # test_mongodb_verification()
    # test_hotel_search()
    # test_data_analysis()
#
# def test_sentiment_analysis():
#     """Test hotel sentiment analysis"""
#     queries = TravelBuddyQueries()
#     try:
#         hotel_name = 'Hotel Arena'
#         sentiment = queries.get_hotel_sentiment_analysis(hotel_name)
#         print(f"\nSentiment Analysis for {hotel_name}:")
#         print(f"Total Reviews: {sentiment['total_reviews']}")
#         print(f"Positive Reviews: {sentiment['positive_reviews']}")
#         print(f"Negative Reviews: {sentiment['negative_reviews']}")
#         print("Review Distribution:")
#         for score in sentiment['review_distribution']:
#             print(f"Score {score['score']}: {score['count']} reviews")
#     except Exception as e:
#         print(f"Error in sentiment analysis: {e}")
#     finally:
#         queries.close()
#
#
# def test_similar_hotels():
#     """Test finding similar hotels"""
#     queries = TravelBuddyQueries()
#     try:
#         hotel_name = 'Hotel Arena'
#         similar = queries.find_similar_hotels_neo4j(hotel_name)
#         print(f"\nSimilar hotels to {hotel_name}:")
#         for hotel in similar:
#             print(f"\nHotel: {hotel['hotel_name']}")
#             print(f"Common Tags: {hotel['common_tags']}")
#             print(f"Average Score: {hotel['avg_score']}")
#     except Exception as e:
#         print(f"Error finding similar hotels: {e}")
#     finally:
#         queries.close()
#
#
# def test_traveler_patterns():
#     """Test analyzing traveler patterns"""
#     queries = TravelBuddyQueries()
#     try:
#         nationality = 'United Kingdom'
#         patterns = queries.analyze_traveler_patterns(nationality)
#         print(f"\nTravel patterns for {nationality} visitors:")
#         for pattern in patterns:
#             print(f"\nHotel: {pattern['hotel_name']}")
#             print(f"Visitor Count: {pattern['visitor_count']}")
#             print(f"Average Rating: {pattern['avg_rating']:.2f}")
#     except Exception as e:
#         print(f"Error analyzing traveler patterns: {e}")
#     finally:
#         queries.close()
#
#
# def test_location_insights():
#     """Test getting location insights"""
#     queries = TravelBuddyQueries()
#     try:
#         hotel_name = 'Hotel Arena'
#         insights = queries.get_location_insights(hotel_name)
#         if insights:
#             print(f"\nLocation insights for {hotel_name}:")
#             print("\nHotel Details:")
#             print(f"Address: {insights['hotel_details']['Hotel_Address']}")
#             print(f"Average Score: {insights['hotel_details']['Average_Score']}")
#             print("\nNext Destinations:")
#             for dest in insights['next_destinations']:
#                 print(f"\nDestination: {dest['next_destination']}")
#                 print(f"Common Visitors: {dest['common_visitors']}")
#         else:
#             print(f"No insights found for {hotel_name}")
#     except Exception as e:
#         print(f"Error getting location insights: {e}")
#     finally:
#         queries.close()
#
#
# def run_all_tests():
#     """Run all test functions"""
#     print("Starting TravelBuddy Database Tests")
#     print("=" * 50)
#
#     test_functions = [
#         test_hotel_search,
#         test_sentiment_analysis,
#         test_similar_hotels,
#         test_traveler_patterns,
#         test_location_insights
#     ]
#
#     for test in test_functions:
#         print(f"\nRunning: {test.__doc__}")
#         print("-" * 30)
#         test()
#
#
# if __name__ == "__main__":
#     # Run all tests
#     run_all_tests()