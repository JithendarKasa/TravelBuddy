from flask import Blueprint, jsonify, current_app
from app.models.neo4j_models import Neo4jHotelModel

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/api/recommendations/location/<city>', methods=['GET'])
def get_location_recommendations(city):
    try:
        print(f"Received location request for: {city}")
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        recommendations = neo4j_model.get_location_based_recommendations(city)
        
        print(f"Found {len(recommendations)} hotels for {city}")
        return jsonify({
            "status": "success",
            "recommended_hotels": recommendations
        })
    except Exception as e:
        print(f"Error getting recommendations for {city}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@recommendations_bp.route('/api/recommendations/tags/<tag>', methods=['GET'])
def get_tag_recommendations(tag):
    try:
        print(f"Received tag request for: {tag}")
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        recommendations = neo4j_model.search_by_tags(tag)
        
        print(f"Found {len(recommendations)} hotels with tag {tag}")
        if not recommendations:
            return jsonify({
                "status": "success",
                "recommended_hotels": [],
                "message": f"No hotels found with tag: {tag}"
            })
        
        return jsonify({
            "status": "success",
            "recommended_hotels": recommendations
        })
    except Exception as e:
        print(f"Error getting tag recommendations for {tag}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Add a debug endpoint to check data structure
@recommendations_bp.route('/api/debug/sample', methods=['GET'])
def get_sample_data():
    try:
        neo4j_model = Neo4jHotelModel(current_app.neo4j_driver)
        with current_app.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (r:Review)
                RETURN r LIMIT 1
            """)
            sample = result.single()
            if sample:
                return jsonify({
                    "status": "success",
                    "sample_data": dict(sample['r'])
                })
            return jsonify({
                "status": "error",
                "message": "No data found"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500