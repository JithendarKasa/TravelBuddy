from flask import Blueprint, jsonify, current_app
from app.models.neo4j_models import Neo4jHotelModel

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/api/recommendations/location/<city>', methods=['GET'])
def get_location_recommendations(city):
    try:
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        recommendations = neo4j_model.get_location_based_recommendations(city)
        
        if not recommendations:
            return jsonify({
                "status": "success",
                "recommended_hotels": [],
                "message": f"No hotels found in {city}"
            })
            
        return jsonify({
            "status": "success",
            "recommended_hotels": recommendations
        })
    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/hotel/<hotel_name>', methods=['GET'])
def get_hotel_recommendations(hotel_name):
    try:
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        similar_hotels = neo4j_model.get_similar_hotels(hotel_name)
        
        if not similar_hotels:
            return jsonify({
                "status": "success",
                "similar_hotels": [],
                "message": f"No similar hotels found for {hotel_name}"
            })
            
        return jsonify({
            "status": "success",
            "similar_hotels": similar_hotels
        })
    except Exception as e:
        print(f"Error getting similar hotels: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/hotel/<hotel_name>', methods=['GET'])
def get_hotel_details(hotel_name):
    try:
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        hotel_info = neo4j_model.get_detailed_hotel_info(hotel_name)
        
        if not hotel_info:
            return jsonify({
                "status": "success",
                "hotel": None,
                "message": f"Hotel {hotel_name} not found"
            })
            
        return jsonify({
            "status": "success",
            "hotel": hotel_info
        })
    except Exception as e:
        print(f"Error getting hotel details: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500