from flask import Blueprint, jsonify, request, current_app
from app.models.neo4j_models import HotelRecommendationModel

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/api/recommendations/location/<city>', methods=['GET'])
def get_location_recommendations(city):
    try:
        print(f"Searching for hotels in: {city}")
        neo4j_model = HotelRecommendationModel(
            uri="neo4j://localhost:7687",
            user="neo4j",
            password="your_password"  # Replace with your password
        )
        
        recommendations = neo4j_model.get_recommendations_by_preferences(
            trip_type=None,
            city=city
        )
        
        return jsonify({
            "status": "success",
            "recommended_hotels": recommendations
        })
    except Exception as e:
        print(f"Error in location recommendations: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/tags/<tag>', methods=['GET'])
def get_tag_recommendations(tag):
    try:
        print(f"Searching for tag: {tag}")
        neo4j_model = HotelRecommendationModel(
            uri="neo4j://localhost:7687",
            user="neo4j",
            password="your_password"  # Replace with your password
        )
        
        recommendations = neo4j_model.get_recommendations_by_preferences(
            trip_type=tag
        )
        
        return jsonify({
            "status": "success",
            "recommended_hotels": recommendations
        })
    except Exception as e:
        print(f"Error in tag recommendations: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/personalized', methods=['GET'])
def get_personalized_recommendations():
    try:
        trip_type = request.args.get('trip_type')
        print(f"Getting personalized recommendations for: {trip_type}")
        
        neo4j_model = HotelRecommendationModel(
            uri="neo4j://localhost:7687",
            user="neo4j",
            password="your_password"  # Replace with your password
        )
        
        recommendations = neo4j_model.get_recommendations_by_preferences(
            trip_type=trip_type,
            min_rating=7.0
        )
        
        return jsonify({
            "status": "success",
            "recommended_hotels": recommendations
        })
    except Exception as e:
        print(f"Error in personalized recommendations: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500