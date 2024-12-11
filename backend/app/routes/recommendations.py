from flask import Blueprint, jsonify, request, current_app
from app.models.neo4j_models import Neo4jHotelModel
from app.services.recommendation_service import RecommendationService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/api/test/connection', methods=['GET'])
def test_connection():
    """Test Neo4j database connection"""
    try:
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        result = neo4j_model.test_connection()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Connection test failed: {str(e)}"
        }), 500

@recommendations_bp.route('/api/recommendations/location/<city>', methods=['GET'])
def get_location_recommendations(city):
    """Get hotel recommendations for a specific city"""
    try:
        logger.info(f"Received location request for: {city}")
        limit = request.args.get('limit', default=10, type=int)
        
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        recommendation_service = RecommendationService(neo4j_model)
        
        result = recommendation_service.get_location_recommendations(city, limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting recommendations for {city}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/travel-type/<travel_type>', methods=['GET'])
def get_travel_type_recommendations(travel_type):
    """Get recommendations based on travel type"""
    try:
        logger.info(f"Received travel type request for: {travel_type}")
        limit = request.args.get('limit', default=10, type=int)
        
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        recommendation_service = RecommendationService(neo4j_model)
        
        result = recommendation_service.get_travel_type_recommendations(travel_type, limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting recommendations for travel type {travel_type}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/similar/<hotel_name>', methods=['GET'])
def get_similar_hotels(hotel_name):
    """Get similar hotels based on reviewer patterns"""
    try:
        logger.info(f"Received similar hotels request for: {hotel_name}")
        limit = request.args.get('limit', default=5, type=int)
        
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        recommendation_service = RecommendationService(neo4j_model)
        
        result = recommendation_service.get_similar_hotels(hotel_name, limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting similar hotels for {hotel_name}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/personalized', methods=['POST'])
def get_personalized_recommendations():
    """Get personalized recommendations based on preferences"""
    try:
        logger.info("Received personalized recommendations request")
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No preferences provided"
            }), 400
        
        limit = data.get('limit', 10)
        preferences = {
            'travel_type': data.get('travel_type', 'Leisure trip'),
            'min_rating': data.get('min_rating', 7.0),
            'required_tags': data.get('required_tags', []),
            'nationality': data.get('nationality')
        }
        
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        recommendation_service = RecommendationService(neo4j_model)
        
        result = recommendation_service.get_personalized_recommendations(preferences, limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/debug/sample', methods=['GET'])
def get_sample_data():
    """Get sample data for debugging"""
    try:
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        with current_app.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (r:Review)
                RETURN properties(r) as review_data
                LIMIT 1
            """)
            sample = result.single()
            
            if sample:
                return jsonify({
                    "status": "success",
                    "sample_data": dict(sample['review_data'])
                })
            return jsonify({
                "status": "error",
                "message": "No data found"
            })
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500