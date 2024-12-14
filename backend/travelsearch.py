from pymongo import MongoClient
from neo4j import GraphDatabase
import logging
import redis
import json
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
            database = "travelbuddy"
        )
        
        # self.neo4j_driver = GraphDatabase.driver(
        #     "bolt://localhost:7687",
        #     auth=("neo4j", "moderndbproject")
        # )

        # self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    
    
    def search_hotels(self, search_text='', features=None, limit=10):
        """
        Enhanced search for hotels using text and tags with optimized pipelines.
        """
        try:
            # Start building the match conditions
            
            # cache_key = f"search:{search_text}:{','.join(features or [])}:{limit}"
            # cached_result = self.redis_client.get(cache_key)

            # if cached_result:
            #     self.logger.info("Cache hit for search query")
            #     return json.loads(cached_result)  # Return cached result

            # self.logger.info("Cache miss for search query, querying database")

            # Database search logic
            match_conditions = []
            if search_text:
                text_keywords = search_text.lower().split()
                text_conditions = [
                    {
                        "$or": [
                            {"Positive_Review": {"$regex": keyword, "$options": "i"}},
                            {"Negative_Review": {"$regex": keyword, "$options": "i"}},
                            {"Tags": {"$regex": keyword, "$options": "i"}}
                        ]
                    }
                    for keyword in text_keywords
                ]
                if text_conditions:
                    match_conditions.append({"$and": text_conditions})

            if features and any(features):
                feature_conditions = [
                    {"Tags": {"$regex": feature.strip(), "$options": "i"}}
                    for feature in features if feature.strip()
                ]
                if feature_conditions:
                    match_conditions.append({"$or": feature_conditions})

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
                {
                    "$project": {
                        "name": 1,
                        "location": 1,
                        "averageReviewScore": 1,
                        "reviewCount": 1,
                        "highlights": 1,
                        "considerations": 1,
                        "tags": {
                            "$setUnion": ["$tags"]
                        }
                    }
                },
                {"$sort": {"averageReviewScore": -1}},
                {"$limit": limit}
            ]

            results = list(self.db.travelbuddy.aggregate(pipeline))
            # Clean up the results
            for hotel in results:
                # Clean up and deduplicate tags
                hotel['tags'] = list(set([
                    tag.strip()
                    for tags in hotel['tags']
                    for tag in (tags.split(',') if tags else [])
                    if tag.strip()
                ]))

            # self.redis_client.setex(cache_key, 3600, json.dumps(results))  # Cache for 1 hour
            return results


        except Exception as e:
            self.logger.error(f"Error in search_hotels: {str(e)}")
            raise

    def close(self):
        """Close database connections"""
        self.mongo_client.close()
        self.neo4j_driver.close()