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
                            {"Positive_Review": {"$regex": f"\\b{keyword}\\b", "$options": "i"}},
                            {"Negative_Review": {"$regex": f"\\b{keyword}\\b", "$options": "i"}},
                            # For location/city searches, check the Hotel_Address field
                            {"Hotel_Address": {"$regex": f"\\b{keyword}\\b", "$options": "i"}},
                            {"Hotel_Name": {"$regex": f"\\b{keyword}\\b", "$options": "i"}},
                            {"Tags": {"$regex": f"\\b{keyword}\\b", "$options": "i"}}
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